import cv2
import time
from ultralytics import YOLO
from collections import Counter, deque
import config

class TrafficDetector:
    def __init__(self, model_path=config.MODEL_PATH):
        """Initialize the detector with a YOLO model."""
        print(f"Loading model: {model_path}...")
        self.model = YOLO(model_path)
        self.vehicle_classes = config.VEHICLE_CLASSES
        self.smoothing_window = deque(maxlen=config.SMOOTHING_WINDOW_SIZE)

    def detect_vehicles(self, frame):
        """Run detection on a single frame and return results."""
        results = self.model(frame, 
                             conf=config.CONFIDENCE_THRESHOLD, 
                             imgsz=config.IMAGE_SIZE, 
                             verbose=False)
        
        boxes = results[0].boxes
        classes = boxes.cls.tolist()
        coords = boxes.xyxy.tolist() # Get bounding box coordinates
        names = self.model.names
        
        detected_vehicles = []
        vehicle_boxes = []
        
        for i, cls_idx in enumerate(classes):
            name = names[int(cls_idx)]
            if name in self.vehicle_classes:
                detected_vehicles.append(name)
                vehicle_boxes.append(coords[i])
                
        return detected_vehicles, vehicle_boxes

    def get_smoothed_count(self, current_count):
        """Calculate moving average of vehicle counts to reduce flicker."""
        self.smoothing_window.append(current_count)
        return int(sum(self.smoothing_window) / len(self.smoothing_window))

    def calculate_green_time(self, total_vehicles):
        """Determine green light duration based on vehicle density."""
        timings = config.TRAFFIC_TIMINGS
        if total_vehicles < timings["low_density"]["threshold"]:
            return timings["low_density"]["green_time"]
        elif total_vehicles < timings["medium_density"]["threshold"]:
            return timings["medium_density"]["green_time"]
        else:
            return timings["high_density"]["green_time"]

    def annotate_frame(self, frame, counts, total, green_time, vehicle_boxes=None, fps=None):
        """Draw detections and info on the frame."""
        # Draw Bounding Boxes
        if config.SHOW_BOXES and vehicle_boxes:
            for box in vehicle_boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), config.BOX_COLOR, config.BOX_THICKNESS)

        # Draw Text Info
        y = 30
        for vehicle_type, count in counts.items():
            text = f"{vehicle_type.capitalize()}: {count}"
            cv2.putText(frame, text, (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE, config.TEXT_COLOR, config.FONT_THICKNESS)
            y += 30

        cv2.putText(frame, f"Total Vehicles: {total}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE + 0.1, config.TOTAL_TEXT_COLOR, config.FONT_THICKNESS)
        
        cv2.putText(frame, f"Rec. Green Time: {green_time}s", (10, y + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE + 0.1, config.SIGNAL_TEXT_COLOR, config.FONT_THICKNESS)
        
        if fps is not None:
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        return frame

def main():
    detector = TrafficDetector()
    source = config.INPUT_SOURCE
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"Error: Could not open source {source}.")
        return

    print("Traffic detection started. Press 'q' to quit.")
    
    frame_count = 0
    fps_deque = deque(maxlen=10)
    
    # Persistent detection results for skipped frames
    last_vehicles = []
    last_boxes = []
    last_counts = Counter()
    last_smoothed_total = 0
    last_green_time = 0

    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            if isinstance(source, str): # Loop video if it's a file
                 cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                 continue
            break

        # Only run inference on specific frames to save CPU/GPU
        if frame_count % (config.FRAME_SKIP + 1) == 0:
            last_vehicles, last_boxes = detector.detect_vehicles(frame)
            last_counts = Counter(last_vehicles)
            current_total = len(last_vehicles)
            last_smoothed_total = detector.get_smoothed_count(current_total)
            last_green_time = detector.calculate_green_time(last_smoothed_total)

        # Update FPS
        end_time = time.time()
        fps_deque.append(1.0 / (end_time - start_time))
        avg_fps = sum(fps_deque) / len(fps_deque)

        # Visualization
        frame = detector.annotate_frame(frame, last_counts, last_smoothed_total, last_green_time, last_boxes, avg_fps)
        
        cv2.imshow("Smart Traffic Management - Real Time", frame)

        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()