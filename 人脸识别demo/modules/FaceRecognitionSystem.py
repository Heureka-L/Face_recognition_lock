import numpy as np
import cv2
import json
import face_recognition as face_rec
from PIL import Image, ImageDraw, ImageFont
import datetime
# 导入自建模块
from modules.FaceRecognitionDB import DataBaseManager

class FaceRecognitionSystem(DataBaseManager): #继承DataBaseManager类
    def __init__(self,video_path,password):
        # 初始化数据库管理器
        super().__init__(password)  #初始化DataBaseManager类的属性
        
        self.video_cap = cv2.VideoCapture(video_path)
        self.video_status = self.video_cap.isOpened() #检测视频流是否正常打开
        self.is_running = False # 人脸识别是否正在运行
        self.Known_faces = [] #从数据库中加载所有已知人脸
        self.names = [] #从数据库中加载的所有人脸对应的姓名 ------保证与人脸编码的下标一致
        self.frame = None #视频数据帧
        self.show_frame = self.frame #用于生成HTTP数据流（用于显示）的视频数据帧       
        self.sys_msg = None #系统提示信息
        self.is_register = False # 是否在进行人脸注册
        self.register_nane = "unknown" # 真在进行注册的姓名
        self.load_known_faces()
        self.font = None   #用于中文绘制的字体     
         # 尝试加载中文字体
        try:
            # Windows系统常见字体路径
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
                print("警告：未找到中文字体，使用默认字体")
        except:
            self.font = ImageFont.load_default()


    # 从视频流中获取一帧
    def get_frame(self):
        if self.video_status:
            ret, frame = self.video_cap.read()
            if ret:
                self.frame = frame

    # 从数据库中加载所有已知人脸    
    def load_known_faces(self):
        try:
            data = self.fetch_all("SELECT face_encoding FROM face_encodings")
            if data is not None: 
                for face_data in data:
                    face_encoding_data = json.loads(face_data.get("face_encoding", "{}"))
                    if face_encoding_data:
                        self.names.append(face_encoding_data.get("name", "unknown")) #添加姓名
                        encoding = np.array(face_encoding_data.get("encoding", []))
                        if len(encoding) > 0:
                            self.Known_faces.append(encoding)
            print("======人脸加载完成======")
        except Exception as e:
            print(f"======从数据库加载人脸失败: {e}======")
            exit()

    # 注册新人脸并储存到数据库
    def register_new_face(self,name,face_encoding):
        face_encoding_list = face_encoding.tolist() # 转化为可储存在JSON中的列表
        encoding_data = {
            "name":name,
            "encoding":face_encoding_list
        }
        sql = "INSERT INTO face_encodings (face_encoding) VALUES (%s)"
        result = self.insert_data(sql,(json.dumps(encoding_data),))
        
        if result:
            print(f"人脸注册成功: {name}")
            # 重新加载人脸数据
            self.Known_faces = []
            self.names = []
            self.load_known_faces()
        else:
            print(f"人脸注册失败: {name}")
        
        self.is_register = False 

    # 人脸识别和注册
    def face_recognition(self):
        while self.is_running: 
            self.get_frame()
            # 添加时间戳
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(self.frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if self.frame is None:
                continue
            rgb_frame = cv2.cvtColor(self.frame,cv2.COLOR_BGR2RGB)
            rgb_small_frame =  cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_rec.face_locations(rgb_small_frame)
            
            if len(face_locations) == 1:
                self.sys_msg = "检测到人脸"
                face_encodings = face_rec.face_encodings(rgb_small_frame,face_locations,model='shape_predictor_68_face_landmarks.dat',num_jitters=1)
                for face_encoding in face_encodings:
                    if self.is_register :
                        self.register_new_face(self.register_nane,face_encoding) # 注册新人脸
                        continue
                    name = "unknown"

                    if len(self.Known_faces) > 0:
                        # 与已知人脸进行对比，返回一个布尔值列表 eg: face_matches = [True,False,False,False,True] 有匹配的人脸为1，否则为0
                        face_matches = face_rec.compare_faces(self.Known_faces,face_encoding,tolerance=0.35)
                        if True in face_matches: #如果有匹配的结果
                            face_distances = face_rec.face_distance(self.Known_faces,face_encoding) #计算欧氏距，欧式距越小匹配度越高
                            min_face_distances = min(face_distances)
                            if min_face_distances > 0.35:
                                name = "unknown"
                            else:
                                match_face_index = np.argmin(face_distances) #求最小值的索引
                                name = self.names[match_face_index]
                        else:
                            name = "unknown"
                    # 绘制识别结果
                    for (top, right, bottom, left) in face_locations:
                        # 缩放回原始尺寸
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        # 绘制人脸框
                        cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 255, 0), 2)                        
                        # 绘制姓名标签
                        cv2.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        # 使用PIL绘制中文文本
                        # 将OpenCV的BGR图像转换为PIL的RGB图像
                        pil_image = Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
                        draw = ImageDraw.Draw(pil_image)
                        # 绘制中文文本
                        text_position = (left + 6, bottom - 30)  # 调整位置以适应中文
                        draw.text(text_position, name, font=self.font, fill=(255, 255, 255))
                        # 转换回OpenCV格式
                        self.frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            elif len(face_locations) == 0:
                self.sys_msg = "未检测到人脸"
            else:
                self.sys_msg = "请确保屏幕中仅存在一张人脸" 
            self.show_frame = self.frame

    # 生成 HTTP 数据帧
    def generate_frame(self):
        while True:
            if self.show_frame is not None:
                # 编码为JPEG
                _, buffer = cv2.imencode('.jpg', self.show_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')