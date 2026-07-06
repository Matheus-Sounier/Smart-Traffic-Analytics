from src.utils.tracker import update_tracker, tracker
from src.utils.ocr import paddle_ocr
from src.utils.plate_validator import validate_plate

from supervision import Detections
import numpy as np
import cv2

VEHICLE_CLASSES = {2, 3, 5, 7}
VEHICLE_CONF_THRESHOLD = 0.60


def get_vehicle_crops(frame, vehicle_model):
    detections = vehicle_model.predict(frame, conf=VEHICLE_CONF_THRESHOLD, verbose=False)[0]
    h, w = frame.shape[:2]
    crops = []

    for box in detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = box
        if int(class_id) not in VEHICLE_CLASSES:
            continue

        vx1 = max(0, int(x1))
        vy1 = max(0, int(y1))
        vx2 = min(w, int(x2))
        vy2 = min(h, int(y2))

        crop = frame[vy1:vy2, vx1:vx2]
        if crop.size == 0:
            continue

        cv2.rectangle(frame, (vx1, vy1), (vx2, vy2), (0, 255, 0), 2)
        cv2.putText(frame, f"vehicle {score:.0%}", (vx1, vy1 - 5),
                    0, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        crops.append((crop, vx1, vy1, vx2, vy2))

    return crops