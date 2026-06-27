from src.utils.tracker import update_tracker
from src.utils.ocr import paddle_ocr
from src.utils.plate_validator import validate_plate

import cv2

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