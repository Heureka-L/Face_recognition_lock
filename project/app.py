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
from modules.SmartLock import SmartLock #继承DataBaseManager类


def main():
    app = Flask(__name__)

    # ==========================从ini文件导入数据库密码=======================
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read('config/.config.ini',encoding='utf-8')
    password = config.get('mysql','DataBase_Password') #从ini文件的mysql节中获取DataBase_Password的值
    # ====================================================================
 
    # 尝试使用IP摄像头，如果失败则使用本地摄像头
    cam_source = r'http://192.168.1.1:8080/?action=stream' # IP摄像头
    samrt_lock = SmartLock(cam_source,password) # 用本地摄像头
    if not samrt_lock.video_status:
        print('初始化失败 程序终止')
        exit()

    # ==========================FLASK SERVER=======================
    @app.route("/run")
    def index():
        render_template('index.html')
         
    @app.route("/manage")
    def manager():
        pass
    
    app.run(host='0.0.0.0',port=8888, debug=True)
if __name__ == '__main__':
    main()
