#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, Float32
from frs_interfaces.msg import DetectieResultaat

import cv2
import depthai as dai
import numpy as np
import os
import threading
import time
import collections
from datetime import timedelta

# =============================================================================
# CONFIGURATIE
# =============================================================================

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'best.pt')
LABELS = ['Maan', 'Octagon', 'Balk', 'Kubus']

# Vaste z per klasse: (liggend_mm, staand_mm)
# Balk/Maan: staand = hoogte_bbox > breedte_bbox * STAAND_RATIO
# Octagon:   staand = bbox NIET duidelijk breder dan hoog (omgekeerde logica)
#            want staande Octagon is rond (vierkante bbox), liggend is breed
Z_PER_KLASSE = {
    'Maan':    (10.0, 11.0),
    'Octagon': (10.0, 15.0),
    'Balk':    (10.0, 30.0),
    'Kubus':   (10.0, 10.0),
}
STAAND_RATIO  = 1.3   # hoogte/breedte drempel voor staand (Balk, Maan)
LIGGEND_RATIO = 1.3   # breedte/hoogte drempel voor liggend Octagon

# Centroide smoothing
CENTROID_SMOOTH_FRAMES = 5

# ArUco
ARUCO_DICT         = cv2.aruco.DICT_4X4_50
ARUCO_MARKER_ID    = 0
ARUCO_MARKER_SIZE_M = 0.048  # 48mm
CALIBRATION_FRAMES = 20

# YOLO
YOLO_CONF_THRESHOLD = 0.3
YOLO_IOU_THRESHOLD  = 0.4
YOLO_INPUT_SIZE     = (640, 640)

# Camera resoluties
RGB_WIDTH      = 1920
RGB_HEIGHT     = 1080
PUBLISH_WIDTH  = 960
PUBLISH_HEIGHT = 540

# Werkgebied (crop rondom marker)
WORKSPACE_SIZE_MM = 700.0

# Detectie persistentie (frames)
PERSIST_FRAMES    = 5
LABEL_HISTORY     = 10

# =============================================================================


class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')

        # --- Publishers ---
        self.pub_camera   = self.create_publisher(Image,            'camera_beelden',     10)
        self.pub_detectie = self.create_publisher(DetectieResultaat, 'detectie_resultaten', 10)
        self.pub_afgesloten = self.create_publisher(Bool,           'afgesloten',         10)

        # --- Subscribers ---
        self.create_subscription(Bool,    'afsluiten',        self._cb_afsluiten,   10)
        self.create_subscription(Float32, 'confidence_drempel', self._cb_confidence, 10)

        # --- Intern ---
        self._afsluiten      = False
        self._conf_threshold = YOLO_CONF_THRESHOLD

        # ArUco
        aruco_dict           = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        aruco_params         = cv2.aruco.DetectorParameters()
        self.aruco_detector  = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        half                 = ARUCO_MARKER_SIZE_M / 2.0
        self.marker_obj_pts  = np.array([
            [-half,  half, 0], [ half,  half, 0],
            [ half, -half, 0], [-half, -half, 0]
        ], dtype=np.float64)

        self.camera_matrix   = None
        self.marker_rvec     = None
        self.marker_tvec     = None
        self.marker_center_px = None
        self.marker_size_px  = None
        self.marker_locked   = False

        self._cal_tvec   = collections.deque(maxlen=CALIBRATION_FRAMES)
        self._cal_rvec   = collections.deque(maxlen=CALIBRATION_FRAMES)
        self._cal_center = collections.deque(maxlen=CALIBRATION_FRAMES)
        self._cal_size   = collections.deque(maxlen=CALIBRATION_FRAMES)

        # Detectie state
        self._label_history    = collections.defaultdict(
            lambda: collections.deque(maxlen=LABEL_HISTORY))
        self._centroid_history = collections.defaultdict(
            lambda: collections.deque(maxlen=CENTROID_SMOOTH_FRAMES))
        self._persistent_detections = {}

        # YOLO model
        self.model = None
        if os.path.exists(MODEL_PATH):
            from ultralytics import YOLO
            self.model = YOLO(MODEL_PATH)
            self.get_logger().info(f'Model geladen: {MODEL_PATH}')
        else:
            self.get_logger().warn('Geen model gevonden — alleen camera_beelden wordt gepubliceerd.')

        threading.Thread(target=self._run_pipeline, daemon=True).start()
        self.get_logger().info('vision_node gestart.')

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _cb_afsluiten(self, msg):
        if msg.data:
            self.get_logger().info('Afsluitverzoek ontvangen.')
            self._afsluiten = True

    def _cb_confidence(self, msg):
        v = float(msg.data)
        if 0.0 < v <= 1.0:
            self._conf_threshold = v
            self.get_logger().info(f'Confidence drempel: {v:.2f}')
        else:
            self.get_logger().warn(f'Ongeldige confidence drempel: {v}')

    # ------------------------------------------------------------------
    # Beeldverbetering
    # ------------------------------------------------------------------
    def _enhance(self, frame):
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
        frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(frame, -1, kernel)

    # ------------------------------------------------------------------
    # ArUco kalibratie (eenmalig)
    # ------------------------------------------------------------------
    def _detect_aruco(self, frame):
        if self.camera_matrix is None:
            return

        if self.marker_locked:
            cv2.putText(frame, 'Marker vergrendeld',
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.aruco_detector.detectMarkers(gray)

        n = len(self._cal_tvec)
        if ids is None:
            cv2.putText(frame, f'Marker zoeken... ({n}/{CALIBRATION_FRAMES})',
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            return

        for i, marker_id in enumerate(ids.flatten()):
            if marker_id != ARUCO_MARKER_ID:
                continue
            img_pts = corners[i][0].astype(np.float64)
            ok, rvec, tvec = cv2.solvePnP(
                self.marker_obj_pts, img_pts, self.camera_matrix, np.zeros((5, 1)))
            if not ok:
                continue

            self._cal_tvec.append(tvec.flatten())
            self._cal_rvec.append(rvec.flatten())
            self._cal_center.append(img_pts.mean(axis=0))
            self._cal_size.append(np.linalg.norm(img_pts[0] - img_pts[1]))

            n = len(self._cal_tvec)
            cv2.aruco.drawDetectedMarkers(frame, [corners[i]], np.array([[marker_id]]))
            cv2.putText(frame, f'Kalibreren... {n}/{CALIBRATION_FRAMES}',
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

            if n >= CALIBRATION_FRAMES:
                self.marker_tvec      = np.median(self._cal_tvec, axis=0).reshape(3, 1)
                self.marker_rvec      = np.median(self._cal_rvec, axis=0).reshape(3, 1)
                self.marker_center_px = np.median(self._cal_center, axis=0)
                self.marker_size_px   = float(np.median(self._cal_size))
                self.marker_locked    = True
                self.get_logger().info(
                    f'Marker vergrendeld. tvec={self.marker_tvec.flatten().round(4)}')

    # ------------------------------------------------------------------
    # Pixel → wereld (ArUco coördinaten, mm)
    # ------------------------------------------------------------------
    def _pixel_to_world_mm(self, x_px, y_px):
        """
        Converteert een pixelcoordinaat naar mm in het ArUco-frame.
        Gebruikt de homografie gebaseerd op de bekende marker grootte.
        """
        if self.marker_center_px is None or self.marker_size_px is None:
            return None, None

        # px_per_mm schalingsfactor
        px_per_mm = self.marker_size_px / (ARUCO_MARKER_SIZE_M * 1000.0)

        dx_px = x_px - self.marker_center_px[0]
        dy_px = y_px - self.marker_center_px[1]

        # Negatief zodat x rechts en y omhoog positief zijn (robotframe conventie)
        x_mm = (dx_px / px_per_mm)
        y_mm = -(dy_px / px_per_mm)

        return x_mm, y_mm

    # ------------------------------------------------------------------
    # Z bepalen op basis van klasse + bounding box aspect ratio
    # ------------------------------------------------------------------
    @staticmethod
    def _bepaal_z(label, x1, y1, x2, y2):
        bbox_w = max(x2 - x1, 1)
        bbox_h = max(y2 - y1, 1)
        z_liggend, z_staand = Z_PER_KLASSE.get(label, (10.0, 10.0))

        if label == 'Octagon':
            # Staande Octagon is rond → bbox ~vierkant
            # Liggende Octagon is breed → breedte > hoogte * ratio
            liggend = (bbox_w / bbox_h) > LIGGEND_RATIO
            return z_liggend if liggend else z_staand
        else:
            # Balk/Maan: staand = hoogte > breedte
            staand = (bbox_h / bbox_w) > STAAND_RATIO
            return z_staand if staand else z_liggend

    # ------------------------------------------------------------------
    # Rotatie van object
    # ------------------------------------------------------------------
    @staticmethod
    def _get_rotation(frame, x1, y1, x2, y2, margin=4):
        h, w = frame.shape[:2]
        roi = frame[max(0, y1-margin):min(h, y2+margin),
                    max(0, x1-margin):min(w, x2+margin)]
        if roi.size == 0:
            return 0.0
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.0
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) < 20:
            return 0.0
        _, _, angle = cv2.minAreaRect(largest)
        if angle < -45:
            angle += 90.0
        return round(angle, 1)

    # ------------------------------------------------------------------
    # Centroide
    # ------------------------------------------------------------------
    @staticmethod
    def _get_centroid(frame, x1, y1, x2, y2, margin=4):
        h, w = frame.shape[:2]
        cx0 = max(0, x1-margin); cy0 = max(0, y1-margin)
        cx1 = min(w, x2+margin); cy1 = min(h, y2+margin)
        roi = frame[cy0:cy1, cx0:cx1]
        bbox_cx = (x1 + x2) // 2
        bbox_cy = (y1 + y2) // 2
        if roi.size == 0:
            return bbox_cx, bbox_cy
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return bbox_cx, bbox_cy
        largest = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest)
        if M['m00'] == 0:
            return bbox_cx, bbox_cy
        return int(cx0 + M['m10']/M['m00']), int(cy0 + M['m01']/M['m00'])

    # ------------------------------------------------------------------
    # Crop werkgebied
    # ------------------------------------------------------------------
    def _get_crop(self, w, h):
        if self.marker_center_px is None or not self.marker_size_px:
            return 0, 0, w, h
        px_per_mm   = self.marker_size_px / (ARUCO_MARKER_SIZE_M * 1000.0)
        half_px     = (WORKSPACE_SIZE_MM / 2.0) * px_per_mm
        cx, cy      = self.marker_center_px
        x0 = int(max(0, cx - half_px));  y0 = int(max(0, cy - half_px))
        x1 = int(min(w, cx + half_px));  y1 = int(min(h, cy + half_px))
        if (x1-x0) < 50 or (y1-y0) < 50:
            return 0, 0, w, h
        return x0, y0, x1, y1

    # ------------------------------------------------------------------
    # YOLO inferentie
    # ------------------------------------------------------------------
    def _run_yolo(self, frame):
        h, w = frame.shape[:2]
        x0, y0, x1, y1 = self._get_crop(w, h)
        cropped = frame[y0:y1, x0:x1]
        cw, ch  = cropped.shape[1], cropped.shape[0]
        if cw == 0 or ch == 0:
            return None, (0, 0, 1.0, 1.0)
        resized  = cv2.resize(cropped, YOLO_INPUT_SIZE)
        scale_x  = cw / YOLO_INPUT_SIZE[0]
        scale_y  = ch / YOLO_INPUT_SIZE[1]
        results  = self.model.predict(resized, conf=self._conf_threshold,
                                      iou=YOLO_IOU_THRESHOLD, verbose=False)
        return results, (x0, y0, scale_x, scale_y)

    @staticmethod
    def _crop_to_frame(cx1, cy1, cx2, cy2, crop_info):
        x0, y0, sx, sy = crop_info
        return (int(x0 + cx1*sx), int(y0 + cy1*sy),
                int(x0 + cx2*sx), int(y0 + cy2*sy))

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------
    def _run_pipeline(self):
        with dai.Pipeline() as pipeline:
            device = pipeline.getDefaultDevice()
            calib  = device.readCalibration()
            self.camera_matrix = np.array(
                calib.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A, RGB_WIDTH, RGB_HEIGHT),
                dtype=np.float64)
            self.get_logger().info(
                f'Intrinsics: fx={self.camera_matrix[0,0]:.1f} fy={self.camera_matrix[1,1]:.1f}')

            cam = pipeline.create(dai.node.Camera).build()
            cam.initialControl.setManualFocus(130)
            queue_rgb = cam.requestOutput(
                (RGB_WIDTH, RGB_HEIGHT), dai.ImgFrame.Type.BGR888p
            ).createOutputQueue()

            pipeline.start()
            self.get_logger().info('DepthAI pipeline gestart (RGB only).')

            timeout = timedelta(seconds=2)

            while pipeline.isRunning() and rclpy.ok():

                if self._afsluiten:
                    self.get_logger().info('Vision node afgesloten.')
                    msg = Bool(); msg.data = True
                    self.pub_afgesloten.publish(msg)
                    break

                rgb_data = queue_rgb.get(timeout)
                if rgb_data is None:
                    self.get_logger().warn('Geen RGB-frame binnen timeout.')
                    continue

                frame = self._enhance(rgb_data.getCvFrame())
                self._detect_aruco(frame)

                # Verhoog persist teller, verwijder oude detections
                for key in list(self._persistent_detections):
                    self._persistent_detections[key]['frames_since_seen'] += 1
                    if self._persistent_detections[key]['frames_since_seen'] > PERSIST_FRAMES:
                        del self._persistent_detections[key]

                h, w = frame.shape[:2]
                crop_x0, crop_y0, crop_x1, crop_y1 = self._get_crop(w, h)

                if self.model is not None and self.marker_locked:
                    results, crop_info = self._run_yolo(frame)
                    ci_x0, ci_y0, sx, sy = crop_info
                    lim_x1 = int(ci_x0 + YOLO_INPUT_SIZE[0] * sx)
                    lim_y1 = int(ci_y0 + YOLO_INPUT_SIZE[1] * sy)

                    if results is not None:
                        for result in results:
                            for box in result.boxes:
                                cls_int    = int(box.cls[0])
                                label      = LABELS[cls_int] if cls_int < len(LABELS) else 'onbekend'
                                confidence = float(box.conf[0])

                                cx1, cy1, cx2, cy2 = map(int, box.xyxy[0].tolist())
                                x1, y1, x2, y2 = self._crop_to_frame(
                                    cx1, cy1, cx2, cy2, crop_info)

                                bbox_cx = (x1 + x2) // 2
                                bbox_cy = (y1 + y2) // 2

                                # Buiten crop? negeren
                                if not (ci_x0 <= bbox_cx <= lim_x1 and
                                        ci_y0 <= bbox_cy <= lim_y1):
                                    continue

                                # Centroide, rotatie, z
                                x_px_raw, y_px_raw = self._get_centroid(frame, x1, y1, x2, y2)
                                rot_deg    = self._get_rotation(frame, x1, y1, x2, y2)
                                z_mm       = self._bepaal_z(label, x1, y1, x2, y2)

                                # Stabiel label via history
                                pos_key = (x_px_raw // 80, y_px_raw // 80)
                                self._label_history[pos_key].append(label)
                                stable_label = max(
                                    set(self._label_history[pos_key]),
                                    key=list(self._label_history[pos_key]).count)

                                # Centroide smoothing
                                self._centroid_history[pos_key].append((x_px_raw, y_px_raw))
                                xs = [p[0] for p in self._centroid_history[pos_key]]
                                ys = [p[1] for p in self._centroid_history[pos_key]]
                                x_px = int(np.median(xs))
                                y_px = int(np.median(ys))

                                # Pixel → mm
                                x_mm, y_mm = self._pixel_to_world_mm(x_px, y_px)
                                if x_mm is None:
                                    continue

                                self._persistent_detections[pos_key] = {
                                    'label':            stable_label,
                                    'confidence':       confidence,
                                    'x_px': x_px, 'y_px': y_px,
                                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                                    'x_mm': x_mm, 'y_mm': y_mm, 'z_mm': z_mm,
                                    'rotatie_deg':      rot_deg,
                                    'frames_since_seen': 0,
                                }

                    # Crop rechthoek tekenen
                    cv2.rectangle(frame, (crop_x0, crop_y0), (crop_x1, crop_y1),
                                  (255, 0, 0), 2)

                    # Publiceer + teken alle persistente detections
                    for det in self._persistent_detections.values():
                        msg = DetectieResultaat()
                        msg.klasse     = det['label']
                        msg.confidence = float(round(det['confidence'], 3))
                        msg.x          = float(round(det['x_mm'], 1))
                        msg.y          = float(round(det['y_mm'], 1))
                        msg.z          = float(round(det['z_mm'], 1))
                        msg.rotatie    = float(det['rotatie_deg'])
                        self.pub_detectie.publish(msg)

                        self.get_logger().info(
                            f"{det['label']} | conf={det['confidence']:.2f} | "
                            f"x={det['x_mm']:.0f}mm y={det['y_mm']:.0f}mm "
                            f"z={det['z_mm']:.0f}mm | rot={det['rotatie_deg']}deg")

                        x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
                        kleur = (0, 255, 0) if det['frames_since_seen'] == 0 else (0, 200, 200)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), kleur, 3)
                        cv2.circle(frame, (det['x_px'], det['y_px']), 6, (0, 0, 255), -1)
                        cv2.putText(frame, f"{det['label']} {det['confidence']:.0%}",
                                    (x1, y1-12), cv2.FONT_HERSHEY_SIMPLEX, 1.0, kleur, 3)
                        cv2.putText(frame,
                                    f"x:{det['x_mm']:.0f} y:{det['y_mm']:.0f} z:{det['z_mm']:.0f}mm",
                                    (x1, y2+28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        cv2.putText(frame, f"rot:{det['rotatie_deg']}deg",
                                    (x1, y2+56), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

                elif self.model is not None and not self.marker_locked:
                    cv2.putText(frame, 'Wacht op marker kalibratie...',
                                (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

                # Publiceer camerabeeld
                pub_frame = cv2.resize(frame, (PUBLISH_WIDTH, PUBLISH_HEIGHT))
                msg_img          = Image()
                msg_img.header.stamp = self.get_clock().now().to_msg()
                msg_img.height   = pub_frame.shape[0]
                msg_img.width    = pub_frame.shape[1]
                msg_img.encoding = 'bgr8'
                msg_img.step     = pub_frame.shape[1] * 3
                msg_img.data     = pub_frame.tobytes()
                self.pub_camera.publish(msg_img)

                cv2.imshow('vision_node', pub_frame)
                cv2.waitKey(1)
                time.sleep(0.8)

        cv2.destroyAllWindows()


def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
