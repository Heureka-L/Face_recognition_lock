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
import configparser # 配置文件解析库
from modules.SmartLock import SmartLock

def main():
    app = Flask(__name__)

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

    # ==========================FLASK SERVER=======================
    # 主页
    @app.route("/run",methods = ["GET","POST"])
    def index():
        if request.method == "GET":
            render_template('index.html')
    
    # 注册
    @app.route("/login",methods = ["GET","POST"])
    def login():
        pass
    
    # 人脸录入
    @app.route("/entered")
    def entered():
        pass
    
    app.run(host='0.0.0.0',port=8888, debug=True)
if __name__ == '__main__':
    main()
