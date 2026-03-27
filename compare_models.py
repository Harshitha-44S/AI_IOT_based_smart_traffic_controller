from ultralytics import YOLO
import os

models = ["yolov8m (1).pt", "yolov8n.pt", "best_vehicle_model.pt"]
test_images = ["download (1).jpg", "download (2).jpg", "download.jpg", "images.jpg", "test.jpg"]

for model_path in models:
    print(f"\n--- Testing Model: {model_path} ---")
    try:
        model = YOLO(model_path)
        for img_path in test_images:
            if os.path.exists(img_path):
                results = model(img_path, conf=0.25, imgsz=640, verbose=False)
                # Filter for vehicle classes if it's the standard YOLO model
                # or just count all if it's a specialized vehicle model
                classes = results[0].boxes.cls.tolist()
                names = model.names
                detected_names = [names[int(cls)] for cls in classes]
                
                # Standard vehicle classes for YOLOv8
                vehicle_classes = ["car", "truck", "bus", "motorcycle", "bicycle"]
                filtered = [cls for cls in detected_names if cls in vehicle_classes or model_path == "best_vehicle_model.pt"]
                
                print(f"Image: {img_path} | Detected vehicles: {len(filtered)} | Details: {filtered}")
            else:
                print(f"Image not found: {img_path}")
    except Exception as e:
        print(f"Error loading model {model_path}: {e}")
