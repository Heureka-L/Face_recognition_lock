# 本程序用于测试由Flask生成的HTTP视频流
# 请在开始人脸识别后再运行此代码
# 本代码与项目无关，可忽略
import cv2
url = 'http://127.0.0.1:8888/video_feed'
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print('open_filed')
    exit()

while cap.isOpened():
    _,frame = cap.read()

    cv2.imshow('FRAME_',frame)
    cv2.waitKey(20)