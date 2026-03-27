from ultralytics import YOLO
import json

def get_classes(model_path):
    try:
        model = YOLO(model_path)
        return model.names
    except Exception as e:
        return f"Error loading {model_path}: {e}"

print("yolov8m (1).pt classes:", json.dumps(get_classes("yolov8m (1).pt"), indent=2))
print("best_vehicle_model.pt classes:", json.dumps(get_classes("best_vehicle_model.pt"), indent=2))
