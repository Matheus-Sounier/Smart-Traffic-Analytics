import json
import os

from datetime import datetime

def save_json(license_plates, startTime, endTime):
    interval_data = {
        "Start Time": startTime.isoformat(),
        "End Time": endTime.isoformat(),
        "License Plates": [
            {"plate": plate, "valid": is_valid}
            for plate, is_valid, image in license_plates
        ]
    }

    interval_file_path = "./src/json/output/output_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
    with open(interval_file_path, 'w') as f:
        json.dump(interval_data, f, indent=2)

    cummulative_file_path = "./src/json/plate_data/LicensePlateData.json"
    if os.path.exists(cummulative_file_path):
        with open(cummulative_file_path, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.append(interval_data)
    with open(cummulative_file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)