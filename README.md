# WeChat RPA Bot - Node.js Version

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

微信 RPA 机器人的 **Node.js/TypeScript 重写版本**。采用成熟、正规的 RPA（机器人流程自动化）技术，通过完全模拟人类的真实鼠标点击和键盘输入来完成协同工作。

> ⚠️ **重要说明**：本项目是 LeoMusk/wechat-rpa-bot-skill 的 Node.js 语言重写版本，核心 RPA 功能依赖于原作者提供的 `service.exe`。请在使用前阅读原项目的许可证和使用条款。

---

##  核心特性

- **Node.js/TypeScript** — 现代 JavaScript 技术栈，适合前端开发者
- **轻量前端** — 纯 HTML/CSS/JS，无需构建，直接运行
- **RESTful API** — 完整封装所有 RPA API 调用
- **Windows 原生** — 提供 `.bat` 批处理脚本，一键启动/停止

---

## 环境要求

- **Windows** 系统
- **微信桌面版 4.1.7**（必须是这个版本，不支持其他版本）
- **Python 3.8+**（用于运行 RPA 服务脚本）
- **Node.js 16+**（用于运行本项目）
- **RPA 后端服务**（`service.exe`，需从 [原项目 Releases](https://github.com/LeoMusk/wechat-rpa-bot-skill/releases) 下载）

---

##  安装步骤

### 1. 下载 RPA 后端服务

本项目依赖原作者的 `service.exe`，请先下载：

```bash
# 在项目根目录执行，下载 v1.7.7 版本（如有更新请使用最新版本）
curl -L -o service.exe https://github.com/LeoMusk/wechat-rpa-bot-skill/releases/download/v1.7.7/service.exe
```

### 2. 安装 Node.js 依赖

```bash
cd nodejs-version
npm install
```

### 3. 安装 Python 依赖

```bash
pip install psutil requests
```

### 4. 配置激活码

本项目使用**激活码**方式认证。请访问 [www.yokoagi.com](https://www.yokoagi.com) 获取激活码。

---

##  快速开始

### 启动服务

```bash
# 方式一：双击运行
双击 "启动微信RPA.bat"

# 方式二：命令行
cd nodejs-version
node dist/server.js
```

### 访问控制台

打开浏览器访问：**http://127.0.0.1:9922/**

### 停止服务

```bash
# 双击运行
双击 "停止微信RPA.bat"
```

---

##  API 示例

所有 API 调用都需要携带 header：`X-API-Key: yoko_test`

### 初始化

```bash
curl --noproxy "*" -X POST http://127.0.0.1:9922/api/init/multi ^
     -H "Content-Type: application/json" ^
     -H "X-API-Key: yoko_test" ^
     -d "{}"
```

### 发送消息

```bash
curl --noproxy "*" -X POST http://127.0.0.1:9922/api/chat/send_message ^
     -H "Content-Type: application/json" ^
     -H "X-API-Key: yoko_test" ^
     -d "{\"user\":\"文件传输助手\",\"message\":\"你好，这是来自 Node.js 的消息！\"}"
```

### 发送文件

```bash
curl --noproxy "*" -X POST http://127.0.0.1:9922/api/agent/chat/send_file ^
     -H "Content-Type: application/json" ^
     -H "X-API-Key: yoko_test" ^
     -d "{\"user\":\"文件传输助手\",\"file_path\":\"C:\\docs\\report.xlsx\"}"
```

### 发布朋友圈

```bash
curl --noproxy "*" -X POST http://127.0.0.1:9922/api/agent/post_moment ^
     -H "Content-Type: application/json" ^
     -H "X-API-Key: yoko_test" ^
     -d "{\"content\":\"今天天气真好！\",\"files\":[\"C:\\\\images\\\\photo.jpg\"]}"
```

---

##  项目结构

```
nodejs-version/
├── package.json          # Node.js 项目配置
├── tsconfig.json         # TypeScript 配置
├── src/
│   ├── client.ts        # RPA API 客户端封装
│   └── server.ts        # Express Web 服务器
├── public/
│   └── index.html       # 前端控制台界面
├── 启动微信RPA.bat       # Windows 启动脚本
└── 停止微信RPA.bat       # Windows 停止脚本
```

---

##  TypeScript 客户端使用

```typescript
import { WeChatRPAClient } from './client';

// 创建客户端实例
const client = new WeChatRPAClient();

// 初始化
async function init() {
  // 获取机器码
  const machineCode = await client.getMachineCode();
  console.log('机器码:', machineCode);

  // 初始化微信
  const result = await client.initialize();
  if (result.success) {
    console.log('微信初始化成功！');
  } else {
    console.log('初始化失败:', result.code);
  }
}

// 发送消息
async function send() {
  const success = await client.sendMessage('文件传输助手', '测试消息');
  console.log('发送成功:', success);
}

init();
send();
```

---

##  常见问题

### Q: 服务无法启动？

1. 确认已下载 `service.exe` 到项目根目录
2. 确认微信 4.1.7 已安装并登录
3. 确认 9922 端口未被占用

### Q: 发送消息失败？

- 检查微信是否已登录
- 检查 API 认证头是否正确：`X-API-Key: yoko_test`
- 检查消息编码是否正确

### Q: 提示"未激活"？

请访问 [www.yokoagi.com](https://www.yokoagi.com) 获取激活码，然后在控制台中激活。

---

##  许可证

本项目遵循 **MIT 许可证**，但核心 RPA 功能依赖于原作者的专有软件。请在使用前阅读并遵守原项目 [LeoMusk/wechat-rpa-bot-skill](https://github.com/LeoMusk/wechat-rpa-bot-skill) 的使用条款。

---

##  参考链接

- [原项目 wechat-rpa-bot-skill](https://github.com/LeoMusk/wechat-rpa-bot-skill)
- [微信 RPA 操作文档](https://n2b8xxdgjx.feishu.cn/wiki/DgLlwBoV4ioFbpkG8LDcz6VjnAf)
- [www.yokoagi.com](https://www.yokoagi.com) — 激活码获取