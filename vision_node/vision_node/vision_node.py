#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

import cv2
import depthai as dai
import numpy as np
import os
import json
import threading
import time

# Pad naar het getrainde YOLO model (.pt formaat via Ultralytics)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'frs_model.pt')

# Labels van de 4 objectklassen (volgorde moet overeenkomen met model.names)
LABELS = ['Maan', 'Octagon', 'Rechthoek', 'Vierkant']


class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')

        # Publishers
        self.pub_camera = self.create_publisher(Image, 'camera_beelden', 10)
        self.pub_detectie = self.create_publisher(String, 'detectie_resultaten', 10)

        # Controleer of model beschikbaar is en laad het
        self.model = None
        if os.path.exists(MODEL_PATH):
            from ultralytics import YOLO
            self.model = YOLO(MODEL_PATH)
            self.get_logger().info(f'Model gevonden: {MODEL_PATH}')
        else:
            self.get_logger().warn('Geen model gevonden — alleen camera_beelden wordt gepubliceerd.')

        # DepthAI draaien in aparte thread
        self.pipeline_thread = threading.Thread(target=self._run_pipeline, daemon=True)
        self.pipeline_thread.start()

        self.get_logger().info('vision_node gestart.')

    def _run_pipeline(self):
        with dai.Pipeline() as pipeline:

            # --- RGB camera (nieuwe API) ---
            cam = pipeline.create(dai.node.Camera).build()
            queue_rgb = cam.requestOutput((640, 480), dai.ImgFrame.Type.BGR888p).createOutputQueue()

            pipeline.start()
            self.get_logger().info('DepthAI pipeline gestart.')

            while pipeline.isRunning() and rclpy.ok():
                rgb_data = queue_rgb.get()
                if rgb_data is None:
                    continue

                frame = rgb_data.getCvFrame()

                # YOLO detectie uitvoeren op CPU via Ultralytics
                if self.model is not None:
                    results = self.model.predict(frame, conf=0.1, verbose=False)
                    for result in results:
                        for box in result.boxes:
                            cls_int = int(box.cls[0])
                            label = LABELS[cls_int] if cls_int < len(LABELS) else 'onbekend'
                            confidence = float(box.conf[0])
                            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                            # Publiceer detectieresultaat als JSON
                            resultaat = {
                                'label': label,
                                'confidence': round(confidence, 3),
                                'x_px': (x1 + x2) // 2,
                                'y_px': (y1 + y2) // 2,
                                'z_mm': 0.0  # later invullen met ArUco
                            }
                            msg = String()
                            msg.data = json.dumps(resultaat)
                            self.pub_detectie.publish(msg)

                            self.get_logger().info(
                                f'Gedetecteerd: {label} | conf={confidence:.2f} | '
                                f'px=({resultaat["x_px"]}, {resultaat["y_px"]})'
                            )

                            # AI overlay tekenen
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f'{label} {confidence:.0%}',
                                        (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

                # Camera beelden publiceren
                msg_img = Image()
                msg_img.header.stamp = self.get_clock().now().to_msg()
                msg_img.height = frame.shape[0]
                msg_img.width = frame.shape[1]
                msg_img.encoding = 'bgr8'
                msg_img.step = frame.shape[1] * 3
                msg_img.data = frame.tobytes()
                self.pub_camera.publish(msg_img)

                # Live preview (~2 fps)
                cv2.imshow("vision_node - camera feed", frame)
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
