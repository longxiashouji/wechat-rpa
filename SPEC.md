# WeChatRPA - 微信 RPA 机器人规格书

> **让程序像真人一样操作微信桌面客户端**

---

## 一、项目定位

**WeChatRPA** 是一款 Windows 桌面自动化工具，通过纯 Python 自研的 Win32 API 封装，实现对微信桌面客户端的全面控制。

核心特点：
- **完全自研** — 不依赖任何第三方专有软件（如 service.exe）
- **系统级操作** — 直接调用 Windows API，模拟真实用户操作
- **易用 API** — HTTP 接口，任何语言都能调用

---

## 二、技术架构

### 2.1 分层设计

```
┌──────────────────────────────────────┐
│         Web API 层 (Flask)            │
│   HTTP 接口 → 路由 → 服务调用           │
├──────────────────────────────────────┤
│         服务层 (Services)             │
│  MessageService / ContactService      │
│  MomentService                       │
├──────────────────────────────────────┤
│         核心层 (Core)                 │
│  WeChatWindow - 窗口管理              │
├──────────────────────────────────────┤
│         工具层 (Utils)                │
│  win32.py - Win32 API 封装            │
│  common.py - 通用工具                 │
├──────────────────────────────────────┤
│         系统层 (Windows API)          │
│  pywin32 + ctypes                    │
│  鼠标/键盘/窗口/剪贴板                │
└──────────────────────────────────────┘
```

### 2.2 核心技术点

**Win32 API 封装**
- `SetCursorPos` / `mouse_event` — 鼠标模拟
- `keybd_event` — 键盘模拟
- `FindWindow` / `FindWindowEx` — 窗口查找
- `SendMessage` / `PostMessage` — 消息发送
- `OpenClipboard` / `SetClipboardData` — 剪贴板

**窗口识别**
- 通过类名 `WeChatMainWndForPC` 查找主窗口
- 遍历子窗口找到消息输入框
- 通过进程名辅助确认微信运行状态

**文本输入**
- 使用剪贴板 + Ctrl+V 粘贴（最可靠的中文输入方式）
- 临时保存原剪贴板内容，操作后恢复

---

## 三、功能模块

### 3.1 消息服务 (MessageService)

| 方法 | 说明 |
|------|------|
| `send_message(user, message)` | 发送文本消息 |
| `send_file(user, file_path)` | 发送文件 |
| `send_image(user, image_path)` | 发送图片 |
| `mass_send(users, message)` | 群发消息 |
| `get_chat_messages(user)` | 获取聊天记录（截图方式）|

### 3.2 通讯录服务 (ContactService)

| 方法 | 说明 |
|------|------|
| `get_contacts()` | 获取通讯录列表 |
| `sync_contacts()` | 同步通讯录 |
| `search_contact(keyword)` | 搜索联系人 |
| `get_contact_info(name)` | 获取联系人详情 |

### 3.3 朋友圈服务 (MomentService)

| 方法 | 说明 |
|------|------|
| `post_moment(content, images)` | 发布朋友圈 |
| `auto_like_moments(count)` | 自动点赞 |

---

## 四、API 设计

### 4.1 RESTful 接口

```
GET  /health                      # 健康检查
GET  /api/license/machine-code     # 获取机器码
POST /api/license/activate         # 激活许可证
POST /api/init/multi              # 初始化微信
POST /api/chat/send_message       # 发送消息
POST /api/agent/chat/send_file   # 发送文件
POST /api/agent/chat/send_image  # 发送图片
GET  /api/contacts                # 获取通讯录
POST /api/contact/sync            # 同步通讯录
POST /api/agent/post_moment       # 发布朋友圈
POST /api/agent/mass_sending      # 群发消息
```

### 4.2 认证方式

所有 API 需要在 Header 中携带：
```
X-API-Key: wechat_rpa_key_2025
```

---

## 五、项目结构

```
WeChatRPA/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── window.py        # WeChatWindow 类
│   ├── services/
│   │   ├── __init__.py
│   │   ├── message.py      # 消息服务
│   │   ├── contact.py       # 通讯录服务
│   │   └── moment.py        # 朋友圈服务
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── win32.py         # Win32 API 封装（核心）
│   │   └── common.py        # 通用工具
│   └── web/
│       ├── __init__.py
│       └── server.py        # Flask Web 服务器
├── scripts/
│   ├── start.bat           # 启动脚本
│   └── stop.bat            # 停止脚本
├── public/
│   └── index.html          # Web 控制台 UI
├── requirements.txt         # Python 依赖
├── README.md
├── SPEC.md
├── CLAUDE.md
└── .gitattributes
```

---

## 六、依赖

| 包 | 版本 | 用途 |
|------|------|------|
| pywin32 | >=306 | Win32 API 调用 |
| pywinauto | >=0.6.8 | UI 控件定位 |
| flask | >=3.0.0 | Web 服务 |
| psutil | >=5.9.0 | 进程管理 |
| Pillow | >=10.0.0 | 图像处理 |
| opencv-python | >=4.8.0 | 图像识别（备用）|

---

## 七、开发进度

- [x] Phase 1: 基础架构（目录结构、工具层）
- [x] Phase 2: 核心功能（窗口管理、输入模拟）
- [x] Phase 3: 服务层（消息、通讯录、朋友圈）
- [x] Phase 4: Web API 服务器
- [x] Phase 5: Web 控制台 UI
- [ ] Phase 6: AI 集成（智能回复、内容生成）
- [ ] Phase 7: 更多自动化场景

---

## 八、设计原则

1. **完全自研** — 不依赖任何第三方专有软件
2. **稳定可靠** — 使用成熟的 Windows API
3. **易于扩展** — 模块化设计，方便添加新功能
4. **开箱即用** — 一键启动，无需复杂配置
5. **社区共建** — 欢迎提交 Issue 和 Pull Request

---

## 九、愿景

让每个人都能拥有自己的微信自动化助手，用程序代替重复的手工操作，提高工作效率。

---

**Copyright (C) 2025 阿龙 / Long**