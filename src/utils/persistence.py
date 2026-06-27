from datetime import datetime
from src.db.data_base import save_to_database
from src.json.json_writer import save_json


def persist_interval(license_plates, saved_plates, startTime, currentTime):
    if (currentTime - startTime).seconds < 2:
        return startTime

    endTime = currentTime
    try:
        new_plates = {
            track_id: (plate, is_valid, image, score, confirm_count)
            for track_id, (plate, is_valid, image, score, confirm_count) in license_plates.items()
            if plate not in saved_plates and confirm_count >= 2
        }
        if new_plates:
            saved_plates.update(plate for plate, *_ in new_plates.values())
            save_json(
              [(plate, is_valid, image, score) for plate, is_valid, image, score, count in new_plates.values()],
              startTime, endTime
            )
            save_to_database(
              [(plate, is_valid, image) for plate, is_valid, image, score, count in new_plates.values()],
              startTime, endTime
          )

    except Exception as e:
        print(f"Error in persisting data: {e}")
    finally:
        for track_id in list(new_plates.keys()):
            license_plates.pop(track_id, None)

    return endTime

def persist_disappeared(license_plates, saved_plates, tracked, currentTime):
    active_ids = set(tracked.tracker_id) if tracked.tracker_id is not None else set()
    disappeared = set(license_plates.keys()) - active_ids

    for track_id in disappeared:
        plate, is_valid, image, score, confirm_count = license_plates.pop(track_id)
        if plate not in saved_plates and confirm_count >= 2:
            saved_plates.add(plate)

