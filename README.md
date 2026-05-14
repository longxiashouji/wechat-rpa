# WeChatRPA - 微信 RPA 机器人

> **完全自主研发 · 用 RPA 技术控制微信桌面客户端**

---

## 一句话理解

> 相当于给微信装了一个"虚拟手指"，你调用接口，它帮你自动操作微信。

---

## 核心能力

| 功能 | 说明 |
|------|------|
| 📤 发送消息 | 给任意联系人发文字 |
| 📎 发送文件 | 发送本地文件到微信 |
| 🖼 发送图片 | 发送图片给联系人 |
| 📢 群发消息 | 一键发给多个好友 |
| 👥 通讯录管理 | 获取好友列表 |
| 🌍 发布朋友圈 | 自动发布朋友圈 |
| 👍 自动点赞 | 自动点赞朋友圈 |

---

## 技术方案

- **语言**: Python 3.8+
- **Windows API**: pywin32 + ctypes（模拟鼠标/键盘/窗口）
- **UI 识别**: pywinauto（窗口控件定位）
- **Web 服务**: Flask（HTTP API）
- **激活系统**: 自建（无需第三方）

**完全自主研发，不依赖任何第三方专有软件。**

---

## 快速开始

### 环境要求

| 要求 | 版本 |
|------|------|
| 操作系统 | Windows 10/11 |
| Python | 3.8+ |
| 微信桌面版 | 任意版本（推荐最新版）|

### 安装

```bash
# 克隆项目
git clone https://github.com/longxiashouji/WeChatRPA.git
cd WeChatRPA

# 安装依赖
pip install -r requirements.txt
```

### 启动

双击运行 `scripts/start.bat`，或在命令行执行：

```bash
python -m src.web.server
```

### 打开控制台

浏览器访问：**http://127.0.0.1:9922/**

---

## API 文档

### 基础配置

| 配置项 | 值 |
|--------|-----|
| 基础 URL | `http://127.0.0.1:9922` |
| API Key | `wechat_rpa_key_2025` |
| Content-Type | `application/json` |

### 发送消息

```bash
curl -X POST http://127.0.0.1:9922/api/chat/send_message \
     -H "Content-Type: application/json" \
     -H "X-API-Key: wechat_rpa_key_2025" \
     -d "{\"user\":\"文件传输助手\",\"message\":\"你好，这是一条测试消息\"}"
```

### 群发消息

```bash
curl -X POST http://127.0.0.1:9922/api/agent/mass_sending \
     -H "Content-Type: application/json" \
     -H "X-API-Key: wechat_rpa_key_2025" \
     -d "{\"users\":[\"张三\",\"李四\"],\"message\":\"这是群发消息\"}"
```

### 发布朋友圈

```bash
curl -X POST http://127.0.0.1:9922/api/agent/post_moment \
     -H "Content-Type: application/json" \
     -H "X-API-Key: wechat_rpa_key_2025" \
     -d "{\"content\":\"今天天气真好！\",\"files\":[\"C:\\\\images\\\\photo.jpg\"]}"
```

---

## 工作原理

```
┌─────────────────┐     HTTP API      ┌─────────────────┐
│   你的程序       │ ────────────────▶  │  WeChatRPA       │
│   (任何语言)     │                   │  Web 服务器      │
└─────────────────┘                   └────────┬────────┘
                                                │
                                       Win32 API 调用
                                                │
                                                ▼
                                     ┌─────────────────┐
                                     │  Windows 系统    │
                                     │  模拟鼠标/键盘   │
                                     └────────┬────────┘
                                                │
                                                ▼
                                     ┌─────────────────┐
                                     │  微信桌面客户端   │
                                     │  WeChat.exe     │
                                     └─────────────────┘
```

---

## 项目结构

```
WeChatRPA/
├── src/
│   ├── core/
│   │   └── window.py       # 微信窗口管理
│   ├── services/
│   │   ├── message.py      # 消息服务
│   │   ├── contact.py      # 通讯录服务
│   │   └── moment.py       # 朋友圈服务
│   ├── utils/
│   │   ├── win32.py       # Win32 API 封装
│   │   └── common.py      # 通用工具
│   └── web/
│       └── server.py      # Flask Web 服务器
├── scripts/
│   ├── start.bat          # 启动脚本
│   └── stop.bat          # 停止脚本
├── public/
│   └── index.html        # Web 控制台 UI
├── requirements.txt       # Python 依赖
├── README.md
├── SPEC.md
├── CLAUDE.md
└── .gitattributes
```

---

## 技术栈

| 分类 | 技术 |
|------|------|
| 语言 | Python 3.8+ |
| Windows API | pywin32, ctypes |
| UI 自动化 | pywinauto |
| Web 框架 | Flask |
| 系统工具 | psutil |

---

## 作者

**阿龙 / Long**

- GitHub: https://github.com/longxiashouji
- Email: 963737104@qq.com
- 微信: clawai

---

## 开源协议

**MIT License**

Copyright (C) 2025 阿龙 / Long

---

<p align="center">
  用 ❤️ 为开源社区打造
</p>