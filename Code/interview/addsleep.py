from ultralytics import YOLO
import cv2
import dlib
import numpy as np
import time
from scipy.spatial import distance as dist

# 初始化YOLOv8模型
yolo_model = YOLO("yolov8n.pt")  

# 定义眼部/嘴部关键点索引
(lStart, lEnd) = (42, 48)
(rStart, rEnd) = (36, 42)
(mStart, mEnd) = (48, 68)

# 定义计算长宽比的函数
def eye_aspect_ratio(eye):
    # 垂直眼标志（X，Y）坐标
    A = dist.euclidean(eye[1], eye[5])  # 计算两个集合之间的欧式距离
    B = dist.euclidean(eye[2], eye[4])
    # 计算水平之间的欧几里得距离
    # 水平眼标志（X，Y）坐标
    C = dist.euclidean(eye[0], eye[3])
    # 眼睛长宽比的计算
    ear = (A + B) / (2.0 * C)
    # 返回眼睛的长宽比
    # print(ear)
    return ear

def mouth_aspect_ratio(mouth):  # 嘴部
    A = np.linalg.norm(mouth[2] - mouth[10])  # 51, 59
    B = np.linalg.norm(mouth[4] - mouth[8])  # 53, 57
    C = np.linalg.norm(mouth[0] - mouth[6])  # 49, 55
    mar = (A + B) / (2.0 * C)
    return mar

# 初始化参数
EYE_AR_THRESH = 0.25  # 低于此值视为闭眼
EYE_AR_CONSEC_FRAMES = 15  # 连续闭眼帧数阈值
MAR_THRESH = 0.8  # 高于此值视为打哈欠
DROWSY_THRESH = 0.3  # 低于此值视为打瞌睡
video_path = "./data/b.mp4"  # 请将b.mp4放在ZjuProject/data/目录下
d1=0
d2=0
d3=0
d4=0
# 初始化计数器
distract_count = 0
all_count=0
COUNTER = 0

SCORE = 100
# 加载dlib模型
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# 初始化摄像头
cap = cv2.VideoCapture(video_path)
print("开始分析")
start = time.time()
while True:

    ret, frame = cap.read()
    all_count+=1
    if not ret:
        break

    # YOLO人物检测
    results = yolo_model(frame,verbose=False)# cuda
    if len(results[0].boxes)==0:
        distract_count+=1
        d1+=1
        continue
    # 遍历所有检测到的人物
    box = sorted(results[0].boxes,key=lambda x:x.conf,reverse=True)[0]
    if box.conf.item() > 0.5 and box.cls.item() == 0:  # 置信度>50%且类别为人
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # 绘制人物框
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 裁剪人物区域
            person_roi = frame[y1:y2, x1:x2]
            if person_roi.size == 0:
                continue  # 跳过空区域

            # 在人物区域内进行人脸检测
            gray = cv2.cvtColor(person_roi, cv2.COLOR_BGR2GRAY)
            faces = detector(gray, 1)
            if len(faces)==0:
                distract_count+=1
                d2+=1
                continue
            for face in faces:
                # 获取面部关键点
                shape = predictor(gray, face)
                shape = np.array([(x1 + shape.part(n).x, y1 + shape.part(n).y)
                                  for n in range(shape.num_parts)])

                # 提取眼部嘴部特征
                left_eye = shape[lStart:lEnd]
                right_eye = shape[rStart:rEnd]
                mouth = shape[mStart:mEnd]

                # 计算特征比率
                eye = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
                mar = mouth_aspect_ratio(mouth)

                # 绘制特征轮廓
                # cv2.drawContours(frame, [cv2.convexHull(left_eye)], -1, (0, 255, 0), 1)
                # cv2.drawContours(frame, [cv2.convexHull(right_eye)], -1, (0, 255, 0), 1)
                # cv2.drawContours(frame, [cv2.convexHull(mouth)], -1, (0, 255, 0), 1)

                # 疲劳检测逻辑
                if eye < EYE_AR_THRESH:
                    COUNTER += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        distract_count += 1
                        d3+=1
                        # cv2.putText(frame, "DROWSINESS ALERT!", (x1, y1 - 30),
                        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    COUNTER = 0

                # 哈欠检测
                if mar > MAR_THRESH:
                    distract_count += 1
                    d4+=1
                    # cv2.putText(frame, "YAWN DETECTED!", (x1, y1 - 60),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


                # 显示实时数据
                # cv2.putText(frame, f"EAR: {eye:.2f}", (x1, y1 - 120),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                # cv2.putText(frame, f"MAR: {mar:.2f}", (x1, y1 - 150),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
    # 显示帧率
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    # cv2.imshow("Driver Monitoring", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
distract = distract_count/all_count
end = time.time()
print("耗时%.2f秒" % (end - start))
print("分析结束")
print("人不在",d1)
print("低头",d2)
print("打瞌睡",d3)
print("打哈欠",d4)
print("总帧数",all_count)
print("不专心的时间占比为%.4f" % distract)
cap.release()
cv2.destroyAllWindows()