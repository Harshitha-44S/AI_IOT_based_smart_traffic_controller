import os
import cv2
import time
from collections import Counter
from detect import TrafficDetector
import config

def process_image(detector, image_path, output_dir):
    """Detect vehicles in an image and save the result."""
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not read image {image_path}")
        return None

    vehicles, boxes = detector.detect_vehicles(frame)
    counts = Counter(vehicles)
    total = len(vehicles)
    
    # Annotate without FPS (static image)
    annotated_frame = detector.annotate_frame(frame.copy(), counts, total, 
                                            detector.calculate_green_time(total), 
                                            boxes)
    
    # Save output
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    save_path = os.path.join(output_dir, f"annotated_{filename}")
    cv2.imwrite(save_path, annotated_frame)
    
    return counts, total

def process_video(detector, video_path, output_dir):
    """Detect vehicles in a video and save the result."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(video_path)
    save_path = os.path.join(output_dir, f"processed_{filename}")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    print(f"Processing video: {filename}...")
    
    total_vehicles_per_frame = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        vehicles, boxes = detector.detect_vehicles(frame)
        counts = Counter(vehicles)
        total = len(vehicles)
        total_vehicles_per_frame.append(total)
        
        annotated_frame = detector.annotate_frame(frame, counts, total, 
                                                detector.calculate_green_time(total), 
                                                boxes)
        out.write(annotated_frame)

    cap.release()
    out.release()
    
    avg_count = sum(total_vehicles_per_frame) / len(total_vehicles_per_frame) if total_vehicles_per_frame else 0
    return Counter({"average": int(avg_count)}), int(avg_count)

def main():
    detector = TrafficDetector()
    
    # Check if BATCH_DIR exists, if not use current dir's images
    target_dir = config.BATCH_DIR
    if not os.path.exists(target_dir):
        print(f"Directory {target_dir} not found. Processing images in current directory...")
        target_dir = "."

    extensions = ('.jpg', '.jpeg', '.png', '.mp4', '.avi', '.mov')
    files = [f for f in os.listdir(target_dir) if f.lower().endswith(extensions)]
    
    if not files:
        print("No image or video files found to process.")
        return

    print(f"\n{'File Name':<30} | {'Total Vehicles':<15} | {'Vehicle Breakdown'}")
    print("-" * 80)

    for file in files:
        file_path = os.path.join(target_dir, file)
        ext = os.path.splitext(file)[1].lower()
        
        if ext in ('.jpg', '.jpeg', '.png'):
            result = process_image(detector, file_path, config.OUTPUT_DIR)
        else:
            result = process_video(detector, file_path, config.OUTPUT_DIR)
            
        if result:
            counts, total = result
            breakdown = ", ".join([f"{k}: {v}" for k, v in counts.items()])
            print(f"{file:<30} | {total:<15} | {breakdown}")

    print("-" * 80)
    print(f"Results saved in: {os.path.abspath(config.OUTPUT_DIR)}")

if __name__ == "__main__":
    main()
