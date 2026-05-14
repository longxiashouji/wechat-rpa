# -*- coding: utf-8 -*-
"""
消息服务模块 - 完全自研
负责发送消息、发文件、发朋友圈等
"""

import time
import os
from typing import List, Optional, Dict

from ..core.window import WeChatWindow
from ..utils.common import Logger, random_delay, retry
from ..utils.win32 import (
    set_clipboard_text, send_ctrl_key, press_key, left_click,
    set_cursor_pos, left_double_click, VK_RETURN, VK_BACK, VK_SPACE
)


class MessageService:
    """消息服务类"""
    
    def __init__(self, window: WeChatWindow = None):
        self.window = window or WeChatWindow()
        self.logger = Logger("MessageService")
    
    def is_wechat_ready(self) -> bool:
        """检查微信是否就绪"""
        return self.window.find_wechat() and self.window.activate()
    
    @retry(max_attempts=2, delay=1)
    def send_message(self, user: str, message: str) -> Dict:
        """
        发送文本消息给指定用户
        
        Args:
            user: 接收人（备注名/昵称/微信号）
            message: 消息内容
            
        Returns:
            {"success": True/False, "message": "..."}
        """
        if not self.is_wechat_ready():
            return {"success": False, "message": "微信未运行或无法激活"}
        
        # 先搜索并打开聊天窗口
        self.logger.info(f"正在发送消息给 {user}")
        
        if not self.window.open_chat_by_search(user):
            return {"success": False, "message": f"无法打开与 {user} 的聊天窗口"}
        
        random_delay(200, 400)
        
        # 发送消息
        if not self.window.send_text_message(message):
            return {"success": False, "message": "发送消息失败"}
        
        return {"success": True, "message": f"消息已发送给 {user}"}
    
    def send_file(self, user: str, file_path: str) -> Dict:
        """
        发送文件给指定用户
        
        Args:
            user: 接收人
            file_path: 文件路径
            
        Returns:
            {"success": True/False, "message": "..."}
        """
        if not os.path.exists(file_path):
            return {"success": False, "message": f"文件不存在: {file_path}"}
        
        if not self.is_wechat_ready():
            return {"success": False, "message": "微信未运行"}
        
        self.logger.info(f"正在发送文件给 {user}: {file_path}")
        
        # 打开聊天窗口
        if not self.window.open_chat_by_search(user):
            return {"success": False, "message": f"无法打开与 {user} 的聊天窗口"}
        
        random_delay(200, 300)
        
        # 点击附件按钮（回形针图标）
        # 位置：聊天输入框左侧
        left, top, right, bottom = self.window.get_main_rect()
        attach_x = left + int((right - left) * 0.15)
        attach_y = bottom - int((bottom - top) * 0.15)
        
        left_click(attach_x, attach_y)
        random_delay(200, 300)
        
        # 选择"文件"选项
        # 通常附件菜单会弹出，选第一个或第二个
        # 简化为直接用键盘快捷键 Ctrl+Shift+D 或直接拖拽
        
        # 方法: 用文件路径复制粘贴到输入框
        # 微信会自动识别文件
        set_clipboard_text(file_path)
        random_delay(100, 200)
        send_ctrl_key(0x56)  # Ctrl+V
        
        random_delay(500, 800)
        
        # 按回车发送
        press_key(VK_RETURN)
        
        self.logger.info(f"文件已发送给 {user}")
        return {"success": True, "message": f"文件已发送给 {user}"}
    
    def send_image(self, user: str, image_path: str) -> Dict:
        """
        发送图片给指定用户
        
        Args:
            user: 接收人
            image_path: 图片路径
            
        Returns:
            {"success": True/False, "message": "..."}
        """
        if not os.path.exists(image_path):
            return {"success": False, "message": f"图片不存在: {image_path}"}
        
        if not self.is_wechat_ready():
            return {"success": False, "message": "微信未运行"}
        
        self.logger.info(f"正在发送图片给 {user}: {image_path}")
        
        # 打开聊天窗口
        if not self.window.open_chat_by_search(user):
            return {"success": False, "message": f"无法打开与 {user} 的聊天窗口"}
        
        random_delay(200, 300)
        
        # 点击图片按钮（在附件菜单中）
        left, top, right, bottom = self.window.get_main_rect()
        # 图片按钮位置偏下
        img_x = left + int((right - left) * 0.10)
        img_y = bottom - int((bottom - top) * 0.12)
        
        left_click(img_x, img_y)
        random_delay(200, 300)
        
        # 在文件选择对话框中输入路径
        # 这里需要处理 Windows 文件选择对话框
        # 简化为直接把图片路径粘贴到对话框
        
        set_clipboard_text(image_path)
        random_delay(100, 200)
        send_ctrl_key(0x56)  # Ctrl+V
        random_delay(100, 200)
        press_key(VK_RETURN)  # 确认
        
        random_delay(500, 800)
        
        # 发送
        press_key(VK_RETURN)
        
        return {"success": True, "message": f"图片已发送给 {user}"}
    
    def mass_send(self, users: List[str], message: str) -> Dict:
        """
        群发消息给多个用户
        
        Args:
            users: 用户列表
            message: 消息内容
            
        Returns:
            {"success": True/False, "sent": [...], "failed": [...]}
        """
        self.logger.info(f"开始群发给 {len(users)} 个用户")
        
        sent = []
        failed = []
        
        for user in users:
            result = self.send_message(user, message)
            if result["success"]:
                sent.append(user)
            else:
                failed.append(user)
            
            # 群发间隔，避免被检测
            random_delay(500, 1000)
        
        self.logger.info(f"群发完成: 成功 {len(sent)}, 失败 {len(failed)}")
        
        return {
            "success": len(failed) == 0,
            "sent": sent,
            "failed": failed,
            "total": len(users)
        }
    
    def get_chat_messages(self, user: str = None, limit: int = 20) -> Dict:
        """
        获取聊天记录（通过截图+OCR方式）
        注意：这个功能需要 AI 参与解析截图
        
        Args:
            user: 聊天对象，为空则获取当前聊天
            limit: 消息条数上限
            
        Returns:
            {"success": True/False, "messages": [...]}
        """
        if not self.is_wechat_ready():
            return {"success": False, "message": "微信未运行"}
        
        # 截图
        screenshot_path = self.window.screenshot()
        if not screenshot_path:
            return {"success": False, "message": "截图失败"}
        
        # 注意：实际项目中应该调用 OCR 或 AI 来解析截图获取消息
        # 这里仅返回截图路径
        return {
            "success": True,
            "screenshot": screenshot_path,
            "message": "截图已保存，需配合 OCR/AI 解析消息内容"
        }
    
    def get_conversations(self) -> List[Dict]:
        """
        获取会话列表
        
        Returns:
            [{"name": "张三", "last_msg": "...", "unread": 0}, ...]
        """
        if not self.is_wechat_ready():
            return []
        
        # 获取 UI 树，分析会话列表
        # 实际需要根据微信界面结构调整
        # 这里返回空列表，后续根据实际 UI 调整
        self.logger.info("获取会话列表")
        
        # 通过截图方式获取
        screenshot = self.window.screenshot()
        
        return []  # 需要配合 AI/OCR 解析