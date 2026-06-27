from supervision import ByteTrack, Detections
import numpy as np

tracker = ByteTrack(
    track_activation_threshold=0.20,
    lost_track_buffer=60,
    minimum_matching_threshold=0.8
)

def update_tracker(results):
    boxes = results[0].boxes

    if len(boxes) == 0:
        return Detections.empty()

    xyxy     = boxes.xyxy.cpu().numpy()
    conf     = boxes.conf.cpu().numpy()
    class_id = boxes.cls.cpu().numpy().astype(int)

    detections = Detections(
        xyxy=xyxy,
        confidence=conf,
        class_id=class_id
    )

    return tracker.update_with_detections(detections)