# 智能门锁系统

基于人脸识别技术的智能门锁系统，使用Python和Flask框架实现。

## 项目简介

本项目是一个智能门锁系统，通过人脸识别技术实现身份验证和门锁控制。系统包含以下主要功能：
- 实时人脸识别验证
- 管理员账户验证
- 用户人脸注册和录入
- 数据库存储人脸特征
- Web界面展示
- 门锁状态控制

## 项目成员

- 项目负责人：[Heureka-L](https://github.com/Heureka-L)
- 开发成员：[李四](https://github.com/lisi), [王五](https://github.com/wangwu)

系统采用五层架构设计，具有良好的模块化结构和扩展性。详细的系统架构请参见[System_Architecture.md](System_Architecture.md)文件。

## 文档资料

为了更好地理解和维护本项目，我们提供了以下详细文档：

- [系统架构文档](doc/System_Architecture.md) - 详细介绍系统的整体架构设计
- [开发文档](doc/Development_Document.md) - 包含项目的开发指南和技术细节
- [控制流程文档](doc/ControlFlow.md) - 描述智能锁的控制流程和工作原理

## 技术栈

- **后端**: Python, Flask
- **数据库**: SQLite
- **人脸识别**: face_recognition库
- **计算机视觉**: OpenCV
- **前端**: HTML, CSS

## 项目结构

```
project/
├── app.py                 # Flask主应用
├── database/              # 数据库存储目录
│   └── data_base_init.py  # 数据库初始化脚本
├── config/
│   └── .config.ini        # 数据库配置文件
├── modules/
│   ├── SmartLock.py       # 智能锁核心类
│   └── FaceRecognitionDB.py # 数据库管理类
├── templates/
│   ├── run.html           # 首页模板
│   ├── login.html         # 登录/注册页面模板
│   └── entered.html       # 人脸录入页面模板
└── static/                # 静态资源文件夹
```

## 功能模块

### 1. 智能锁核心 (SmartLock.py)
- 视频流处理：实时从摄像头获取视频帧并处理
- 人脸识别与验证：基于face_recognition库实现的人脸检测和匹配
- 用户人脸注册：新用户人脸数据采集与存储
- 数据库交互：与数据库进行人脸特征数据的读写操作
- 门锁控制：根据识别结果控制门锁开关状态

### 2. 数据库管理 (FaceRecognitionDB.py)
- MySQL数据库连接管理：建立和管理数据库连接
- 人脸特征数据存储：存储用户人脸编码数据
- 管理员账户管理：存储和验证管理员账户信息
- 数据查询和插入操作：提供统一的数据访问接口

### 3. Web服务 (app.py)
- Flask应用路由：处理HTTP请求路由（/run, /login, /entered等）
- 视频流传输：生成并传输实时视频流到Web界面
- 用户界面展示：渲染HTML模板并处理表单提交
- 会话管理：管理用户登录状态和权限验证

## 安装与配置

### 环境要求
- Python 3.7+
- MySQL数据库
- 相关Python依赖包

### 安装步骤

1. 克隆项目到本地
2. 安装依赖包：
   ```bash
   pip install face_recognition opencv-python flask pillow numpy
   ```

3. 配置摄像头：
   - 修改 `config/.config.ini` 文件中的 IP 摄像头 URL（可选）

4. 初始化数据库：
   ```bash
   python database/data_base_init.py
   ```

5. 运行应用：
   ```bash
   python app.py
   ```

## 使用说明

1. 启动应用后，访问 `http://localhost:8888/run`
2. 系统将尝试连接摄像头进行人脸识别
3. 点击"人脸注册"按钮进入管理员登录页面
4. 输入管理员账户密码进行验证
5. 验证成功后进入人脸录入页面，可进行新用户人脸注册
6. 识别成功后系统将自动控制门锁开关
7. 系统支持同时存在多个已注册用户

## 访问地址

- 首页（人脸识别）: http://localhost:8888/run
- 管理员登录: http://localhost:8888/login
- 人脸录入: http://localhost:8888/entered

## 配置文件

### config/.config.ini
```ini
# 摄像头配置
[camera]
# IP摄像头URL，如果没有IP摄像头，请留空
IP_Camera_URL = your_ip_camera_url
```

需要将 `your_database_password` 替换为实际的数据库密码。如果使用IP摄像头，还需要配置 `IP_Camera_URL` 项。

## 数据库结构

系统使用名为 `smartlock_db` 的数据库，包含以下表格：

### admin_users 表
存储管理员账户信息
- id: 主键，自动递增
- username: 管理员用户名
- password: 管理员密码（明文存储，生产环境应使用哈希加密）
- created_at: 账户创建时间
- updated_at: 账户更新时间

### face_features 表
存储用户人脸特征数据
- id: 主键，自动递增
- username: 用户名
- face_encoding: JSON格式的人脸编码数据
- created_at: 记录创建时间
- updated_at: 记录更新时间

## 注意事项

1. 首次运行前必须执行 `database/data_base_init.py` 初始化数据库
2. 确保摄像头设备正常工作
3. 数据库连接信息需正确配置
4. 项目仍在开发中，部分功能可能尚未完善

## 版权信息

本项目仅供学习交流使用, 请在遵守相关法律法规的前提下使用。