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

        if count % 3 == 0:
            raw_text, score = paddle_ocr(frame, x1, y1, x2, y2)
            if raw_text:
                plate, is_valid = validate_plate(raw_text)
                if plate:
                    _, buffer = cv2.imencode('.jpg', frame[y1:y2, x1:x2])
                    plate_image = buffer.tobytes()
                    if track_id not in license_plates:
                        license_plates[track_id] = (plate, is_valid, plate_image, score, 1)
                    else:
                        existing_plate, _, _, existing_score, existing_count = license_plates[track_id]

                        if plate == existing_plate:
                            new_count = existing_count + 1
                            best_score = max(score, existing_score)
                            best_image = plate_image if score >= existing_score else license_plates[track_id][2]
                            license_plates[track_id] = (plate, is_valid, best_image, best_score, new_count)

                        elif score > existing_score:
                            license_plates[track_id] = (plate, is_valid, plate_image, score, 1)

        if track_id in license_plates:
            plate, is_valid, _, score, confirm_count = license_plates[track_id]
            status = 'Ok' if is_valid else '?'
            label = f"{plate} ({status}) [{confirm_count}/1]"
            textSize = cv2.getTextSize(label, 0, fontScale=0.5, thickness=2)[0]
            c2 = x1 + textSize[0], y1 - textSize[1] - 3
            color = (0, 255, 0) if confirm_count >= 1 else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), c2, (255, 0, 0), -1)
            cv2.putText(frame, label, (x1, y1 - 2), 0, 0.5, [255, 255, 255],
                        thickness=1, lineType=cv2.LINE_AA)

    return tracked, license_plates