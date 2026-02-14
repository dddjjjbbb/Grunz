"""MegaDetector wrapper using PytorchWildlife."""


def create_detector():
    """Create and return a MegaDetectorV6 instance.

    Weights are downloaded automatically on first invocation.
    """
    from PytorchWildlife.models import detection as pw_detection

    return pw_detection.MegaDetectorV6(version="MDV6-yolov9-c")


def convert_result(pw_result):
    """Convert a PytorchWildlife detection result to the legacy JSON format.

    JSONParser expects each image entry to have:
      - "file": str
      - "max_detection_conf": float
      - "detections": [{"category": str, "conf": float, "bbox": [x1, y1, x2, y2]}]
    """
    detections_obj = pw_result["detections"]
    boxes = detections_obj.xyxy
    confidences = detections_obj.confidence
    class_ids = detections_obj.class_id

    detections = []
    for i in range(len(boxes)):
        detections.append({
            "category": str(int(class_ids[i])),
            "conf": float(confidences[i]),
            "bbox": [float(c) for c in boxes[i]],
        })

    max_conf = float(max(confidences)) if len(confidences) > 0 else 0.0

    return {
        "file": pw_result["img_id"],
        "max_detection_conf": max_conf,
        "detections": detections,
    }
