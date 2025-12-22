# 智能门锁系统开发文档

## 项目概述

本项目是一个基于人脸识别技术的智能门锁系统，使用Python和Flask框架实现。系统包含三个主要功能模块：
1. 首页 - 显示实时视频流和人脸识别结果
2. 用户注册 - 管理员账户验证
3. 人脸录入 - 新用户人脸数据采集与存储

## 系统架构

```
project/
├── app.py                 # Flask主应用
├── data_base_init.py      # 数据库初始化脚本
├── config/
│   └── .config.ini        # 配置文件（包含数据库和摄像头配置）
├── modules/
│   ├── SmartLock.py       # 智能锁核心类
│   └── FaceRecognitionDB.py # 数据库管理类
├── templates/
│   ├── run.html           # 首页模板
│   ├── login.html         # 登录/注册页面模板
│   └── entered.html       # 人脸录入页面模板
└── static/                # 静态资源文件夹
```

## 配置文件说明

### config/.config.ini
```ini
# 数据库
[mysql]
# 数据库密码
DataBase_Password = your_database_password

# 摄像头配置
[camera]
# IP摄像头URL，如果没有IP摄像头，请留空
IP_Camera_URL = 
```

需要将 `your_database_password` 替换为实际的数据库密码。如果使用IP摄像头，还需要配置 `IP_Camera_URL` 项，例如：`http://192.168.1.1:8080/?action=stream`

## 数据库设计

### 数据库结构
系统使用名为 `face_recognition_db` 的数据库，包含两个表：

#### admin_users 表（管理员账户表）
```sql
CREATE TABLE admin_users(
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '管理员用户名',
    password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员账户表';
```

#### face_features 表（人脸特征存储表）
```sql
CREATE TABLE face_features (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    face_encoding JSON NOT NULL COMMENT '128维人脸特征向量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人脸特征存储表';
```

## 核心功能实现

### 1. 首页 (/run)

#### 功能需求
- 显示实时视频流（带人脸识别结果）
- 提供"人脸注册"按钮跳转到注册页面

#### 实现要点
1. 使用Flask的Response对象和generate_frame方法构建HTTP视频流
2. HTML中使用`<img>`标签的src指向/video_feed路由显示视频流
3. 添加"人脸注册"按钮链接到/login路由

#### 代码示例
```python
@app.route("/run", methods=["GET"])
def index():
    return render_template('run.html')

@app.route('/video_feed')
def video_feed():
    return Response(face_rec_sys.generate_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
```

### 2. 用户注册与验证 (/login)

#### 功能需求
- GET请求显示登录表单（用户名、密码输入框及提交按钮）
- POST请求接收表单数据并验证管理员账户
- 验证成功跳转到人脸录入页面(/entered)，失败则提示错误

#### 实现要点
1. 根据request.method区分GET和POST请求
2. 使用SmartLock类的fetch_one方法查询数据库验证账户
3. 验证成功后跳转到人脸录入页面

#### 代码示例
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        # 验证管理员账户
        user = face_rec_sys.fetch_one(
            "SELECT * FROM admin_users WHERE username=%s AND password=%s",
            (username, password)
        )
        if user:
            # 设置认证状态
            session['authenticated'] = True
            return redirect('/entered')
        else:
            # 返回错误信息
            return render_template('login.html', error="账号或密码错误")
```

### 3. 人脸录入 (/entered)

#### 功能需求
- **身份认证前提**：访问此路由需要先通过管理员身份认证
- 显示人脸录入视频流
- 提供"开始录入"、"重新录入"、"确认录入"按钮
- 点击"开始录入"后3秒拍照并静止显示
- 用户可选择"重新录入"或"确认录入"
- 确认录入后将人脸数据存入数据库并跳转到首页
- **认证状态清除**：人脸录入成功后自动取消身份认证授权

#### 实现要点
1. 在进入页面前验证用户身份认证状态
2. 使用Session或其他机制管理认证状态
3. 复用视频流显示功能
4. 实现按钮事件处理逻辑
5. 控制视频流的动态/静态切换
6. 调用SmartLock类的人脸注册方法
7. 录入成功后清除认证状态

#### 代码示例
```python
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
            return render_template('entered.html', registering=True)
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
                return render_template('entered.html', error="未检测到有效人脸数据")
        elif action == 'restart':
            # 重新开始录入
            face_rec_sys.is_register = True
            face_rec_sys.register_face_encoding = None
            return render_template('entered.html', registering=True)
```

## SmartLock类核心方法

### 1. 视频流处理
- `_get_frame()`: 从摄像头获取一帧图像
- `generate_frame()`: 生成HTTP视频流数据帧

### 2. 人脸识别与注册
- `_face_recognition()`: 核心人脸识别逻辑
- `load_known_faces()`: 从数据库加载已知人脸数据
- `register_new_face(username)`: 注册新人脸数据

### 3. 数据库交互
- 继承自DataBaseManager类的方法：
  - `fetch_one(sql, args)`: 查询单条记录
  - `fetch_all(sql, args)`: 查询多条记录
  - `insert_data(sql, args)`: 插入数据

## HTML模板设计

### 1. run.html (首页)
```html
<!DOCTYPE html>
<html>
<head>
    <title>智能门锁系统</title>
</head>
<body>
    <h1>智能门锁系统</h1>
    <img src="{{ url_for('video_feed') }}" width="640" height="480">
    <br>
    <a href="/login"><button>人脸注册</button></a>
</body>
</html>
```

### 2. login.html (注册页面)
```html
<!DOCTYPE html>
<html>
<head>
    <title>管理员登录</title>
</head>
<body>
    <h1>请输入管理员账号密码</h1>
    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}
    <form method="POST">
        <label>用户名:</label>
        <input type="text" name="username" required><br><br>
        <label>密码:</label>
        <input type="password" name="password" required><br><br>
        <input type="submit" value="提交">
    </form>
</body>
</html>
```

### 3. entered.html (人脸录入页面)
```html
<!DOCTYPE html>
<html>
<head>
    <title>人脸录入</title>
    <script>
        function submitAction(action) {
            document.getElementById('action').value = action;
            document.getElementById('entryForm').submit();
        }
    </script>
</head>
<body>
    <h1>人脸录入</h1>
    <img src="{{ url_for('video_feed') }}" width="640" height="480">
    <form id="entryForm" method="POST">
        <input type="hidden" id="action" name="action">
        {% if registering %}
            <input type="hidden" name="username" value="new_user">
        {% endif %}
        <br>
        <button type="button" onclick="submitAction('start')">开始录入</button>
        <button type="button" onclick="submitAction('restart')">重新录入</button>
        <button type="button" onclick="submitAction('confirm')">确认录入</button>
    </form>
</body>
</html>
```

## 开发难点与解决方案

### 1. HTTP视频流构建与显示
**难点**: 实现实时视频流在Web页面中的稳定显示
**解决方案**: 
- 使用Flask的Response对象配合生成器函数
- 设置正确的MIME类型`multipart/x-mixed-replace`
- 在HTML中使用`<img>`标签引用视频流URL

### 2. 数据库用户验证
**难点**: 安全地验证管理员账户
**解决方案**:
- 使用参数化查询防止SQL注入
- 对密码进行加密存储（建议使用哈希算法）
- 合理处理验证失败的情况

### 3. 视频流动态/静态切换
**难点**: 在录制和预览状态间切换视频流显示
**解决方案**:
- 通过设置标志位控制视频处理逻辑
- 在人脸录入时暂停人脸识别功能
- 保留最后一帧图像用于预览显示

### 4. 表单数据传递与处理
**难点**: 在不同页面间传递状态信息
**解决方案**:
- 使用隐藏表单字段传递状态参数
- 利用Session存储临时数据
- 合理设计路由和重定向逻辑

## 部署与运行

### 环境要求
- Python 3.7+
- MySQL数据库
- 相关Python依赖包

### 安装步骤
1. 安装依赖：
   ```
   pip install pymysql cryptography face_recognition opencv-python flask pillow numpy
   ```

2. 配置系统：
   - 修改 `config/.config.ini` 中的数据库密码
   - 如使用IP摄像头，配置 `IP_Camera_URL` 项
   - 运行 `python data_base_init.py` 初始化数据库

3. 配置Flask Session：
   - 在app.py中添加session配置以支持身份认证状态管理
   
   ```python
   from flask import Flask, render_template, Response, jsonify, request, session
   
   def main():
       app = Flask(__name__)
       # 添加secret_key以支持session
       app.secret_key = 'your_secret_key_here'  # 在生产环境中应使用安全的随机密钥
       
       # ... 其他代码 ...
   ```

4. 运行应用：
   ```
   python app.py
   ```

### 访问地址
- 首页: http://127.0.0.1:8888/run
- 注册: http://127.0.0.1:8888/login
- 录入: http://127.0.0.1:8888/entered

## 扩展建议

1. **安全性增强**
   - 使用密码哈希存储替代明文密码
   - 添加CSRF保护
   - 实现HTTPS支持

2. **用户体验优化**
   - 添加加载动画和进度指示器
   - 实现响应式设计适配移动设备
   - 添加多语言支持

3. **功能扩展**
   - 添加用户管理界面
   - 实现开门记录日志
   - 添加远程控制API

4. **性能优化**
   - 实现人脸特征缓存机制
   - 优化视频流压缩算法
   - 添加数据库连接池