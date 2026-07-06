from src.utils.tracker import update_tracker, tracker
from src.utils.ocr import paddle_ocr
from src.utils.plate_validator import validate_plate

from supervision import Detections
import numpy as np
import cv2

VEHICLE_CLASSES = {2, 3, 5, 7}
VEHICLE_CONF_THRESHOLD = 0.60


def process_frame(frame, count, model, license_plates):
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
            label = f"{plate} ({status}) [{confirm_count}/2]"
            textSize = cv2.getTextSize(label, 0, fontScale=0.5, thickness=2)[0]
            c2 = x1 + textSize[0], y1 - textSize[1] - 3
            color = (0, 255, 0) if confirm_count >= 2 else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), c2, (255, 0, 0), -1)
            cv2.putText(frame, label, (x1, y1 - 2), 0, 0.5, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

    return tracked, license_plates