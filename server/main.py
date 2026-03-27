import sys
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil
import cv2
import numpy as np
from collections import Counter

# Add parent directory to path to import TrafficDetector and config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detect import TrafficDetector
import config

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Detector
detector = TrafficDetector()

# Static files for results
UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

app.mount("/results", StaticFiles(directory=RESULT_DIR), name="results")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext in ('.jpg', '.jpeg', '.png'):
        frame = cv2.imread(file_path)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        vehicles, boxes = detector.detect_vehicles(frame)
        counts = Counter(vehicles)
        total = len(vehicles)
        green_time = detector.calculate_green_time(total)

        annotated_frame = detector.annotate_frame(frame.copy(), counts, total, green_time, boxes)
        
        result_filename = f"result_{file.filename}"
        result_path = os.path.join(RESULT_DIR, result_filename)
        cv2.imwrite(result_path, annotated_frame)

        return {
            "filename": file.filename,
            "result_url": f"/results/{result_filename}",
            "total_vehicles": total,
            "breakdown": counts,
            "recommended_green_time": green_time
        }
    
    elif ext in ('.mp4', '.avi', '.mov'):
        # For videos, we'll process the first frame as a preview and return metadata
        # In a real app, you'd process the whole video in the background
        cap = cv2.VideoCapture(file_path)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=400, detail="Could not read video file")

        vehicles, boxes = detector.detect_vehicles(frame)
        counts = Counter(vehicles)
        total = len(vehicles)
        green_time = detector.calculate_green_time(total)
        
        preview_filename = f"preview_{os.path.splitext(file.filename)[0]}.jpg"
        preview_path = os.path.join(RESULT_DIR, preview_filename)
        cv2.imwrite(preview_path, frame)

        return {
            "filename": file.filename,
            "preview_url": f"/results/{preview_filename}",
            "total_vehicles": total,
            "breakdown": counts,
            "recommended_green_time": green_time,
            "message": "Video uploaded. Analysis based on first frame."
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
