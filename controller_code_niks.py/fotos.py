#!/usr/bin/env python3
import cv2
import depthai as dai
import os
from datetime import datetime

SAVE_DIR = "dataset/raw_images"
os.makedirs(SAVE_DIR, exist_ok=True)

foto_teller = 0

try:
    with dai.Pipeline() as pipeline:
        cam = pipeline.create(dai.node.Camera).build()
        queue = cam.requestOutput((640, 480)).createOutputQueue()

        pipeline.start()
        print("OAK-D gestart. SPATIE = foto maken | Q = stoppen")

        while pipeline.isRunning():
            frame_data = queue.get()
            assert isinstance(frame_data, dai.ImgFrame)
            frame = frame_data.getCvFrame()

            cv2.putText(frame, f"Fotos: {foto_teller} | SPATIE = foto | Q = stop",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("OAK-D Camera", frame)

            toets = cv2.waitKey(1) & 0xFF

            if toets == ord('q'):
                break
            elif toets == ord(' '):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                pad = os.path.join(SAVE_DIR, f"foto_{timestamp}.jpg")
                cv2.imwrite(pad, frame)
                foto_teller += 1
                print(f"[{foto_teller}] Opgeslagen: {pad}")

except Exception as e:
    print(f"FOUT: {e}")
finally:
    cv2.destroyAllWindows()
    print(f"\nKlaar! {foto_teller} foto('s) opgeslagen in '{SAVE_DIR}'.")