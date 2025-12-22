# 智能锁控制流

## SmartLock类

### 属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| open_lock | bool | 开锁状态，true表示开，false表示关 |
| lock_state | bool | 智能锁工作状态，true表示运行，false表示非运行 |
| server_base_url | string | 后端服务器基地址 |
| video_cap | cv2.VideoCapture | 视频捕获对象，用于从摄像头获取视频流 |
| video_status | bool | 视频流状态，记录视频流是否正常打开 |
| is_running | bool | 人脸识别运行状态，true表示正在运行，false表示停止运行 |
| Known_faces | list | 已知人脸编码列表，存储从数据库加载的所有已知人脸编码 |
| names | list | 已知人脸姓名列表，存储与Known_faces对应的人脸姓名 |
| frame | numpy.ndarray | 当前视频帧，存储当前从摄像头获取的视频帧 |
| show_frame | numpy.ndarray | 显示帧，用于生成HTTP数据流显示的视频帧 |
| sys_msg | string | 系统消息，显示系统状态信息 |
| current_face_exist | bool | 当前人脸存在状态，记录当前识别到的人脸是否存在于数据库中 |
| is_register | bool | 注册状态，true表示正在进行人脸注册，false表示不在注册状态 |
| register_face_encoding | numpy.ndarray | 待注册人脸编码，存储正在进行注册的人脸编码 |
| font | ImageFont | 字体对象，用于绘制中文文本 |

### 核心方法

#### 视频处理相关
- `_get_frame()`：从视频流中获取一帧图像
- `generate_frame()`：生成HTTP视频流数据帧，用于Web界面显示

#### 人脸识别与注册相关
- `load_known_faces()`：从数据库中加载所有已知人脸数据
- `_face_recognition()`：核心人脸识别逻辑，包括人脸检测、匹配和结果绘制
- `register_new_face(username)`：注册新人脸并存储到数据库

#### 门锁控制相关
- `open_lock()`：开锁操作
- `close_lock()`：关锁操作
- `init_lock()`：初始化锁状态（默认关闭）
- `lock_control()`：锁控制逻辑，根据人脸识别结果控制门锁开关
- `run_server()`：启动智能锁服务，开启人脸识别和锁控制线程

## 系统控制流程

### 1. 系统启动流程
1. 读取配置文件获取数据库密码
2. 尝试初始化视频源（优先使用IP摄像头，失败则使用本地摄像头）
3. 初始化SmartLock对象，连接数据库并加载已知人脸数据
4. 启动Flask Web服务

### 2. 人脸识别流程
1. 启动视频捕获线程，持续获取视频帧
2. 在每一帧中进行人脸检测：
   - 检测到单个人脸：进行人脸识别
   - 检测到多个人脸：提示"请确保屏幕中仅存在一张人脸"
   - 未检测到人脸：提示"未检测到人脸"
3. 人脸识别过程：
   - 如果处于注册状态：保存当前人脸编码到register_face_encoding
   - 如果不是注册状态：与已知人脸进行比对
     - 匹配成功：标记current_face_exist为True，显示匹配用户名
     - 匹配失败：标记current_face_exist为None，显示"unknown"
4. 根据识别结果控制门锁：
   - 识别到已知人脸：开门
   - 未识别到人脸或识别失败：关门

### 3. 用户注册流程
1. 管理员通过/login路由进行身份验证
2. 验证成功后跳转到/entered路由进行人脸录入
3. 在人脸录入页面：
   - 点击"开始录入"按钮，设置is_register为True
   - 系统持续捕获人脸并更新register_face_encoding
   - 点击"确认录入"按钮，调用register_new_face方法将人脸数据存入数据库
   - 录入完成后清除认证状态并返回首页

### 4. Web界面交互流程
1. 首页(/run)：显示实时视频流和人脸识别结果
2. 登录页(/login)：管理员账户验证
3. 人脸录入页(/entered)：新用户人脸数据采集与存储