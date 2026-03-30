import os

# Project Root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Model Configuration
MODEL_PATH = os.path.join(PROJECT_ROOT, "yolov8m (1).pt")
CONFIDENCE_THRESHOLD = 0.2  # Lowered to capture distant/partially obscured vehicles
IMAGE_SIZE = 1024           # Increased from 640 to capture more detail in the distance

# Vehicle Detection Configuration
VEHICLE_CLASSES = ["car", "truck", "bus", "motorcycle", "bicycle"]
FRAME_SKIP = 2  # Process every 2nd frame for better real-time display speed
INPUT_SOURCE = 0 # 0 for webcam, or "path/to/video.mp4" for files
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "processed_results") # Where to save results
BATCH_DIR = os.path.join(PROJECT_ROOT, "uploads") # Directory to process multiple files

# Traffic Signal Configuration
SMOOTHING_WINDOW_SIZE = 5  # Number of frames for moving average
TRAFFIC_TIMINGS = {
    "low_density": {"threshold": 10, "green_time": 20},
    "medium_density": {"threshold": 25, "green_time": 40},
    "high_density": {"green_time": 60}
}

# Display Configuration
SHOW_BOXES = True
BOX_COLOR = (0, 165, 255) # Orange
BOX_THICKNESS = 1
FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
FONT_THICKNESS = 2
TEXT_COLOR = (0, 255, 0)
TOTAL_TEXT_COLOR = (255, 0, 0)
SIGNAL_TEXT_COLOR = (0, 0, 255)
