#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

import cv2
import depthai as dai
import numpy as np
import os
import json
import threading
import time
import collections
from datetime import timedelta

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'frs_model.pt')
LABELS = ['Maan', 'Octagon', 'Rechthoek', 'Vierkant']

# --- ArUco instellingen ---
ARUCO_DICT = cv2.aruco.DICT_4X4_50
ARUCO_MARKER_ID = 0
ARUCO_MARKER_SIZE_M = 0.048  # 48mm

# --- YOLO instellingen ---
YOLO_CONF_THRESHOLD = 0.5
YOLO_IOU_THRESHOLD = 0.45

# --- Resoluties ---
RGB_WIDTH = 1280
RGB_HEIGHT = 720
DEPTH_WIDTH = 640
DEPTH_HEIGHT = 368
PUBLISH_WIDTH = 640
PUBLISH_HEIGHT = 480
FRAME_WIDTH = DEPTH_WIDTH
FRAME_HEIGHT = DEPTH_HEIGHT

# --- Digitale zoom ---
WORKSPACE_SIZE_MM = 900.0
YOLO_INPUT_SIZE = (640, 640)

# --- Plausibiliteitsgrenzen ---
MAX_PLAUSIBLE_HEIGHT_MM = 60.0
MIN_PLAUSIBLE_HEIGHT_MM = -15.0
MAX_PLAUSIBLE_DISTANCE_MM = WORKSPACE_SIZE_MM * 0.75

DIST_COEFFS = np.zeros((5, 1), dtype=np.float64)

# Kalibratie-offset: stereo depth meet systematisch te ver op deze
# cameraafstand. Gemeten: Vierkant (10mm hoog) geeft ~13-18mm -> offset ~6mm.
# Pas aan als de opstelling verandert (andere hoogte camera/tafel).
HOOGTE_OFFSET_MM = 6.0

# --- Temporele filtering ---
# Depth-history per POSITIE-bucket (x//50, y//50) zodat objecten die
# wisselen van label toch een consistente depth-history houden, en twee
# aparte objecten naast elkaar niet elkaars history mengen.
DEPTH_HISTORY_SIZE = 5
POSITION_BUCKET_PX = 50  # pixels per bucket


class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')

        self.pub_camera = self.create_publisher(Image, 'camera_beelden', 10)
        self.pub_detectie = self.create_publisher(String, 'detectie_resultaten', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

        half_size = ARUCO_MARKER_SIZE_M / 2.0
        self.marker_obj_points = np.array([
            [-half_size,  half_size, 0],
            [ half_size,  half_size, 0],
            [ half_size, -half_size, 0],
            [-half_size, -half_size, 0]
        ], dtype=np.float64)

        self.marker_rvec = None
        self.marker_tvec = None
        self.marker_center_px = None
        self.marker_size_px = None
        self.camera_matrix = None

        # Depth-history per positie-bucket
        self._depth_history = collections.defaultdict(
            lambda: collections.deque(maxlen=DEPTH_HISTORY_SIZE)
        )

        self.model = None
        if os.path.exists(MODEL_PATH):
            from ultralytics import YOLO
            self.model = YOLO(MODEL_PATH)
            self.get_logger().info(f'Model gevonden: {MODEL_PATH}')
        else:
            self.get_logger().warn('Geen model gevonden — alleen camera_beelden wordt gepubliceerd.')

        self.pipeline_thread = threading.Thread(target=self._run_pipeline, daemon=True)
        self.pipeline_thread.start()
        self.get_logger().info('vision_node gestart.')

    def _detect_aruco(self, frame):
        if self.camera_matrix is None:
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.aruco_detector.detectMarkers(gray)
        if ids is None:
            return
        for i, marker_id in enumerate(ids.flatten()):
            if marker_id != ARUCO_MARKER_ID:
                continue
            img_points = corners[i][0].astype(np.float64)
            success, rvec, tvec = cv2.solvePnP(
                self.marker_obj_points, img_points,
                self.camera_matrix, DIST_COEFFS
            )
            if not success:
                continue
            self.marker_rvec = rvec
            self.marker_tvec = tvec
            self.marker_center_px = img_points.mean(axis=0)
            self.marker_size_px = np.linalg.norm(img_points[0] - img_points[1])
            self._broadcast_transform('camera_frame', 'aruco_marker', rvec, tvec)
            cv2.aruco.drawDetectedMarkers(frame, [corners[i]], np.array([[marker_id]]))
            cv2.drawFrameAxes(frame, self.camera_matrix, DIST_COEFFS, rvec, tvec, ARUCO_MARKER_SIZE_M * 0.5)

    def _broadcast_transform(self, parent_frame, child_frame, rvec, tvec):
        rot_matrix, _ = cv2.Rodrigues(rvec)
        quat = self._rotation_matrix_to_quaternion(rot_matrix)
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = parent_frame
        t.child_frame_id = child_frame
        t.transform.translation.x = float(tvec[0])
        t.transform.translation.y = float(tvec[1])
        t.transform.translation.z = float(tvec[2])
        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]
        self.tf_broadcaster.sendTransform(t)

    @staticmethod
    def _rotation_matrix_to_quaternion(R):
        trace = R[0, 0] + R[1, 1] + R[2, 2]
        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (R[2, 1] - R[1, 2]) * s
            y = (R[0, 2] - R[2, 0]) * s
            z = (R[1, 0] - R[0, 1]) * s
        elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
            s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
            w = (R[2, 1] - R[1, 2]) / s
            x = 0.25 * s
            y = (R[0, 1] + R[1, 0]) / s
            z = (R[0, 2] + R[2, 0]) / s
        elif R[1, 1] > R[2, 2]:
            s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
            w = (R[0, 2] - R[2, 0]) / s
            x = (R[0, 1] + R[1, 0]) / s
            y = 0.25 * s
            z = (R[1, 2] + R[2, 1]) / s
        else:
            s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
            w = (R[1, 0] - R[0, 1]) / s
            x = (R[0, 2] + R[2, 0]) / s
            y = (R[1, 2] + R[2, 1]) / s
            z = 0.25 * s
        return [x, y, z, w]

    def _deproject_pixel_to_camera_point(self, x_px, y_px, depth_mm):
        fx = self.camera_matrix[0, 0]
        fy = self.camera_matrix[1, 1]
        cx = self.camera_matrix[0, 2]
        cy = self.camera_matrix[1, 2]
        z_m = depth_mm / 1000.0
        x_m = (x_px - cx) * z_m / fx
        y_m = (y_px - cy) * z_m / fy
        return np.array([x_m, y_m, z_m], dtype=np.float64)

    def _publish_object_transform(self, object_label, x_px, y_px, depth_mm, index):
        if self.marker_tvec is None or self.marker_rvec is None:
            return 0.0, False, 0.0, 0.0
        if self.camera_matrix is None:
            return 0.0, False, 0.0, 0.0
        if depth_mm is None or depth_mm <= 0:
            return 0.0, False, 0.0, 0.0

        point_camera = self._deproject_pixel_to_camera_point(x_px, y_px, depth_mm)
        rot_matrix, _ = cv2.Rodrigues(self.marker_rvec)
        t_marker = self.marker_tvec.reshape(3)
        point_marker = rot_matrix.T @ (point_camera - t_marker)
        point_marker[2] = -point_marker[2]

        object_height_mm = max(0.0, float(point_marker[2]) * 1000.0 - HOOGTE_OFFSET_MM)
        xy_distance_mm = float(np.hypot(point_marker[0], point_marker[1])) * 1000.0

        if not (MIN_PLAUSIBLE_HEIGHT_MM <= object_height_mm <= MAX_PLAUSIBLE_HEIGHT_MM):
            self.get_logger().warn(
                f'Detectie "{object_label}" genegeerd: implausibele hoogte '
                f'{object_height_mm:.1f}mm.'
            )
            return None, True, 0.0, 0.0

        if xy_distance_mm > MAX_PLAUSIBLE_DISTANCE_MM:
            self.get_logger().warn(
                f'Detectie "{object_label}" genegeerd: {xy_distance_mm:.0f}mm van marker.'
            )
            return None, True, 0.0, 0.0

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'aruco_marker'
        t.child_frame_id = f'object_{index}'
        t.transform.translation.x = float(point_marker[0])
        t.transform.translation.y = float(point_marker[1])
        t.transform.translation.z = float(point_marker[2])
        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

        x_mm = float(point_marker[0]) * 1000.0
        y_mm = float(point_marker[1]) * 1000.0
        return object_height_mm, False, x_mm, y_mm

    @staticmethod
    def _get_rotation_angle(frame, x1, y1, x2, y2, margin=4):
        """Berekent de rotatiehoek van het object binnen de bounding box via
        cv2.minAreaRect op de grootste contour. Geeft een hoek in graden
        t.o.v. de horizontale as terug (-90 tot 0 graden, OpenCV conventie).
        Genormaliseerd naar -90..90 zodat de robot altijd de kortste draai maakt.
        Retourneert 0.0 bij falen (geen contour gevonden)."""
        h, w = frame.shape[:2]
        cx0 = max(0, x1 - margin)
        cy0 = max(0, y1 - margin)
        cx1 = min(w, x2 + margin)
        cy1 = min(h, y2 + margin)

        roi = frame[cy0:cy1, cx0:cx1]
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

        # OpenCV geeft hoeken in [-90, 0). Normaliseer naar [-45, 45] zodat
        # een vierkant dat 91° gedraaid is als -1° wordt gezien (symmetrie).
        if angle < -45:
            angle += 90.0

        return round(angle, 1)

    @staticmethod
    def _find_centroid_in_bbox(frame, x1, y1, x2, y2, margin=4):
        h, w = frame.shape[:2]
        bbox_cx = (x1 + x2) // 2
        bbox_cy = (y1 + y2) // 2
        cx0 = max(0, x1 - margin)
        cy0 = max(0, y1 - margin)
        cx1 = min(w, x2 + margin)
        cy1 = min(h, y2 + margin)
        roi = frame[cy0:cy1, cx0:cx1]
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
        cx_roi = M['m10'] / M['m00']
        cy_roi = M['m01'] / M['m00']
        return int(cx0 + cx_roi), int(cy0 + cy_roi)

    def _get_crop_region(self, frame_w, frame_h):
        if self.marker_center_px is None or self.marker_size_px is None or self.marker_size_px <= 0:
            return 0, 0, frame_w, frame_h
        marker_size_mm = ARUCO_MARKER_SIZE_M * 1000.0
        px_per_mm = self.marker_size_px / marker_size_mm
        half_region_px = (WORKSPACE_SIZE_MM / 2.0) * px_per_mm
        cx, cy = self.marker_center_px
        if not getattr(self, '_crop_logged', False):
            self.get_logger().info(
                f'Crop: marker={self.marker_size_px:.1f}px | px_per_mm={px_per_mm:.3f} | '
                f'werkgebied={WORKSPACE_SIZE_MM:.0f}mm -> {2*half_region_px:.0f}px breed'
            )
            self._crop_logged = True
        x0 = int(max(0, cx - half_region_px))
        y0 = int(max(0, cy - half_region_px))
        x1 = int(min(frame_w, cx + half_region_px))
        y1 = int(min(frame_h, cy + half_region_px))
        if (x1 - x0) < 50 or (y1 - y0) < 50:
            return 0, 0, frame_w, frame_h
        return x0, y0, x1, y1

    def _run_yolo_on_crop(self, frame):
        h, w = frame.shape[:2]
        x0, y0, x1, y1 = self._get_crop_region(w, h)
        cropped = frame[y0:y1, x0:x1]
        crop_h, crop_w = cropped.shape[:2]
        if crop_w == 0 or crop_h == 0:
            return None, (0, 0, 1.0, 1.0)
        resized = cv2.resize(cropped, YOLO_INPUT_SIZE)
        scale_x = crop_w / YOLO_INPUT_SIZE[0]
        scale_y = crop_h / YOLO_INPUT_SIZE[1]
        predict_start = time.monotonic()
        results = self.model.predict(resized, conf=YOLO_CONF_THRESHOLD,
                                     iou=YOLO_IOU_THRESHOLD, verbose=False)
        predict_duration = time.monotonic() - predict_start
        if predict_duration > 1.0:
            self.get_logger().warn(f'YOLO-inferentie duurde {predict_duration:.2f}s (traag).')
        return results, (x0, y0, scale_x, scale_y)

    @staticmethod
    def _bbox_crop_to_frame(x1, y1, x2, y2, crop_info):
        crop_x0, crop_y0, scale_x, scale_y = crop_info
        fx1 = int(crop_x0 + x1 * scale_x)
        fy1 = int(crop_y0 + y1 * scale_y)
        fx2 = int(crop_x0 + x2 * scale_x)
        fy2 = int(crop_y0 + y2 * scale_y)
        return fx1, fy1, fx2, fy2

    def _lookup_depth(self, depth_frame, x_px_rgb, y_px_rgb, window=8):
        depth_h, depth_w = depth_frame.shape[:2]
        x_px = int(x_px_rgb * depth_w / RGB_WIDTH)
        y_px = int(y_px_rgb * depth_h / RGB_HEIGHT)
        x0, x1 = max(0, x_px - window), min(depth_w, x_px + window + 1)
        y0, y1 = max(0, y_px - window), min(depth_h, y_px + window + 1)
        patch = depth_frame[y0:y1, x0:x1]
        valid = patch[patch > 0]
        if valid.size == 0:
            self.get_logger().warn(
                f'Geen geldige depth op depth-coord=({x_px},{y_px}) '
                f'[rgb=({x_px_rgb},{y_px_rgb})], frame={depth_w}x{depth_h}'
            )
            return None
        return float(np.median(valid))

    def _run_pipeline(self):
        with dai.Pipeline() as pipeline:
            device = pipeline.getDefaultDevice()

            calib = device.readCalibration()
            intrinsics = calib.getCameraIntrinsics(
                dai.CameraBoardSocket.CAM_A, RGB_WIDTH, RGB_HEIGHT
            )
            self.camera_matrix = np.array(intrinsics, dtype=np.float64)
            self.get_logger().info(
                f'Camera-intrinsics: fx={self.camera_matrix[0,0]:.1f}, '
                f'fy={self.camera_matrix[1,1]:.1f}'
            )

            cam = pipeline.create(dai.node.Camera).build()
            queue_rgb = cam.requestOutput(
                (RGB_WIDTH, RGB_HEIGHT), dai.ImgFrame.Type.BGR888p
            ).createOutputQueue()

            mono_left = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B)
            mono_right = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C)
            left_out = mono_left.requestOutput((DEPTH_WIDTH, DEPTH_HEIGHT), dai.ImgFrame.Type.NV12)
            right_out = mono_right.requestOutput((DEPTH_WIDTH, DEPTH_HEIGHT), dai.ImgFrame.Type.NV12)

            stereo = pipeline.create(dai.node.StereoDepth)
            stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.ROBOTICS)
            stereo.setLeftRightCheck(True)
            stereo.setExtendedDisparity(False)
            stereo.setSubpixel(True)
            stereo.setOutputSize(DEPTH_WIDTH, DEPTH_HEIGHT)
            stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)

            left_out.link(stereo.left)
            right_out.link(stereo.right)
            queue_depth = stereo.depth.createOutputQueue()

            pipeline.start()
            self.get_logger().info('DepthAI pipeline gestart.')

            queue_timeout = timedelta(seconds=2)

            while pipeline.isRunning() and rclpy.ok():
                rgb_data = queue_rgb.get(queue_timeout)
                if rgb_data is None:
                    self.get_logger().warn('Geen RGB-frame binnen timeout.')
                    continue
                depth_data = queue_depth.get(queue_timeout)
                if depth_data is None:
                    self.get_logger().warn('Geen depth-frame binnen timeout.')
                    continue

                frame = rgb_data.getCvFrame()
                depth_frame = depth_data.getFrame()

                self._detect_aruco(frame)

                if self.model is not None:
                    results, crop_info = self._run_yolo_on_crop(frame)

                    if results is not None:
                        for result in results:
                            for idx, box in enumerate(result.boxes):
                                cls_int = int(box.cls[0])
                                label = LABELS[cls_int] if cls_int < len(LABELS) else 'onbekend'
                                confidence = float(box.conf[0])

                                cx1, cy1, cx2, cy2 = map(int, box.xyxy[0].tolist())
                                x1, y1, x2, y2 = self._bbox_crop_to_frame(
                                    cx1, cy1, cx2, cy2, crop_info)

                                x_px, y_px = self._find_centroid_in_bbox(frame, x1, y1, x2, y2)

                                # Rotatiehoek berekenen via minAreaRect op contour
                                rotation_deg = self._get_rotation_angle(frame, x1, y1, x2, y2)

                                # Depth ophalen met temporele filtering per positie-bucket
                                pos_key = (x_px // POSITION_BUCKET_PX,
                                           y_px // POSITION_BUCKET_PX)
                                raw_depth = self._lookup_depth(depth_frame, x_px, y_px)
                                if raw_depth is not None and raw_depth > 0:
                                    self._depth_history[pos_key].append(raw_depth)
                                depth_mm = float(np.median(self._depth_history[pos_key])) \
                                    if self._depth_history[pos_key] else raw_depth

                                hoogte_mm, blocked, xm, ym = self._publish_object_transform(
                                    label, x_px, y_px, depth_mm, idx
                                )

                                if blocked:
                                    continue

                                # JSON publiceren inclusief rotatiehoek
                                resultaat = {
                                    'label': label,
                                    'confidence': round(confidence, 3),
                                    'x_px': x_px,
                                    'y_px': y_px,
                                    'x_mm': round(xm, 1),
                                    'y_mm': round(ym, 1),
                                    'z_mm': float(depth_mm) if depth_mm is not None else 0.0,
                                    'hoogte_mm': round(hoogte_mm, 1),
                                    'rotatie_deg': rotation_deg
                                }
                                msg = String()
                                msg.data = json.dumps(resultaat)
                                self.pub_detectie.publish(msg)

                                self.get_logger().info(
                                    f'{label} | conf={confidence:.2f} | '
                                    f'x={xm:.0f}mm y={ym:.0f}mm | '
                                    f'hoogte={hoogte_mm:.1f}mm | '
                                    f'rotatie={rotation_deg}°'
                                )

                                # Overlay tekenen
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.circle(frame, (x_px, y_px), 4, (0, 0, 255), -1)

                                # Label + confidence boven de box
                                cv2.putText(frame, f'{label} {confidence:.0%}',
                                            (x1, y1 - 8),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

                                # Coördinaten + rotatie onder de box (twee regels)
                                if depth_mm and depth_mm > 0:
                                    cv2.putText(frame,
                                                f'x:{xm:.0f} y:{ym:.0f} h:{hoogte_mm:.0f}mm',
                                                (x1, y2 + 14),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1)
                                    cv2.putText(frame,
                                                f'rot:{rotation_deg}deg',
                                                (x1, y2 + 28),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 200, 255), 1)

                    # Crop-gebied (blauwe rand)
                    crop_x0, crop_y0, scale_x, scale_y = crop_info
                    crop_x1 = int(crop_x0 + YOLO_INPUT_SIZE[0] * scale_x)
                    crop_y1 = int(crop_y0 + YOLO_INPUT_SIZE[1] * scale_y)
                    cv2.rectangle(frame, (crop_x0, crop_y0), (crop_x1, crop_y1), (255, 0, 0), 1)

                # Publiceren op 640x480
                publish_frame = cv2.resize(frame, (PUBLISH_WIDTH, PUBLISH_HEIGHT))

                msg_img = Image()
                msg_img.header.stamp = self.get_clock().now().to_msg()
                msg_img.height = publish_frame.shape[0]
                msg_img.width = publish_frame.shape[1]
                msg_img.encoding = 'bgr8'
                msg_img.step = publish_frame.shape[1] * 3
                msg_img.data = publish_frame.tobytes()
                self.pub_camera.publish(msg_img)

                cv2.imshow("vision_node - camera feed", publish_frame)
                cv2.waitKey(1)
                time.sleep(0.5)


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
