from fastapi import FastAPI, HTTPException, Query 
from pydantic import BaseModel
from ultralytics import YOLO
import cv2
import dlib
import numpy as np
import time
from scipy.spatial import distance as dist
from main import app


model_path = "./yolov8n.pt"
yolo_model = YOLO(model_path) 

# 定义眼部/嘴部关键点索引
(lStart, lEnd) = (42, 48)
(rStart, rEnd) = (36, 42)
(mStart, mEnd) = (48, 68)

# 定义计算长宽比的函数
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def mouth_aspect_ratio(mouth):
    A = np.linalg.norm(mouth[2] - mouth[10])
    B = np.linalg.norm(mouth[4] - mouth[8])
    C = np.linalg.norm(mouth[0] - mouth[6])
    mar = (A + B) / (2.0 * C)
    return mar

# 初始化参数
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 15
MAR_THRESH = 0.8
DROWSY_THRESH = 0.3

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")

@app.get("/analyzeVideo")  
def analyze_video(video_path: str):  
    d1 = d2 = d3 = d4 = 0
    distract_count = all_count = COUNTER = 0
    cap = cv2.VideoCapture(video_path)  
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="无法打开视频文件")

    start = time.time()
    while True:
        ret, frame = cap.read()
        all_count += 1
        if not ret:
            break

        results = yolo_model(frame,verbose=False)
        if len(results[0].boxes) == 0:
            distract_count += 1
            d1 += 1
            continue

        box = sorted(results[0].boxes, key=lambda x: x.conf, reverse=True)[0]
        if box.conf.item() > 0.5 and box.cls.item() == 0:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            person_roi = frame[y1:y2, x1:x2]
            if person_roi.size == 0:
                continue

            gray = cv2.cvtColor(person_roi, cv2.COLOR_BGR2GRAY)
            faces = detector(gray, 1)
            if len(faces) == 0:
                distract_count += 1
                d2 += 1
                continue

            for face in faces:
                shape = predictor(gray, face)
                shape = np.array([(x1 + shape.part(n).x, y1 + shape.part(n).y) for n in range(shape.num_parts)])
                left_eye = shape[lStart:lEnd]
                right_eye = shape[rStart:rEnd]
                mouth = shape[mStart:mEnd]

                eye = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
                mar = mouth_aspect_ratio(mouth)

                if eye < EYE_AR_THRESH:
                    COUNTER += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        distract_count += 1
                        d3 += 1
                else:
                    COUNTER = 0

                if mar > MAR_THRESH:
                    distract_count += 1
                    d4 += 1

    cap.release()
    end = time.time()
    distract = distract_count / all_count if all_count > 0 else 0

    return {
        "time_consumed": f"{end - start:.2f}秒",
        "person_not_present": d1,
        "head_down": d2,
        "drowsy": d3,
        "yawning": d4,
        "total_frames": all_count,
        "distraction_ratio": f"{distract:.4f}"
    }


if __name__ == "__main__":
    analyze_video("./test.mp4")