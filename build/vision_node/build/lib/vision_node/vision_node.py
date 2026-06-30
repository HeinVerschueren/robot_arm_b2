#!/usr/bin/env python3
#vision_node.py Fast Robotic Solutions 
#projectgroep B2
#Ontwerper:Rens Peeters
#Detecteer objecten (Balk, Kubus, Maan, Octagon) via een
#OAK-D camera en YOLOv8, en publiceert hun positie (x, y, z in mm) en
#rotatie via ROS2-topics.
import os
import sys
from pathlib import Path

#Bepaal workspace-root (3 mappen omhoog vanaf dit bestand)
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
#Pad naar gegenereerde Python-bindings van frs_interfaces
ROS_SITE_PACKAGES = WORKSPACE_ROOT / 'install' / 'frs_interfaces' / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
#Voeg toe aan sys.path zodat frs_interfaces importeerbaar is
if ROS_SITE_PACKAGES.exists() and str(ROS_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(ROS_SITE_PACKAGES))

#Pad naar gecompileerde interface-libraries
ROS_INTERFACE_LIB_DIR = WORKSPACE_ROOT / 'install' / 'frs_interfaces' / 'lib'
if ROS_INTERFACE_LIB_DIR.exists():
    #LD_LIBRARY_PATH aanvullen zodat .so-bestanden gevonden worden
    library_path = str(ROS_INTERFACE_LIB_DIR)
    existing_ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
    paths = [p for p in existing_ld_library_path.split(':') if p]
    if library_path not in paths:
        os.environ['LD_LIBRARY_PATH'] = ':'.join(paths + [library_path]) if paths else library_path

    #PYTHONPATH aanvullen zodat frs_interfaces ook in subprocessen werkt
    existing_pythonpath = os.environ.get('PYTHONPATH', '')
    python_paths = [p for p in existing_pythonpath.split(':') if p]
    if str(ROS_SITE_PACKAGES) not in python_paths:
        os.environ['PYTHONPATH'] = ':'.join(python_paths + [str(ROS_SITE_PACKAGES)]) if python_paths else str(ROS_SITE_PACKAGES)

#ROS2-imports
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, Float32
from frs_interfaces.msg import DetectieResultaat

#Camera, beeldverwerking en algemene libraries
import cv2
import depthai as dai
import numpy as np
import threading
import time
import collections
from datetime import timedelta

# =============================================================================
# CONFIGURATIE
# =============================================================================

#Pad naar het YOLOv8-gewichtenbestand
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'best.pt')

#Klassenamen — volgorde moet overeenkomen met het getrainde model
LABELS = ['Balk', 'Kubus', 'Maan', 'Octagon']

#Vaste z-hoogte per klasse in mm (alle objecten liggen plat op tafel)
Z_PER_KLASSE = {
    'Maan':    10.0,
    'Octagon': 10.0,
    'Balk':    10.0,
    'Kubus':   10.0,
}

#Aantal frames voor mediaan-smoothing van de centroidpositie
CENTROID_SMOOTH_FRAMES = 5

#ArUco-markerinstellingen
ARUCO_DICT          = cv2.aruco.DICT_4X4_50  #markerwoordenboek
ARUCO_MARKER_ID     = 0                       #te gebruiken marker-ID
ARUCO_MARKER_SIZE_M = 0.048                   #fysieke markergrootte in meter
CALIBRATION_FRAMES  = 20                      #frames voor mediaan-kalibratie

#YOLO-inferentie instellingen
YOLO_CONF_THRESHOLD = 0.85      #lage drempel voor testen; productie = 0.85
YOLO_IOU_THRESHOLD  = 0.4       #IoU-drempel voor non-maximum suppression
YOLO_INPUT_SIZE     = (640, 640)  #invoergrootte van het model

#Camera- en publicatieresolutie
RGB_WIDTH      = 1920  #capture breedte
RGB_HEIGHT     = 1080  #capture hoogte
PUBLISH_WIDTH  = 960   #publiceer breedte (gehalveerd voor bandbreedte)
PUBLISH_HEIGHT = 540   #publiceer hoogte

#Grootte van het werkgebied rondom de ArUco-marker (vierkant in mm)
WORKSPACE_SIZE_MM = 500.0

#Aantal frames dat een detectie zichtbaar blijft na het verdwijnen van een object
PERSIST_FRAMES = 5

#Venstergrootte voor labelstabilisatie via meerderheidstemming
LABEL_HISTORY = 10

#Correctiefactor voor zwaartepunt halve schijf (Maan).
#Geometrisch zwaartepunt halve schijf = 4r/3π vanaf middelpunt → factor = 2/(3π)
MAAN_CM_FACTOR = 2.0 / (3.0 * np.pi)  # ≈ 0.2122

# =============================================================================


class VisionNode(Node):
    """
    Hoofd-node voor het vision-systeem.

    Publiceert:
      camera_beelden        – live cameraframe (960×540, BGR8)
      detectie_resultaten   – DetectieResultaat per gedetecteerd object
      afgesloten            – Bool True wanneer de node gestopt is
      vision_gereed         – Bool True zodra ArUco-kalibratie voltooid is

    Ontvangt:
      shut_down             – Bool True om de node te stoppen
      confidence_drempel    – Float32 om YOLO-drempel live aan te passen
    """

    def __init__(self):
        super().__init__('vision_node')

        #Publishers
        self.pub_camera        = self.create_publisher(Image,             'camera_beelden',      10)
        self.pub_detectie      = self.create_publisher(DetectieResultaat, 'detectie_resultaten', 10)
        self.pub_afgesloten    = self.create_publisher(Bool,              'afgesloten',          10)
        self.pub_vision_gereed = self.create_publisher(Bool,              'vision_gereed',       10)

        #Subscribers
        self.create_subscription(Bool,    'shut_down',          self._cb_afsluiten,  10)
        self.create_subscription(Float32, 'confidence_drempel', self._cb_confidence, 10)

        self._afsluiten      = False               #True → pipeline stopt
        self._conf_threshold = YOLO_CONF_THRESHOLD  #aanpasbaar via topic

        #ArUco-detector initialiseren
        aruco_dict          = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        aruco_params        = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

        #3D-hoekpunten van de marker in markercoördinaten (vlak, z=0)
        half = ARUCO_MARKER_SIZE_M / 2.0
        self.marker_obj_pts = np.array([
            [-half,  half, 0], [ half,  half, 0],
            [ half, -half, 0], [-half, -half, 0]
        ], dtype=np.float64)

        #Cameraparameters en kalibratiestatus
        self.camera_matrix    = None   #intrinsieke matrix uit DepthAI
        self.marker_rvec      = None   #rotatie-vector marker (mediaan)
        self.marker_tvec      = None   #translatie-vector marker (mediaan)
        self.marker_center_px = None   #pixelmiddelpunt marker (mediaan)
        self.marker_size_px   = None   #markergrootte in pixels (mediaan)
        self.marker_locked    = False  #True zodra kalibratie klaar is

        #Kalibratiebuffers (mediaan over CALIBRATION_FRAMES metingen)
        self._cal_tvec   = collections.deque(maxlen=CALIBRATION_FRAMES)
        self._cal_rvec   = collections.deque(maxlen=CALIBRATION_FRAMES)
        self._cal_center = collections.deque(maxlen=CALIBRATION_FRAMES)
        self._cal_size   = collections.deque(maxlen=CALIBRATION_FRAMES)

        #Histories voor temporele stabilisatie per positiesleutel (80×80 px grid)
        self._label_history    = collections.defaultdict(
            lambda: collections.deque(maxlen=LABEL_HISTORY))
        self._centroid_history = collections.defaultdict(
            lambda: collections.deque(maxlen=CENTROID_SMOOTH_FRAMES))

        #Persistente detecties: blijven PERSIST_FRAMES frames zichtbaar
        self._persistent_detections = {}

        #YOLOv8-model laden
        self.model = None
        if os.path.exists(MODEL_PATH):
            from ultralytics import YOLO
            self.model = YOLO(MODEL_PATH)
            self.get_logger().info(f'Model geladen: {MODEL_PATH}')
        else:
            self.get_logger().warn('Geen model gevonden — alleen camera_beelden wordt gepubliceerd.')

        #Pipeline in aparte thread (blocking camera-loop)
        threading.Thread(target=self._run_pipeline, daemon=True).start()
        self.get_logger().info('vision_node gestart.')

    # ------------------------------------------------------------------
    def _cb_afsluiten(self, msg):
        """Callback voor 'shut_down'-topic. Zet afsluitvlag."""
        if msg.data:
            self.get_logger().info('Afsluitverzoek ontvangen.')
            self._afsluiten = True

    def _cb_confidence(self, msg):
        """
        Callback voor 'confidence_drempel'-topic.
        Past de YOLO-drempel live aan (0 < waarde ≤ 1).
        Gebruik: ros2 topic pub /confidence_drempel std_msgs/msg/Float32 "data: 0.85"
        """
        v = float(msg.data)
        if 0.0 < v <= 1.0:
            self._conf_threshold = v
            self.get_logger().info(f'Confidence drempel: {v:.2f}')
        else:
            self.get_logger().warn(f'Ongeldige confidence drempel: {v}')

    # ------------------------------------------------------------------
    def _enhance(self, frame):
        """
        Beeldverbetering voor betere detectie van matte, donkere objecten:
          1. CLAHE op L-kanaal in LAB-kleurruimte (adaptief contrast)
          2. Scherptefilter (unsharp-mask kernel)
        """
        #Naar LAB-kleurruimte en contrast verbeteren op het L-kanaal
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
        frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        #Scherptefilter toepassen
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(frame, -1, kernel)

    # ------------------------------------------------------------------
    def _detect_aruco(self, frame):
        """
        Detecteert ArUco-marker ID 0 en verzamelt CALIBRATION_FRAMES poses.
        Na voldoende metingen worden mediaan-waarden berekend en vergrendeld.
        Publiceert 'vision_gereed' zodra kalibratie klaar is.
        """
        if self.camera_matrix is None:
            return

        #Na vergrendeling geen herberekening meer nodig
        if self.marker_locked:
            cv2.putText(frame, 'Marker vergrendeld',
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            return

        #Marker zoeken in grijswaardenbeeld
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

            #Pose van marker berekenen t.o.v. camera
            img_pts = corners[i][0].astype(np.float64)
            ok, rvec, tvec = cv2.solvePnP(
                self.marker_obj_pts, img_pts, self.camera_matrix, np.zeros((5, 1)))
            if not ok:
                continue

            #Meting toevoegen aan kalibratiebuffers
            self._cal_tvec.append(tvec.flatten())
            self._cal_rvec.append(rvec.flatten())
            self._cal_center.append(img_pts.mean(axis=0))
            self._cal_size.append(np.linalg.norm(img_pts[0] - img_pts[1]))

            n = len(self._cal_tvec)
            cv2.aruco.drawDetectedMarkers(frame, [corners[i]], np.array([[marker_id]]))
            cv2.putText(frame, f'Kalibreren... {n}/{CALIBRATION_FRAMES}',
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

            if n >= CALIBRATION_FRAMES:
                #Mediaan-waarden berekenen voor robuuste kalibratie
                self.marker_tvec      = np.median(self._cal_tvec, axis=0).reshape(3, 1)
                self.marker_rvec      = np.median(self._cal_rvec, axis=0).reshape(3, 1)
                self.marker_center_px = np.median(self._cal_center, axis=0)
                self.marker_size_px   = float(np.median(self._cal_size))
                self.marker_locked    = True
                self.get_logger().info(
                    f'Marker vergrendeld. tvec={self.marker_tvec.flatten().round(4)}')

                #Signaleer dat detectie kan beginnen
                msg_gereed = Bool()
                msg_gereed.data = True
                self.pub_vision_gereed.publish(msg_gereed)
                self.get_logger().info('vision_gereed gepubliceerd.')

    # ------------------------------------------------------------------
    def _pixel_to_world_mm(self, x_px, y_px):
        """
        Converteert pixelcoördinaten naar mm t.o.v. de ArUco-marker.
        Schaalfactor: marker_size_px / (markergrootte_m × 1000).
        y-as is omgekeerd (pixel-y loopt naar beneden, wereld-y naar boven).
        Geeft (None, None) als kalibratie nog niet klaar is.
        """
        if self.marker_center_px is None or self.marker_size_px is None:
            return None, None
        px_per_mm = self.marker_size_px / (ARUCO_MARKER_SIZE_M * 1000.0)
        dx_px = x_px - self.marker_center_px[0]
        dy_px = y_px - self.marker_center_px[1]
        x_mm  =  dx_px / px_per_mm
        y_mm  = -dy_px / px_per_mm  #omgekeerd: pixel-y daalt, wereld-y stijgt
        return x_mm, y_mm

    # ------------------------------------------------------------------
    def _get_contour(self, frame, x1, y1, x2, y2, margin=4):
        """
        Extraheert het grootste contour in de bounding-box (met marge).
        Gebruikt Otsu-thresholding. Geeft (None, cx0, cy0) bij mislukken.
        """
        #ROI bepalen met marge, binnen framegrenzen
        h, w = frame.shape[:2]
        cx0 = max(0, x1 - margin); cy0 = max(0, y1 - margin)
        cx1 = min(w, x2 + margin); cy1 = min(h, y2 + margin)
        roi = frame[cy0:cy1, cx0:cx1]
        if roi.size == 0:
            return None, cx0, cy0

        #Otsu-thresholding en grootste contour zoeken
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, cx0, cy0

        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) < 20:  #te klein → ruis
            return None, cx0, cy0

        return largest, cx0, cy0

    # ------------------------------------------------------------------
    def _bepaal_z(self, label):
        """
        Geeft de vaste z-hoogte (mm) voor het gegeven label.
        Alle objecten liggen plat op tafel → altijd 10 mm.
        """
        return Z_PER_KLASSE.get(label, 10.0)

    # ------------------------------------------------------------------
    @staticmethod
    def _get_rotation(frame, x1, y1, x2, y2, margin=4):
        """
        Berekent de rotatie in graden via minAreaRect op het grootste contour.
        Bereik: -45° … +45°. Geeft 0.0 terug bij mislukken.
        """
        h, w = frame.shape[:2]
        roi = frame[max(0, y1-margin):min(h, y2+margin),
                    max(0, x1-margin):min(w, x2+margin)]
        if roi.size == 0:
            return 0.0
        #Otsu-thresholding en grootste contour zoeken
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.0
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) < 20:
            return 0.0
        #Hoek van kleinste omsluitende rechthoek
        _, _, angle = cv2.minAreaRect(largest)
        if angle < -45:
            angle += 90.0  #corrigeer naar leesbaar bereik
        return round(angle, 1)

    # ------------------------------------------------------------------
    def _get_centroid(self, frame, x1, y1, x2, y2, label='', margin=4):
        """
        Bepaalt het grijppunt (pixelpositie) waar de gripper het object oppakt.

        Voor de meeste objecten (Balk, Octagon, Kubus) is het zwaartepunt van
        de vorm een goed en betrouwbaar grijppunt, want deze vormen zijn
        symmetrisch/gevuld. Daarvoor gebruiken we cv2.moments: een standaard
        OpenCV-berekening die het geometrische zwaartepunt van een contour geeft.

        De Maan is een halve-maanvorm (benaderd als halve schijf). Het
        zwaartepunt van zo'n vorm ligt wiskundig altijd op een vaste afstand
        van 4r/(3π) vanaf het middelpunt van de rechte zijde, richting de
        gebogen kant — een bekende formule uit de werktuigbouwkunde voor het
        zwaartepunt van een halve cirkel. We gebruiken hiervoor de afmetingen
        van de kleinste omsluitende rechthoek (minAreaRect), wat veel minder
        gevoelig is voor kleine onnauwkeurigheden in de contourdetectie dan
        een berekening die op losse pixels werkt (zoals moments). Hierdoor
        geeft deze methode een consistent grijppunt midden in de Maan, ook
        bij wisselende rotatie of belichting.
        """
        #Fallback-waarde: midden van de bounding box (als er geen contour gevonden wordt)
        bbox_cx = (x1 + x2) // 2
        bbox_cy = (y1 + y2) // 2

        contour, cx0, cy0 = self._get_contour(frame, x1, y1, x2, y2, margin)
        if contour is None:
            return bbox_cx, bbox_cy

        if label == 'Maan':
            #Kleinste omsluitende rechthoek: geeft middelpunt en afmetingen van de vorm
            rect = cv2.minAreaRect(contour)
            (rect_cx, rect_cy), (rw, rh), _ = rect
            rect_cx_frame = cx0 + rect_cx
            rect_cy_frame = cy0 + rect_cy

            #Diameter van de halve schijf = korte zijde van de rechthoek
            diameter = min(rw, rh)
            #Analytische verschuiving van rechthoekcentrum naar werkelijk zwaartepunt
            offset_px = (0.5 - MAAN_CM_FACTOR) * diameter

            #Richting bepalen: van rechthoekcentrum naar het ruwe contourzwaartepunt
            #(alleen de richting wordt gebruikt, niet de exacte positie — dus
            # ongevoelig voor kleine contourruis)
            M = cv2.moments(contour)
            if M['m00'] > 0:
                cont_cx = cx0 + M['m10'] / M['m00']
                cont_cy = cy0 + M['m01'] / M['m00']
                dx, dy = cont_cx - rect_cx_frame, cont_cy - rect_cy_frame
                dist = np.sqrt(dx**2 + dy**2)
            else:
                dist = 0.0

            if dist > 1.0:
                nx, ny = dx / dist, dy / dist
            else:
                #Geen duidelijke richting gevonden: gebruik rechthoekcentrum
                return int(round(rect_cx_frame)), int(round(rect_cy_frame))

            grijp_x = int(round(rect_cx_frame + nx * offset_px))
            grijp_y = int(round(rect_cy_frame + ny * offset_px))
            return grijp_x, grijp_y

        #Standaard: geometrisch zwaartepunt via image moments
        M = cv2.moments(contour)
        if M['m00'] == 0:
            return bbox_cx, bbox_cy
        return int(cx0 + M['m10'] / M['m00']), int(cy0 + M['m01'] / M['m00'])

    # ------------------------------------------------------------------
    def _get_crop(self, w, h):
        """
        Berekent het pixelgebied dat overeenkomt met het werkgebied
        (WORKSPACE_SIZE_MM × WORKSPACE_SIZE_MM) rondom de ArUco-marker.
        Geeft het volledige frame terug als kalibratie nog niet klaar is.
        """
        if self.marker_center_px is None or not self.marker_size_px:
            return 0, 0, w, h
        px_per_mm = self.marker_size_px / (ARUCO_MARKER_SIZE_M * 1000.0)
        half_px   = (WORKSPACE_SIZE_MM / 2.0) * px_per_mm
        cx, cy    = self.marker_center_px
        x0 = int(max(0, cx - half_px)); y0 = int(max(0, cy - half_px))
        x1 = int(min(w, cx + half_px)); y1 = int(min(h, cy + half_px))
        if (x1 - x0) < 50 or (y1 - y0) < 50:
            return 0, 0, w, h
        return x0, y0, x1, y1

    # ------------------------------------------------------------------
    def _run_yolo(self, frame):
        """
        Snijdt werkgebied uit, schaalt naar YOLO-invoergrootte en voert inferentie uit.
        Geeft (results, crop_info) terug; crop_info bevat (x0, y0, scale_x, scale_y).
        """
        h, w = frame.shape[:2]
        x0, y0, x1, y1 = self._get_crop(w, h)
        cropped = frame[y0:y1, x0:x1]
        cw, ch  = cropped.shape[1], cropped.shape[0]
        if cw == 0 or ch == 0:
            return None, (0, 0, 1.0, 1.0)
        #Schalen naar vaste YOLO-invoergrootte
        resized = cv2.resize(cropped, YOLO_INPUT_SIZE)
        scale_x = cw / YOLO_INPUT_SIZE[0]
        scale_y = ch / YOLO_INPUT_SIZE[1]
        results = self.model.predict(resized, conf=self._conf_threshold,
                                     iou=YOLO_IOU_THRESHOLD, verbose=False)
        return results, (x0, y0, scale_x, scale_y)

    @staticmethod
    def _crop_to_frame(cx1, cy1, cx2, cy2, crop_info):
        """Rekent bounding-box van YOLO-ruimte terug naar framecoördinaten."""
        x0, y0, sx, sy = crop_info
        return (int(x0 + cx1*sx), int(y0 + cy1*sy),
                int(x0 + cx2*sx), int(y0 + cy2*sy))

    # ------------------------------------------------------------------
    def _run_pipeline(self):
        """
        Hoofd camera-loop. Stappen per frame:
          1. Frame ophalen (RGB 1920×1080)
          2. Beeldverbetering (CLAHE + scherpte)
          3. ArUco-kalibratie (tot vergrendeld)
          4. YOLO-inferentie (alleen na kalibratie)
          5. Centroid, rotatie en z-hoogte bepalen
          6. Labelstabilisatie + centroid-smoothing
          7. DetectieResultaat publiceren per object
          8. Frame publiceren (960×540)
        """
        with dai.Pipeline() as pipeline:
            #Camera-intrinsics ophalen uit DepthAI-kalibratie
            device = pipeline.getDefaultDevice()
            calib  = device.readCalibration()
            self.camera_matrix = np.array(
                calib.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A, RGB_WIDTH, RGB_HEIGHT),
                dtype=np.float64)
            self.get_logger().info(
                f'Intrinsics: fx={self.camera_matrix[0,0]:.1f} fy={self.camera_matrix[1,1]:.1f}')

            #RGB-camera met handmatige focus (~280 mm werkafstand)
            cam = pipeline.create(dai.node.Camera).build()
            cam.initialControl.setManualFocus(130)
            queue_rgb = cam.requestOutput(
                (RGB_WIDTH, RGB_HEIGHT), dai.ImgFrame.Type.BGR888p
            ).createOutputQueue()

            pipeline.start()
            self.get_logger().info('DepthAI pipeline gestart (RGB only).')

            timeout = timedelta(seconds=2)

            while pipeline.isRunning() and rclpy.ok():

                #Stoppen indien afsluitverzoek ontvangen
                if self._afsluiten:
                    self.get_logger().info('Vision node afgesloten.')
                    msg = Bool(); msg.data = True
                    self.pub_afgesloten.publish(msg)
                    break

                #Frame ophalen
                rgb_data = queue_rgb.get(timeout)
                if rgb_data is None:
                    self.get_logger().warn('Geen RGB-frame binnen timeout.')
                    continue

                frame = self._enhance(rgb_data.getCvFrame())
                self._detect_aruco(frame)

                #Persistente detecties ouder maken; verlopen detecties verwijderen
                for key in list(self._persistent_detections):
                    self._persistent_detections[key]['frames_since_seen'] += 1
                    if self._persistent_detections[key]['frames_since_seen'] > PERSIST_FRAMES:
                        del self._persistent_detections[key]

                h, w = frame.shape[:2]
                crop_x0, crop_y0, crop_x1, crop_y1 = self._get_crop(w, h)

                if self.model is not None and self.marker_locked:
                    #YOLO-inferentie op uitgesneden werkgebied
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

                                #Bounding-box terugrekenen naar framecoördinaten
                                cx1, cy1, cx2, cy2 = map(int, box.xyxy[0].tolist())
                                x1, y1, x2, y2 = self._crop_to_frame(
                                    cx1, cy1, cx2, cy2, crop_info)

                                bbox_cx = (x1 + x2) // 2
                                bbox_cy = (y1 + y2) // 2

                                #Objecten buiten werkgebied overslaan
                                if not (ci_x0 <= bbox_cx <= lim_x1 and
                                        ci_y0 <= bbox_cy <= lim_y1):
                                    continue

                                #Nauwkeurig zwaartepunt (Maan: pi-formule halve schijf, overig: moments)
                                x_px_raw, y_px_raw = self._get_centroid(
                                    frame, x1, y1, x2, y2, label=label)

                                rot_deg = self._get_rotation(frame, x1, y1, x2, y2)

                                #Vaste z-hoogte per klasse (altijd 10 mm)
                                z_mm = self._bepaal_z(label)

                                #Positiesleutel op 80×80 px grid voor stabilisatie
                                pos_key = (x_px_raw // 80, y_px_raw // 80)

                                #Labelstabilisatie: meest voorkomend label in history
                                self._label_history[pos_key].append(label)
                                stable_label = max(
                                    set(self._label_history[pos_key]),
                                    key=list(self._label_history[pos_key]).count)

                                #Centroid-smoothing via mediaan over meerdere frames
                                self._centroid_history[pos_key].append((x_px_raw, y_px_raw))
                                xs   = [p[0] for p in self._centroid_history[pos_key]]
                                ys   = [p[1] for p in self._centroid_history[pos_key]]
                                x_px = int(np.median(xs))
                                y_px = int(np.median(ys))

                                #Pixel → mm t.o.v. ArUco-marker
                                x_mm, y_mm = self._pixel_to_world_mm(x_px, y_px)
                                if x_mm is None:
                                    continue

                                #Sla op als persistente detectie
                                self._persistent_detections[pos_key] = {
                                    'label':             stable_label,
                                    'confidence':        confidence,
                                    'x_px': x_px, 'y_px': y_px,
                                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                                    'x_mm': x_mm, 'y_mm': y_mm, 'z_mm': z_mm,
                                    'rotatie_deg':       rot_deg,
                                    'frames_since_seen': 0,
                                }

                    #Werkgebied-rechthoek (blauw)
                    cv2.rectangle(frame, (crop_x0, crop_y0), (crop_x1, crop_y1),
                                  (255, 0, 0), 2)

                    #Publiceer alle actieve detecties
                    for det in self._persistent_detections.values():
                        msg = DetectieResultaat()
                        msg.klasse     = det['label']
                        msg.confidence = float(round(det['confidence'], 3))
                        msg.x          = float(round(det['x_mm'], 1))
                        msg.y          = float(round(det['y_mm'], 1))
                        msg.z          = float(round(det['z_mm'], 1))  #altijd 10.0
                        msg.rotatie    = float(det['rotatie_deg'])
                        self.pub_detectie.publish(msg)

                        self.get_logger().info(
                            f"{det['label']} | conf={det['confidence']:.2f} | "
                            f"x={det['x_mm']:.0f}mm y={det['y_mm']:.0f}mm "
                            f"z={det['z_mm']:.0f}mm | rot={det['rotatie_deg']}deg")

                        #Visualisatie op het beeld
                        x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
                        #Groen = actief gedetecteerd, cyaan = persistent (ouder)
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

                #Frame publiceren (verkleind naar 960×540)
                pub_frame            = cv2.resize(frame, (PUBLISH_WIDTH, PUBLISH_HEIGHT))
                msg_img              = Image()
                msg_img.header.stamp = self.get_clock().now().to_msg()
                msg_img.height       = pub_frame.shape[0]
                msg_img.width        = pub_frame.shape[1]
                msg_img.encoding     = 'bgr8'
                msg_img.step         = pub_frame.shape[1] * 3
                msg_img.data         = pub_frame.tobytes()
                self.pub_camera.publish(msg_img)

                cv2.imshow('vision_node', pub_frame)
                cv2.waitKey(1)
                time.sleep(0.8)  #pauze voor USB-bandbreedte stabiliteit

        cv2.destroyAllWindows()


def main(args=None):
    #ROS2 initialiseren en node starten
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        #Netjes afsluiten
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
