# -*- coding: utf-8 -*-
"""
Web API 服务器 - 完全自研
使用 Flask 提供 HTTP API
"""

import os
import sys
import time
import threading
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.serving import make_server

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.window import WeChatWindow
from src.services.message import MessageService
from src.services.contact import ContactService
from src.services.moment import MomentService
from src.utils.common import Logger, generate_machine_code


# 创建 Flask 应用
app = Flask(__name__, static_folder='../../public', static_url_path='')
app.config['JSON_AS_ASCII'] = False

# 全局服务实例
window = WeChatWindow()
message_service = MessageService(window)
contact_service = ContactService(window)
moment_service = MomentService(window)

logger = Logger("WebServer")

# API Key（可配置）
API_KEY = os.environ.get('WECHAT_RPA_API_KEY', 'wechat_rpa_key_2025')
API_PREFIX = '/api'


def require_api_key(f):
    """API 密钥验证装饰器"""
    def wrapper(*args, **kwargs):
        key = request.headers.get('X-API-Key', '')
        if key != API_KEY:
            return jsonify({'error': 'Invalid API Key', 'success': False}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# ==================== 健康检查 ====================

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': time.time(),
        'service': 'WeChatRPA',
        'version': '1.0.0'
    })


# ==================== 许可证接口 ====================

@app.route(f'{API_PREFIX}/license/machine-code', methods=['GET'])
@require_api_key
def get_machine_code():
    """获取机器码"""
    machine_code = generate_machine_code()
    return jsonify({
        'success': True,
        'machine_code': machine_code
    })


@app.route(f'{API_PREFIX}/license/activate', methods=['POST'])
@require_api_key
def activate_license():
    """激活许可证"""
    data = request.get_json() or {}
    activation_key = data.get('activation_key', '')
    
    # 自建激活逻辑（可对接自己的服务器验证）
    # 这里简化为本地验证
    if activation_key and len(activation_key) >= 8:
        return jsonify({
            'success': True,
            'message': '激活成功',
            'expire_time': None  # 永不过期
        })
    
    return jsonify({
        'success': False,
        'message': '激活码无效'
    }), 400


@app.route(f'{API_PREFIX}/license/verify', methods=['GET'])
@require_api_key
def verify_license():
    """验证许可证"""
    # 自研激活系统，直接返回已激活
    return jsonify({
        'success': True,
        'activated': True,
        'message': '已激活'
    })


# ==================== 状态接口 ====================

@app.route(f'{API_PREFIX}/agent/backend_status', methods=['GET'])
@require_api_key
def backend_status():
    """获取后端状态"""
    wechat_running = window.find_wechat()
    return jsonify({
        'success': True,
        'backend_status': 'online' if wechat_running else 'offline',
        'wechat_running': wechat_running
    })


@app.route(f'{API_PREFIX}/agent/features_status', methods=['GET'])
@require_api_key
def features_status():
    """获取功能状态"""
    return jsonify({
        'success': True,
        'features': {
            'message': True,
            'contact': True,
            'moment': True,
            'mass_send': True,
            'auto_reply': False,  # 需要 AI
            'auto_like': True,
            'auto_comment': False  # 需要 AI
        }
    })


# ==================== 初始化接口 ====================

@app.route(f'{API_PREFIX}/init/multi', methods=['POST'])
@require_api_key
def init_multi():
    """初始化微信多开"""
    if not window.find_wechat():
        return jsonify({
            'success': False,
            'message': '微信未运行'
        }), 500
    
    window.activate()
    
    return jsonify({
        'success': True,
        'message': '初始化成功',
        'main_hwnd': window.main_hwnd
    })


# ==================== 消息接口 ====================

@app.route(f'{API_PREFIX}/chat/send_message', methods=['POST'])
@require_api_key
def send_message():
    """发送消息"""
    data = request.get_json() or {}
    user = data.get('user', '')
    message = data.get('message', '')
    
    if not user or not message:
        return jsonify({
            'success': False,
            'message': 'user 和 message 参数必填'
        }), 400
    
    result = message_service.send_message(user, message)
    
    return jsonify(result)


@app.route(f'{API_PREFIX}/agent/chat/send_file', methods=['POST'])
@require_api_key
def send_file():
    """发送文件"""
    data = request.get_json() or {}
    user = data.get('user', '')
    file_path = data.get('file_path', '')
    
    if not user or not file_path:
        return jsonify({
            'success': False,
            'message': 'user 和 file_path 参数必填'
        }), 400
    
    result = message_service.send_file(user, file_path)
    
    return jsonify(result)


@app.route(f'{API_PREFIX}/agent/chat/send_image', methods=['POST'])
@require_api_key
def send_image():
    """发送图片"""
    data = request.get_json() or {}
    user = data.get('user', '')
    image_path = data.get('image_path', '')
    
    if not user or not image_path:
        return jsonify({
            'success': False,
            'message': 'user 和 image_path 参数必填'
        }), 400
    
    result = message_service.send_image(user, image_path)
    
    return jsonify(result)


@app.route(f'{API_PREFIX}/chat/messages/<session_name>', methods=['GET'])
@require_api_key
def get_messages(session_name):
    """获取聊天记录"""
    limit = request.args.get('limit', 20, type=int)
    
    result = message_service.get_chat_messages(session_name, limit)
    
    return jsonify(result)


# ==================== 通讯录接口 ====================

@app.route(f'{API_PREFIX}/contacts', methods=['GET'])
@require_api_key
def get_contacts():
    """获取通讯录"""
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    contacts = contact_service.get_contacts(refresh)
    
    return jsonify({
        'success': True,
        'contacts': contacts,
        'count': len(contacts)
    })


@app.route(f'{API_PREFIX}/contact/sync', methods=['POST'])
@require_api_key
def sync_contacts():
    """同步通讯录"""
    result = contact_service.sync_contacts()
    return jsonify(result)


# ==================== 朋友圈接口 ====================

@app.route(f'{API_PREFIX}/agent/post_moment', methods=['POST'])
@require_api_key
def post_moment():
    """发布朋友圈"""
    data = request.get_json() or {}
    content = data.get('content', '')
    files = data.get('files', [])
    
    result = moment_service.post_moment(content, files)
    
    return jsonify(result)


@app.route(f'{API_PREFIX}/moment/toggle-auto-comment', methods=['POST'])
@require_api_key
def toggle_auto_comment():
    """开关朋友圈自动评论"""
    data = request.get_json() or {}
    enabled = data.get('enabled', False)
    
    return jsonify({
        'success': True,
        'enabled': enabled,
        'message': f"朋友圈自动评论已{'开启' if enabled else '关闭'}"
    })


# ==================== 群发接口 ====================

@app.route(f'{API_PREFIX}/agent/mass_sending', methods=['POST'])
@require_api_key
def mass_sending():
    """群发消息"""
    data = request.get_json() or {}
    users = data.get('users', [])
    message = data.get('message', '')
    
    if not users or not message:
        return jsonify({
            'success': False,
            'message': 'users 和 message 参数必填'
        }), 400
    
    result = message_service.mass_send(users, message)
    
    return jsonify(result)


# ==================== 配置接口 ====================

@app.route(f'{API_PREFIX}/config/<config_type>', methods=['GET', 'POST'])
@require_api_key
def config(config_type):
    """获取/设置配置"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'config': {
                'api_key': API_KEY,
                'api_prefix': API_PREFIX
            }
        })
    else:
        return jsonify({
            'success': True,
            'message': '配置已保存'
        })


# ==================== UI 页面 ====================

@app.route('/')
def index():
    """主页"""
    return send_from_directory(app.static_folder, 'index.html')


# ==================== 启动服务器 ====================

class Server:
    """Web 服务器封装"""
    
    def __init__(self, host='127.0.0.1', port=9922):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self):
        """启动服务器"""
        if self.running:
            logger.warn("服务器已在运行")
            return
        
        logger.info(f"启动 Web 服务器: http://{self.host}:{self.port}/")
        
        self.server = make_server(self.host, self.port, app, threaded=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.running = True
        
        logger.info("Web 服务器已启动")
    
    def stop(self):
        """停止服务器"""
        if not self.running:
            return
        
        logger.info("停止 Web 服务器...")
        
        if self.server:
            self.server.shutdown()
        
        self.running = False
        logger.info("Web 服务器已停止")
    
    def restart(self):
        """重启服务器"""
        self.stop()
        time.sleep(1)
        self.start()


# 全局服务器实例
_server = None


def get_server(host='127.0.0.1', port=9922):
    """获取服务器实例"""
    global _server
    if _server is None:
        _server = Server(host, port)
    return _server


if __name__ == '__main__':
    server = get_server()
    server.start()
    
    print(f"\n========================================")
    print(f"  微信 RPA 服务器已启动")
    print(f"  访问地址: http://127.0.0.1:9922/")
    print(f"  API Key: {API_KEY}")
    print(f"========================================\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.stop()