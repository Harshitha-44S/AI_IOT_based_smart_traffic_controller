from detect import TrafficDetector
import cv2
import os

def test_detector():
    detector = TrafficDetector()
    test_images = ["download (1).jpg", "test.jpg"]
    
    for img_path in test_images:
        print(f"\nVerifying: {img_path}")
        if not os.path.exists(img_path):
            print(f"File {img_path} not found, skipping...")
            continue
            
        frame = cv2.imread(img_path)
        vehicles, vehicle_boxes = detector.detect_vehicles(frame)
        count = len(vehicles)
        
        # Test smoothing
        smoothed = detector.get_smoothed_count(count)
        green_time = detector.calculate_green_time(smoothed)
        
        print(f"  Detected: {count}")
        print(f"  Smoothed: {smoothed}")
        print(f"  Green Time: {green_time}s")
        
        # Basic sanity checks
        if count == 0:
            print(f"  WARNING: No vehicles detected in {img_path}. This might be an issue with model or image.")
        else:
            print(f"  PASS: Detection working for {img_path}")

if __name__ == "__main__":
    test_detector()
