import numpy as np

import cv2
import json
import face_recognition as face_rec
from PIL import Image, ImageDraw, ImageFont
import datetime
import threading
# 导入自建模块
from modules.FaceRecognitionDB import DataBaseManager
import time
import queue

class SmartLock(DataBaseManager): #继承DataBaseManager类
    def __init__(self,video_path,db_path=None):
        # 初始化数据库管理器
        super().__init__(db_path)  #初始化DataBaseManager类的属性
        self.video_cap = cv2.VideoCapture(video_path)
        self.video_status = self.video_cap.isOpened() #检测视频流是否正常打开
        self.is_running = False # 人脸识别是否正在运行
        self.Known_faces = [] #从数据库中加载所有已知人脸
        self.names = [] #从数据库中加载的所有人脸对应的姓名 ------保证与人脸编码的下标一致
        self.frame = None #视频数据帧
        self.show_frame = self.frame #用于生成HTTP数据流（用于显示）的视频数据帧       
        self.sys_msg = None #系统提示信息
        self.current_face_exist = None #当前识别到的人脸是否存在于数据库中
        self.is_register = False # 是否在进行人脸注册
        self.register_face_encoding = None # 正在进行注册的人脸编码
        self.capture_preview_request = False # 标记是否需要捕获预览图像
        self.lock_open_time = None # 记录开锁时间
        self.auto_close_lock_thread = None # 自动关锁线程
        self.open_lock = False # 初始化锁状态为关闭
        # 添加线程锁
        self.frame_lock = threading.Lock()
        self.show_frame_lock = threading.Lock()
        self.face_exist_lock = threading.Lock()
        self.register_lock = threading.Lock()
        self.register_encoding_lock = threading.Lock()
        self.sys_msg_lock = threading.Lock()
        self.capture_preview_lock = threading.Lock()
        self.lock_state_lock = threading.Lock()
        self.load_known_faces()
        self.font = None   #用于中文绘制的字体     
         # 尝试加载中文字体
        try:
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",      # 黑体
                "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
                "C:/Windows/Fonts/simsun.ttc",      # 宋体
                "simhei.ttf",                       # 当前目录
                "msyh.ttc",                         # 当前目录
            ]

            for font_path in font_paths:
                try:
                    self.font = ImageFont.truetype(font_path, 20)  # 字体大小20
                    break
                except:
                    continue
                                
            if self.font is None:
                # 如果找不到字体，使用默认字体（可能不支持中文）
                self.font = ImageFont.load_default()
        except:
            self.font = ImageFont.load_default()

    # 从视频流中获取一帧
    def _get_frame(self):
        while self.video_status:
            ret, frame = self.video_cap.read()
            if ret:
                # 添加时间戳
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                with self.frame_lock:
                    self.frame = frame
                # 检查是否有预览捕获请求
                with self.capture_preview_lock:
                    if self.capture_preview_request:
                        # 保存当前帧用于预览
                        _, buffer = cv2.imencode('.jpg', frame)
                        self.preview_frame_bytes = buffer.tobytes()
                        self.capture_preview_request = False  # 重置请求标志

    # 从数据库中加载所有已知人脸    
    def load_known_faces(self):
        try:
            data = self.fetch_all("SELECT username, face_encoding FROM face_features")
            if data is not None: 
                for face_data in data:
                    username = face_data.get("username", "unknown")
                    face_encoding_data = json.loads(face_data.get("face_encoding", "{}"))
                    if face_encoding_data:
                        self.names.append(username) #添加姓名
                        encoding = np.array(face_encoding_data)
                        if len(encoding) > 0:
                            self.Known_faces.append(encoding)
            print("======人脸加载完成======")
        except Exception as e:
            print(f"======从数据库加载人脸失败: {e}======")
            exit()
        
    # 注册新人脸并储存到数据库
    def register_new_face(self,username):
        with self.sys_msg_lock:
            self.sys_msg = "请面向屏幕后点击开始录入"
        with self.register_encoding_lock:
            face_encoding_list = self.register_face_encoding.tolist() # 转化为可储存在JSON中的列表
        sql = "INSERT INTO face_features (username, face_encoding) VALUES (?, ?)"
        result = self.insert_data(sql,(username, json.dumps(face_encoding_list)))
        
        if result:
            print(f"人脸注册成功: {username}")
            # 重新加载人脸数据
            self.Known_faces = []
            self.names = []
            self.load_known_faces()
        else:
            print(f"人脸注册失败: {username}")
        
        with self.register_lock:
            self.is_register = False 
        with self.register_encoding_lock:
            self.register_face_encoding = None # 重置待注册的人脸编码
                                                                                                                                
    # 人脸识别
    def _face_recognition(self):
        if len(self.Known_faces) > 0:
            exist_known_face = True
        else:
            exist_known_face = False
        while self.is_running: 
            time1 = time.time()
            time2 = time.time()
            frame_copy = None
            with self.frame_lock:
                if self.frame is None:
                    continue
                frame_copy = self.frame.copy()
            rgb_frame = cv2.cvtColor(frame_copy,cv2.COLOR_BGR2RGB)
            rgb_small_frame =  cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_rec.face_locations(rgb_small_frame,model="cnn")
            if len(face_locations) == 1:
                with self.sys_msg_lock:
                    self.sys_msg = "检测到人脸"
                face_encodings = face_rec.face_encodings(rgb_small_frame,face_locations,model='shape_predictor_68_face_landmarks.dat',num_jitters=1)
                with self.face_exist_lock:
                    self.current_face_exist = False
                if len(face_encodings) != 1: #确保只有一个人脸编码
                    with self.sys_msg_lock:
                        self.sys_msg = "检测到多个人脸"
                    continue
                for face_encoding in face_encodings:
                    with self.register_lock:
                        is_register = self.is_register
                    if is_register:
                        with self.register_encoding_lock:
                            self.register_face_encoding = face_encoding  #持续更新待注册的人脸编码
                        continue
                    name = "unknown"
                    
                    if exist_known_face:
                        # 与已知人脸进行对比，返回一个布尔值列表 eg: face_matches = [True,False,False,False,True] 有匹配的人脸为1，否则为0
                        face_matches = face_rec.compare_faces(self.Known_faces,face_encoding,tolerance=0.35)
                        if True in face_matches: #如果有匹配的结果
                            matches = []
                            real_match_name_index = []
                            for i,match in enumerate(face_matches): #筛选出匹配编码，减少计算
                                if match:
                                    matches.append(self.Known_faces[i])
                                    real_match_name_index.append(i)

                            face_distances = face_rec.face_distance(matches,face_encoding) #计算欧氏距，欧式距越小匹配度越高
                            # face_distances = face_rec.face_distance(self.Known_faces,face_encoding) #计算欧氏距，欧式距越小匹配度越高
                            min_face_distances = min(face_distances)
                            if min_face_distances > 0.35:
                                name = "unknown"
                                with self.face_exist_lock:
                                    self.current_face_exist = False
                            else:
                                virtual_match_face_index = np.argmin(face_distances) #求最小值的索引
                                name = self.names[real_match_name_index[virtual_match_face_index]]
                                # name = self.names[virtual_match_face_index]
                                with self.face_exist_lock:
                                    self.current_face_exist = True
                        else:
                            name = "unknown"
                            with self.face_exist_lock:
                                self.current_face_exist = False
                    
                    
                    # 绘制识别结果
                    for (top, right, bottom, left) in face_locations:
                        # 缩放回原始尺寸
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        # 绘制人脸框
                        cv2.rectangle(frame_copy, (left, top), (right, bottom), (0, 255, 0), 2)                        
                        # 绘制姓名标签
                        cv2.rectangle(frame_copy, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        # 使用PIL绘制中文文本
                        # 将OpenCV的BGR图像转换为PIL的RGB图像
                        pil_image = Image.fromarray(cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB))
                        draw = ImageDraw.Draw(pil_image)
                        # 绘制中文文本
                        text_position = (left + 6, bottom - 30)  # 调整位置以适应中文
                        draw.text(text_position, name, font=self.font, fill=(255, 255, 255))
                        # 转换回OpenCV格式
                        frame_copy = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                        
            elif len(face_locations) == 0:
                with self.sys_msg_lock:
                    self.sys_msg = "未检测到人脸"
            else:
                with self.sys_msg_lock:
                    self.sys_msg = "请确保屏幕中仅存在一张人脸" 
            with self.show_frame_lock:
                self.show_frame = frame_copy

    #开启智能锁服务
    def run_server(self):
        self.is_running = True # 开启服务
        threading.Thread(target=self._get_frame).start() #画面刷新
        threading.Thread(target=self._face_recognition).start() # 开启人脸识别线程
        self.init_lock() # 初始化时先关锁
        threading.Thread(target=self.lock_control).start() # 开启锁控制线程

    # 生成 HTTP 数据帧
    def generate_frame(self):
        while True:
            time.sleep(0.05)
            show_frame_copy = None
            with self.show_frame_lock:
                if self.show_frame is not None:
                    show_frame_copy = self.show_frame.copy()
            if show_frame_copy is not None:
                cv2.imshow("FRAME",show_frame_copy)
                cv2.waitKey(1)
                # 编码为JPEG
                _, buffer = cv2.imencode('.jpg', show_frame_copy)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
    
    #开锁
    def _open_lock(self):
        self.open_lock = True
        frame = cv2.imread('unlock.png')
        if frame is not None:
            cv2.imshow("LOCK",frame)
            cv2.waitKey(1000)
        print('lock open')

    #关锁
    def _close_lock(self):
        self.open_lock = False
        frame = cv2.imread('lock.png')
        if frame is not None:
            cv2.imshow("LOCK",frame)
            cv2.waitKey(1000)
        print('lock closed')
    # 初始化锁状态
    def init_lock(self):
        self._close_lock()
    # 获取当前帧用于预览
    def get_current_frame_for_preview(self):
        # 请求捕获一个新帧用于预览
        with self.capture_preview_lock:
            self.capture_preview_request = True
        
        # 等待一段时间以确保帧被捕获
        time.sleep(0.1)
        
        with self.capture_preview_lock:
            if hasattr(self, 'preview_frame_bytes'):
                return self.preview_frame_bytes
        return None

    # 自动关锁线程
    def auto_close_lock(self):
        time.sleep(5)  # 等待5秒
        with self.lock_state_lock:
            if self.open_lock:  # 如果锁仍然是开启状态
                self._close_lock()
                print("5秒后自动关锁")
                self.lock_open_time = None  # 重置开锁时间

    # 锁控制线程
    def lock_control(self):
        with self.face_exist_lock:
            current_face_exist = self.current_face_exist
        if current_face_exist:
            with self.lock_state_lock:
                # 如果当前是关锁状态，才执行开锁
                if not self.open_lock:
                    self._open_lock()
                    print("检测到已知人脸，开锁")
                    # 记录开锁时间
                    self.lock_open_time = time.time()
                    # 启动自动关锁线程
                    if self.auto_close_lock_thread and self.auto_close_lock_thread.is_alive():
                        # 如果已有自动关锁线程在运行，等待其完成
                        self.auto_close_lock_thread.join(timeout=0.1)
                    self.auto_close_lock_thread = threading.Thread(target=self.auto_close_lock)
                    self.auto_close_lock_thread.daemon = True
                    self.auto_close_lock_thread.start()
        else:
            with self.lock_state_lock:
                # 如果当前是开锁状态，才执行关锁
                if self.open_lock:
                    self._close_lock()
                    print("未检测到已知人脸，关锁")
                    self.lock_open_time = None  # 重置开锁时间
