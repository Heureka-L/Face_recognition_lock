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
from flask import Flask, render_template, Response, jsonify, request, session, redirect
import configparser # 配置文件解析库
import sys
from modules.SmartLock import SmartLock
import uuid


def main():
    app = Flask(__name__)
    # 添加secret_key以支持session
    app.secret_key = str(uuid.uuid4()) # 随机密钥

    # ==========================从ini文件导入配置=======================
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read('config/.config.ini',encoding='utf-8')
    ip_camera_url = config.get('camera', 'IP_Camera_URL', fallback='')  # 从ini文件的camera节中获取IP_Camera_URL的值
    # ====================================================================

    # 尝试使用IP摄像头，如果失败则使用本地摄像头
    video_sources = []
    if ip_camera_url:  # 如果配置了IP摄像头URL，则添加到视频源列表
        video_sources.append(ip_camera_url)  # IP摄像头
    video_sources.extend([0])  # 本地摄像头
    face_rec_sys = None
    for source in video_sources:
        face_rec_sys = SmartLock(source)
        if face_rec_sys.video_status:
            print(f"视频源 {source} 初始化成功")
            break
        else:
            print(f"视频源 {source} 初始化失败")
    if not face_rec_sys or not face_rec_sys.video_status:
        print("所有视频源都初始化失败，程序退出")
        exit()
    
    # 启动智能锁服务
    face_rec_sys.run_server()

    # ==========================FLASK SERVER=======================
    # 主页
    @app.route("/run",methods = ["GET","POST"])
    def index():
        if request.method == "GET":
            return render_template('run.html')
    
    # 视频流
    @app.route('/video_feed')
    def video_feed():
        return Response(face_rec_sys.generate_frame(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    
    # 注册
    @app.route("/login",methods = ["GET","POST"])
    def login():
        if request.method == "GET":
            return render_template('login.html')
        else:
            username = request.form['username']
            password = request.form['password']
            # 验证管理员账户
            user = face_rec_sys.fetch_one(
                "SELECT * FROM admin_users WHERE username=? AND password=?",
                (username, password)
            )
            if user:
                # 设置认证状态
                session['authenticated'] = True
                return redirect('/entered')
            else:
                # 返回错误信息
                return render_template('login.html', error="账号或密码错误")
            
    # 预览图像
    @app.route('/preview_image')
    def preview_image():
        # 获取当前帧用于预览
        frame_bytes = face_rec_sys.get_current_frame_for_preview()
        if frame_bytes:
            return Response(frame_bytes, mimetype='image/jpeg')
        else:
            # 返回一个默认图像或错误
            return "", 404
    
    # 人脸录入
    @app.route("/entered", methods=["GET", "POST"])
    def entered():
        # 检查用户是否已通过身份认证
        if not session.get('authenticated'):
            # 未通过认证，重定向到登录页面
            return redirect('/login')
        
        if request.method == "GET":
            return render_template('entered.html')
        else:
            action = request.form.get('action')
            username = request.form.get('username', '')
            
            if action == 'start':
                # 设置注册标志位
                face_rec_sys.is_register = True
                return render_template('entered.html', registering=True, username=username)
            elif action == 'confirm':
                # 检查是否有人脸待注册
                if face_rec_sys.register_face_encoding is not None:
                    # 调用注册方法
                    face_rec_sys.register_new_face(username)
                    # 重置注册状态
                    face_rec_sys.is_register = False
                    # 清除身份认证状态
                    session['authenticated'] = False
                    return redirect('/run')
                else:
                    return render_template('entered.html', error="未检测到有效人脸数据", username=username)
            elif action == 'restart':
                # 重新开始录入
                face_rec_sys.is_register = True
                face_rec_sys.register_face_encoding = None
                return render_template('entered.html', registering=True, username=username)
                
    app.run(host='0.0.0.0',port=8888, debug=True)
if __name__ == '__main__':
    main()
