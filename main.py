from datetime import datetime
from ultralytics import YOLO

from src.db.data_base import init_db
from src.utils.pipeline import process_frame
from src.utils.persistence import persist_interval, persist_disappeared

import cv2
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

cap = cv2.VideoCapture("./Resources/carLicence4.mp4")

plate_model = YOLO("models/plate/best.pt")

vehicle_model = YOLO("models/vehiculos/yolov10n.pt")

count = 0

init_db()

startTime = datetime.now()
saved_plates = set()
license_plates = {}

while True:
    ret, frame = cap.read()
    if ret:
        currentTime = datetime.now()
        count += 1
        print(f"Frame Number: {count}")

        display = cv2.resize(frame, (1280, 768))
        cv2.imshow("Video", display)
        if cv2.waitKey(1) & 0xFF == ord('1'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()