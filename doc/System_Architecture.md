# 智能门锁系统架构图

```mermaid
graph TD
    A[用户界面层] --> B[Web服务层]
    B --> C[核心业务逻辑层]
    C --> D[数据访问层]
    C --> E[硬件接口层]
    
    subgraph 用户界面层
        A1[Web浏览器]
    end
    
    subgraph Web服务层
        B1[Flask应用]
        B2[路由处理]
        B3[会话管理]
    end
    
    subgraph 核心业务逻辑层
        C1[SmartLock类]
        C2[人脸识别引擎]
        C3[视频流处理]
        C4[用户认证逻辑]
        C5[人脸注册逻辑]
    end
    
    subgraph 硬件接口层
        E1[摄像头设备]
        E2[门锁执行器]
    end
    
    subgraph 数据访问层
        D1[DataBaseManager类]
        D2[MySQL数据库]
    end
    
    %% 数据库表结构
    D2 --> F1[admin_users表]
    D2 --> F2[face_features表]
    
    %% 连接关系
    A1 --- B1
    B1 --> B2
    B1 --> B3
    B1 --> C1
    C1 --> C2
    C1 --> C3
    C1 --> C4
    C1 --> C5
    C1 --> D1
    C2 --> E1
    C3 --> E1
    C5 --> E1
    D1 --> D2
    
    %% 样式定义
    style A fill:#FFE4B5,stroke:#333
    style B fill:#87CEEB,stroke:#333
    style C fill:#98FB98,stroke:#333
    style D fill:#FFA07A,stroke:#333
    style E fill:#DDA0DD,stroke:#333
    style F1 fill:#F0E68C,stroke:#333
    style F2 fill:#F0E68C,stroke:#333
```

## 架构层次说明

### 1. 用户界面层
- **Web浏览器**: 用户通过标准Web浏览器访问系统，当前不包含移动端应用程序接口

### 2. Web服务层
- **Flask应用**: 基于Python Flask框架构建的Web应用程序
- **路由处理**: 处理HTTP请求路由（/run, /login, /entered等）
- **会话管理**: 管理用户会话状态和身份认证

### 3. 核心业务逻辑层
- **SmartLock类**: 系统核心类，继承自DataBaseManager，整合所有业务功能
- **人脸识别引擎**: 基于face_recognition库实现的人脸检测与识别功能
- **视频流处理**: 实时处理摄像头视频流，生成HTTP视频流
- **用户认证逻辑**: 管理管理员账户登录验证
- **人脸注册逻辑**: 处理新用户人脸数据采集与存储

### 4. 硬件接口层
- **摄像头设备**: 支持本地摄像头(设备0)和网络摄像头(IP摄像头)
- **门锁执行器**: 门锁控制硬件接口（代码中定义但未完全实现）

### 5. 数据访问层
- **DataBaseManager类**: 封装数据库操作的基类，提供连接管理和SQL执行功能
- **MySQL数据库**: 存储系统数据的关系型数据库管理系统

### 6. 数据库表结构
- **admin_users表**: 存储管理员账户信息（id, username, password等字段）
- **face_features表**: 存储用户人脸特征数据（id, username, face_encoding等字段）

## 数据流向说明

1. **用户访问**: 用户通过Web浏览器发起HTTP请求
2. **路由分发**: Flask应用根据URL路径分发请求到对应处理函数
3. **业务处理**: SmartLock类执行具体的业务逻辑处理
4. **数据操作**: 通过DataBaseManager类访问MySQL数据库
5. **硬件交互**: 与摄像头设备进行数据交互获取视频流
6. **结果返回**: 处理结果通过HTTP响应返回给用户浏览器

## 系统特性

1. **单体架构**: 所有功能模块集中在一个应用程序中
2. **Web优先**: 专为Web浏览器访问设计，暂无移动端接口
3. **实时处理**: 支持实时视频流处理和人脸识别
4. **模块化设计**: 数据库操作独立封装，便于维护和扩展
5. **会话安全**: 通过Flask Session管理用户认证状态

## 时序图

### 1. 人脸识别开门流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant W as Web浏览器
    participant F as Flask应用
    participant S as SmartLock类
    participant R as 人脸识别引擎
    participant C as 摄像头设备
    participant D as DataBaseManager类
    participant M as MySQL数据库
    participant L as 门锁执行器

    loop 视频流处理循环
        C->>S: 提供视频帧
        S->>R: 人脸检测与识别
        R->>S: 返回识别结果
        S->>D: 查询人脸数据
        D->>M: 执行查询
        M-->>D: 返回人脸特征
        D-->>S: 返回查询结果
        alt 识别成功
            S->>L: 发送开锁指令
            L-->>S: 确认开锁
        else 识别失败
            S->>L: 发送闭锁指令
            L-->>S: 确认闭锁
        end
        S->>W: 生成视频流
        W-->>U: 显示实时视频和识别结果
    end
```

### 2. 人脸注册流程

```mermaid
sequenceDiagram
    participant U as 管理员
    participant W as Web浏览器
    participant F as Flask应用
    participant S as SmartLock类
    participant R as 人脸识别引擎
    participant C as 摄像头设备
    participant D as DataBaseManager类
    participant M as MySQL数据库

    U->>W: 访问/login页面
    W->>F: 发送GET请求
    F-->>U: 返回登录页面
    U->>W: 输入账号密码
    W->>F: 发送POST请求
    F->>D: 验证管理员账户
    D->>M: 查询账户信息
    M-->>D: 返回账户数据
    D-->>F: 返回验证结果
    alt 验证成功
        F->>W: 重定向到/entered页面
        W->>U: 显示人脸录入页面
        U->>W: 点击开始录入
        W->>F: 发送开始录入请求
        F->>S: 设置注册标志位
        loop 人脸采集循环
            C->>S: 提供视频帧
            S->>R: 检测人脸
            R->>S: 返回人脸编码
            S->>W: 更新视频流
            W-->>U: 显示实时视频
        end
        U->>W: 点击确认录入
        W->>F: 发送确认请求
        F->>S: 注册新人脸
        S->>D: 保存人脸数据
        D->>M: 插入人脸特征
        M-->>D: 确认保存
        D-->>S: 返回保存结果
        S->>F: 重定向到/run页面
        F->>W: 返回首页
        W-->>U: 显示首页
    else 验证失败
        F->>W: 返回错误信息
        W-->>U: 显示登录错误
    end
```