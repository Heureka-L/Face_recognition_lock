#
#                   _ooOoo_
#                  o8888888o
#                  88" . "88
#                  (| -_- |)
#                  O\ = /O
#               ____/`---'\____
#             .' \\| |// `
#            / \\||| : |||// \
#           / _||||| -:- |||||- \
#           | | \\\ - /// | |
#           | \_| ''\---/'' | |
#           \ .-\__ `-` ___/-. /
#         ___`. .' /--.--\ `. . __
#      ."" '< `.___\_<|>_/___.' >'""
#     | | : `- \`.;`\ _ /`;.`/ - ` : | |
#     \ \ `-. \_ __\ /__ _/ .-` / /
# ======`-.____`-.___\_____/___.-`____.-'======
#                   `=---='
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#            佛祖保佑 永无BUG
#
from flask import Flask, render_template, Response, jsonify, request
import cv2
import face_recognition as face_rec
import numpy as np
import threading
from datetime import datetime
import json
import pymysql
import configparser # 配置文件解析库
from pymysql import Error

class DataBaseManager:
    def __init__(self, password):
        self.DB_CONFIG = {
            "host": "localhost",
            "user": "root",
            "passwd": password,
            "charset": "utf8mb4",
            "port": 3306,
            "database": "face_recognition_db",
            "autocommit": True  # 自动提交事务
        }
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            return pymysql.connect(**self.DB_CONFIG)
        except Error as e:
            print(f"数据库连接错误: {e}")
            raise

    # 以字典形式返回所有查询结果
    def fetch_all(self, sql, args=None):
        connection = self._get_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except Error as e:
            print(f"查询错误: {e}")
            return []
        finally:
            connection.close()

    # 以字典形式返回一条查询结果
    def fetch_one(self, sql, args=None):
        connection = self._get_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                result = cursor.fetchone()
                return result
        except Error as e:
            print(f"查询错误: {e}")
            return None
        finally:
            connection.close()
    
    # 插入数据
    def insert_data(self, sql, args=None):
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                connection.commit()
                return cursor.lastrowid  # 返回插入的ID
        except Error as e:
            connection.rollback()
            print(f"插入数据错误: {e}")
            return None
        finally:
            connection.close()

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
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(self.frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if self.frame is None:
                continue
            rgb_frame = cv2.cvtColor(self.frame,cv2.COLOR_BGR2RGB)
            rgb_small_frame =  cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_rec.face_locations(rgb_small_frame)
            
            if len(face_locations) == 1:
                self.sys_msg = "检测到人脸"
                face_encodings = face_rec.face_encodings(rgb_small_frame,face_locations,model='shape_predictor_68_face_landmarks.dat',num_jitters=5)
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
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(self.frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
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
def main():
    app = Flask(__name__)

    # ==========================从ini文件导入数据库密码=======================
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read('.config.ini',encoding='utf-8')
    password = config.get('mysql','DataBase_Password') #从ini文件的mysql节中获取DataBase_Password的值
    # ====================================================================
    # 尝试使用IP摄像头，如果失败则使用本地摄像头
    video_sources = [
        r'http://192.168.1.1:8080/?action=stream',  # IP摄像头
        0,  # 本地摄像头
        r'sources/Mediastorm_TIM.mp4'  # 备用测试视频文件
    ]

    face_rec_sys = None
    for source in video_sources:
        face_rec_sys = FaceRecognitionSystem(source,password) # 用本地摄像头
        if face_rec_sys.video_status:
            print(f"视频源 {source} 初始化成功")
            break
        else:
            print(f"视频源 {source} 初始化失败")

    if not face_rec_sys or not face_rec_sys.video_status:
        print("所有视频源都初始化失败，程序退出")
        exit()
    
        print("视频流状态：" + str(face_rec_sys.video_status))
    
    # 主页
    @app.route('/')
    def index():
        return render_template("index.html")
    
    @app.route('/video_feed')
    def video_feed():
        """视频流路由"""
        return Response(face_rec_sys.generate_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/start_recognition', methods=['POST'])
    def start_recognition():
        """启动人脸识别"""
        if not face_rec_sys.is_running:
            face_rec_sys.is_running = True
            recognition_thread = threading.Thread(target=face_rec_sys.face_recognition)
            recognition_thread.daemon = True
            recognition_thread.start()
            return jsonify({"success": True, "message": "人脸识别已启动"})
        else:
            return jsonify({"success": False, "message": "人脸识别已在运行中"})
    
    @app.route('/stop_recognition', methods=['POST'])
    def stop_recognition():
        """停止人脸识别"""
        if face_rec_sys.is_running:
            face_rec_sys.is_running = False
            return jsonify({"success": True, "message": "人脸识别已停止"})
        else:
            return jsonify({"success": False, "message": "人脸识别未在运行"})
    
    @app.route('/register_new_face', methods=['POST'])
    def register_new_face():
        """注册新人脸"""
        data = request.get_json()
        name = data.get('name', 'unknown')
        
        if not name or name.strip() == '':
            return jsonify({"success": False, "message": "姓名不能为空"})
        
        # 设置注册状态
        face_rec_sys.is_register = True
        face_rec_sys.register_nane = name.strip()
        
        return jsonify({"success": True, "message": f"请面向摄像头，正在注册 {name} 的人脸信息..."})
    
    @app.route('/get_status', methods=['GET'])
    def get_status():
        """获取系统状态"""
        return jsonify({
            "is_running": face_rec_sys.is_running,
            "known_faces_count": len(face_rec_sys.Known_faces),
            "sys_msg": face_rec_sys.sys_msg or "系统就绪",
            "is_register": face_rec_sys.is_register,
            "register_name": face_rec_sys.register_nane
        })

    app.run(host='0.0.0.0',port=8888, debug=True)
if __name__ == '__main__':
    main()
