# WeChatRPA

> **作者：阿龙 / Long**

## 项目简介

WeChatRPA 是一款完全自主研发的微信 RPA 机器人。使用 Python + Windows API 实现微信桌面客户端的自动化控制。

## 技术栈

- Python 3.8+ (Win32 API, ctypes)
- pywin32 + pywinauto
- Flask (Web API)
- psutil (进程管理)

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m src.web.server

# 打开控制台
# 浏览器访问 http://127.0.0.1:9922/
```

## 核心模块

- `src/utils/win32.py` — Win32 API 封装（核心）
- `src/core/window.py` — 微信窗口管理
- `src/services/message.py` — 消息服务
- `src/web/server.py` — Web API 服务器

## 版权声明

Copyright (C) 2025 阿龙 / Long. 963737104@qq.com