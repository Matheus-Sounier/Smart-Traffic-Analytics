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


def process_frame(frame, count, model, license_plates, vehicle_model=None):

    if vehicle_model is not None:
        vehicle_crops = get_vehicle_crops(frame, vehicle_model)

        if not vehicle_crops:
            return None, license_plates

        all_xyxy = []
        for crop, vx1, vy1, vx2, vy2 in vehicle_crops:
            plate_results = model.predict(crop, conf=0.10, verbose=False)[0]
            for box in plate_results.boxes.xyxy.cpu().numpy():
                px1, py1, px2, py2 = box
                all_xyxy.append([px1 + vx1, py1 + vy1, px2 + vx1, py2 + vy1])

        if not all_xyxy:
            return None, license_plates

        xyxy = np.array(all_xyxy, dtype=float)
        conf = np.ones(len(xyxy))
        class_id = np.zeros(len(xyxy), dtype=int)

        detections = Detections(xyxy=xyxy, confidence=conf, class_id=class_id)
        tracked = tracker.update_with_detections(detections)

    else:
        results = model.predict(frame, conf=0.10)
        tracked = update_tracker(results)

    for i in range(len(tracked)):
        x1, y1, x2, y2 = map(int, tracked.xyxy[i])
        if tracked.tracker_id is None:
            continue
        track_id = tracked.tracker_id[i]

        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)