/**
 * 微信 RPA 机器人 - Express Web 服务器
 *
 * 提供 Web UI 界面和 REST API 代理
 * 将前端请求转发到 RPA 后端 (127.0.0.1:9922)
 */

import express from 'express';
import { createServer } from 'http';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 9922;

// 中间件
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// 代理配置
const RPA_BASE = 'http://127.0.0.1:9922';
const API_KEY = 'yoko_test';

// 代理 helper
async function proxyRequest(res: express.Response, method: string, url: string, data?: any) {
  try {
    const fetch = (await import('node-fetch')).default;
    const options: any = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
    };
    if (data) options.body = JSON.stringify(data);

    const response = await fetch(`${RPA_BASE}${url}`, options);
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      const json = await response.json();
      res.status(response.status).json(json);
    } else {
      res.status(response.status).send(await response.text());
    }
  } catch (e: any) {
    console.error(`代理请求失败 [${method} ${url}]:`, e.message);
    res.status(502).json({ error: '代理请求失败', message: e.message });
  }
}

// API 路由 - 许可证
app.get('/api/license/machine-code', (req, res) => proxyRequest(res, 'GET', '/api/license/machine-code'));
app.post('/api/license/activate', (req, res) => proxyRequest(res, 'POST', '/api/license/activate', req.body));
app.get('/api/license/verify', (req, res) => proxyRequest(res, 'GET', '/api/license/verify'));

// API 路由 - 初始化
app.get('/api/agent/backend_status', (req, res) => proxyRequest(res, 'GET', '/api/agent/backend_status'));
app.get('/api/agent/instances_status', (req, res) => proxyRequest(res, 'GET', '/api/agent/instances_status'));
app.post('/api/init/multi', (req, res) => proxyRequest(res, 'POST', '/api/init/multi', req.body));
app.post('/api/system/wechat41/auto_config', (req, res) => proxyRequest(res, 'POST', '/api/system/wechat41/auto_config', req.body));

// API 路由 - 消息
app.post('/api/chat/send_message', (req, res) => proxyRequest(res, 'POST', '/api/chat/send_message', req.body));
app.post('/api/agent/chat/send_file', (req, res) => proxyRequest(res, 'POST', '/api/agent/chat/send_file', req.body));
app.get('/api/chat/messages/:sessionName', (req, res) => proxyRequest(res, 'GET', `/api/chat/messages/${req.params.sessionName}`));

// API 路由 - 朋友圈
app.post('/api/agent/post_moment', (req, res) => proxyRequest(res, 'POST', '/api/agent/post_moment', req.body));

// API 路由 - 群发
app.post('/api/agent/mass_sending', (req, res) => proxyRequest(res, 'POST', '/api/agent/mass_sending', req.body));
app.get('/api/agent/tasks', (req, res) => proxyRequest(res, 'GET', '/api/agent/tasks'));

// API 路由 - 通讯录
app.get('/api/contacts', (req, res) => proxyRequest(res, 'GET', '/api/contacts'));
app.post('/api/contact/sync', (req, res) => proxyRequest(res, 'POST', '/api/contact/sync', req.body));

// API 路由 - AI 功能
app.get('/api/agent/features_status', (req, res) => proxyRequest(res, 'GET', '/api/agent/features_status'));
app.post('/api/chat/multi-monitor/start', (req, res) => proxyRequest(res, 'POST', '/api/chat/multi-monitor/start'));
app.post('/api/chat/monitor/stop', (req, res) => proxyRequest(res, 'POST', '/api/chat/monitor/stop'));
app.post('/api/moment/toggle-auto-comment', (req, res) => proxyRequest(res, 'POST', '/api/moment/toggle-auto-comment', req.body));
app.post('/api/friend/auto-add-new/toggle', (req, res) => proxyRequest(res, 'POST', '/api/friend/auto-add-new/toggle', req.body));

// API 路由 - 配置
app.get('/api/config/:configType', (req, res) => proxyRequest(res, 'GET', `/api/config/${req.params.configType}`));
app.post('/api/config/:configType', (req, res) => proxyRequest(res, 'POST', `/api/config/${req.params.configType}`, req.body));

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 启动服务器
const server = createServer(app);
server.listen(PORT, () => {
  console.log(`🚀 微信 RPA 控制台已启动: http://127.0.0.1:${PORT}/`);
  console.log(`📡 RPA 后端代理: ${RPA_BASE}`);
});

export default app;