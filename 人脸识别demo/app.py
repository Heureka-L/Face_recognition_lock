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
import threading
import configparser # 配置文件解析库
from modules.FaceRecognitionSystem import FaceRecognitionSystem

def main():
    app = Flask(__name__)

    # ==========================从ini文件导入数据库密码=======================
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read('config/.config.ini',encoding='utf-8')
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
            recognition_thread = threading.Thread(target=face_rec_sys.face_recognition) # 在单独线程中运行
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
        
        # 设置注册状态5
        face_rec_sys.is_register = True
        face_rec_sys.register_nane = name.strip()
        
        return jsonify({"success": True, "message": f"正在注册 {name} 的人脸信息..."})
    
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
