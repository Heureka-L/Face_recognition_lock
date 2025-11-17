# 人脸识别系统使用指南

## 项目概述

这是一个基于 Flask + OpenCV + face_recognition + MySQL 的人脸识别系统，支持实时人脸识别、人脸注册、数据库持久化存储等功能。

## 系统功能

### 核心功能
- ✅ **实时人脸识别** - 通过摄像头实时识别人脸
- ✅ **人脸注册** - 添加新的人脸到系统中
- ✅ **数据库持久化** - 人脸数据存储在MySQL数据库中
- ✅ **Web界面操作** - 通过浏览器进行系统管理
- ✅ **多视频源支持** - 支持IP摄像头、本地摄像头、视频文件

### 技术特点
- **高精度识别** - 使用dlib人脸识别算法，128维特征向量
- **自适应阈值** - 识别阈值0.35，平衡准确率和召回率
- **多人脸处理** - 自动检测并提示单人脸要求
- **实时状态反馈** - 系统状态和识别结果实时显示

## 环境要求

### 硬件要求
- **摄像头** - 支持USB摄像头或笔记本内置摄像头
- **内存** - 至少4GB RAM（推荐8GB）
- **处理器** - 支持SSE2指令集的CPU

### 软件要求
- **操作系统** - Windows 10/11, Linux, macOS
- **Python** - 3.7+ (推荐3.8-3.13)
- **MySQL** - 5.7+ 或 MariaDB 10.2+
- **浏览器** - Chrome, Firefox, Edge 最新版本

## 安装配置

### 1. 安装Python依赖

```bash
# 使用清华镜像源加速安装
pip install flask opencv-python opencv-contrib-python pymysql  pillow face_recognition  -i https://pypi.tuna.tsinghua.edu.cn/simple
```
#### 问题处理：<br>
- face_reconition 库安装失败<br>
face_recognition库依赖于dlib库运行，在安装face_reconition库前需要先安装dlib库
- dlib库安装<br>
dlib 是 Python 中一个强大的人脸识别库，但由于其依赖 C++ 编译和复杂的依赖关系，安装过程可能比较困难。<br>
在安装dlib前需要先安装：<br>
1、安装 Visual Studio Build Tools：https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/
2、cmake：https://cmake.org/download/ （找到Windows x64 Installer下载并安装）<br>
dlib和face_recognition安装：
```bash
pip install dlib -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install face_recognition 
```

不出意外的话face_recognition库就能正常安装了，安装不了联系我解决.jpg
### 2. 配置MySQL数据库

#### 2.1 安装MySQL
- Windows: 下载MySQL Installer安装
- Linux: `sudo apt-get install mysql-server`
- macOS: `brew install mysql`

#### 2.2 设置数据库密码
编辑 `config.ini` 文件，修改数据库密码(密码不用加引号)：
```ini
DataBase_Password = your_password
```

#### 2.3 初始化数据库
```bash
python data_base_init.py
```

预期输出：
```
数据库创建成功
数据表创建成功
数据库和表结构创建完成！
```

### 3. 启动系统

```bash
python app.py
```

### **重要提示： 若运行代码提示face_recognition模块未安装或未检测到人脸识别模型,请执行以下命令：**
```bash
# 原因未知，可能是face_recognition模块的安装问题，执行以上命令后，再次运行app.py即可。
pip install setuptools
```

成功启动后，控制台显示：
```
视频源 XXX 初始化成功
视频流状态：True
 * Running on http://127.0.0.1:8888
```

### 4. 访问Web界面

打开浏览器，访问：http://localhost:8888

## 使用说明

### 基本操作流程

#### 1. 首次使用
1. 启动系统后，Web界面会显示实时视频流
2. 系统状态显示"已停止"，已知人脸数为0
3. 需要先注册人脸才能进行识别

#### 2. 注册人脸
1. 点击"注册新人脸"按钮
2. 在弹出的对话框中输入姓名（支持中文）
3. 面向摄像头，确保光线充足，面部清晰
4. 系统会自动检测人脸并注册
5. 注册成功后，状态栏会显示相关信息

**注册要求：**
- 确保只有一张人脸在画面中
- 光线均匀，避免逆光
- 正面面对摄像头
- 保持自然表情

#### 3. 开始识别
1. 点击"开始识别"按钮
2. 系统状态变为"运行中"
3. 视频流中会实时显示识别结果
4. 识别到的人脸会用绿色框标记，并显示姓名
5. 未识别的人脸会显示为"unknown"

#### 4. 停止识别
点击"停止识别"按钮，系统停止人脸识别，但视频流继续显示。

#### 状态信息说明
- **状态** - 运行中/已停止
- **已知人脸** - 数据库中已注册的人脸数量
- **系统消息** - 当前操作状态或提示信息
- **注册状态** - 正在注册时显示注册人姓名

#### 识别结果显示
- **绿色边框** - 检测到的人脸位置
- **姓名标签** - 边框下方显示识别到的姓名
- **时间戳** - 视频左上角显示当前时间

### API接口说明

系统提供RESTful API接口，可用于二次开发：

| 接口 | 方法 | 功能 |
|-----|------|------|
| `/` | GET | 主页 |
| `/video_feed` | GET | 视频流 |
| `/start_reconition` | POST | 启动人脸识别 |
| `/stop_reconition` | POST | 停止人脸识别 |
| `/register_new_face` | POST | 注册新人脸 |
| `/get_status` | GET | 获取系统状态 |

**状态API返回格式：**
```json
{
  "is_running": true,
  "known_faces_count": 5,
  "sys_msg": "检测到人脸",
  "is_register": false,
  "register_name": "unknown"
}
```

## 项目结构详解

```
01_人脸识别demo_MySQL/
├── app.py                  # 主应用文件 - Flask服务器和人脸识别核心逻辑
├── data_base_init.py       # 数据库初始化脚本
├── 使用指南.md            # 本使用指南
├── README.md              # 项目说明文档
├── info.txt               # 开发文档和类结构说明
├── moudle/                # 人脸识别模型文件
│   ├── dlib_face_recognition_resnet_model_v1.dat    # 人脸识别模型
│   ├── shape_predictor_5_face_landmarks.dat        # 5点 landmarks模型
│   └── shape_predictor_68_face_landmarks.dat     # 68点 landmarks模型
├── sources/               # 视频源文件
│   ├── 32673695682-1-30064.mp4    # 备用测试视频
│   └── known_faces/      # 示例人脸图片
│       ├── tim1.png
│       ├── tim2.png
│       ├── tim3.png
│       ├── tim4.png
│       └── tim5.png
├── static/                # 静态文件目录（预留）
└── templates/             # HTML模板
    └── index.html         # Web界面模板
```

## 常见问题解决

### 数据库相关问题

#### 数据库连接失败
**错误现象：** `数据库连接错误` 或 `创建失败`
**解决方法：**
1. 检查MySQL服务是否启动
2. 确认用户名密码正确
3. 检查MySQL端口是否为3306
4. 确认有创建数据库的权限

#### 数据库权限问题
**错误现象：** `Access denied for user`
**解决方法：**
```sql
-- 在MySQL中执行
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 视频流相关问题

#### 摄像头无法打开
**错误现象：** `视频源 0 初始化失败`
**解决方法：**
1. 检查摄像头是否被其他程序占用
2. 确认摄像头驱动正常
3. 尝试更换视频源索引（修改app.py第246行）
4. 检查摄像头权限设置

#### 视频流延迟或卡顿
**解决方法：**
1. 降低视频分辨率（修改app.py第175行缩放比例）
2. 关闭其他占用CPU的程序
3. 检查USB接口是否松动

### 人脸识别相关问题

#### 识别准确率差
**解决方法：**
1. 确保光线充足均匀
2. 重新注册更清晰的人脸样本
3. 调整识别阈值（修改app.py第188行）
4. 保持摄像头清洁

#### 无法检测到人脸
**解决方法：**
1. 调整与摄像头的距离（0.5-2米最佳）
2. 确保面部无遮挡
3. 检查光线条件
4. 重新启动系统

### 系统性能优化

#### CPU占用过高
**优化方法：**
1. 降低视频帧率（修改app.py第175行）
2. 减少识别频率
3. 使用更低分辨率的视频流

#### 内存使用优化
**优化方法：**
1. 定期清理视频缓存
2. 限制同时处理的人脸数量
3. 优化数据库查询

## 高级配置

### 视频源配置
在 `app.py` 第238-243行，可以配置多个视频源：
```python
video_sources = [
    r'http://192.168.1.1:8080/?action=stream',  # IP摄像头
    0,  # 本地摄像头
    r'sources/32673695682-1-30064.mp4'  # 视频文件
]
```

### 识别参数调整
在 `app.py` 第188行调整识别阈值：
```python
face_matches = face_rec.compare_faces(self.Known_faces,face_encoding,tolerance=0.35)
```
阈值范围：0.3-0.38(亚洲人推荐值)，值越小要求越严格

### 数据库配置
修改数据库连接参数（`app.py` 第14-24行）：
```python
self.DB_CONFIG = {
    "host": "localhost",
    "user": "root", 
    "passwd": password,
    "charset": "utf8mb4",
    "port": 3306,
    "database": "face_recognition_db"
}
```

### 添加人脸识别历史记录
可以新增数据表记录识别历史：
```sql
CREATE TABLE recognition_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    recognition_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT
);
```
## 技术支持

### 日志调试
系统会在控制台输出详细日志，包括：
- 数据库操作状态
- 视频流状态
- 人脸识别结果
- 错误信息

### 性能监控
可以通过API定期获取系统状态，监控：
- 识别成功率
- 系统响应时间
- 资源使用情况

## 联系信息

如有问题或建议，请通过以下方式联系：
- GitHub仓库：https://github.com/Heureka-L/Face_recognition_lock
- 提交Issue到项目仓库（若要使用github联系我获取访问权限）
- 参考info.txt了解代码结构
---

**版本：** v1.1  
**更新日期：** 2025-11-16  
**作者：** Heureka