from datetime import datetime
from ultralytics import YOLO

from src.db.data_base import init_db
from src.utils.pipeline import process_frame
from src.utils.persistence import persist_interval, persist_disappeared

import cv2
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

cap = cv2.VideoCapture("./Resources/carLicence6.mp4")
model = YOLO("models/best.pt")
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

        tracked, license_plates = process_frame(frame, count, model, license_plates)
        startTime = persist_interval(license_plates, saved_plates, startTime, currentTime)
        persist_disappeared(license_plates, saved_plates, tracked, currentTime)

        display = cv2.resize(frame, (1280, 768))
        cv2.imshow("Video", display)
        if cv2.waitKey(1) & 0xFF == ord('1'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()