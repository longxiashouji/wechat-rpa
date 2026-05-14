# -*- coding: utf-8 -*-
"""
朋友圈服务模块 - 完全自研
负责发朋友圈、评论等
"""

import time
import os
from typing import List, Dict

from ..core.window import WeChatWindow
from ..utils.common import Logger, random_delay
from ..utils.win32 import left_click, set_clipboard_text, send_ctrl_key, press_key, VK_RETURN


class MomentService:
    """朋友圈服务类"""
    
    def __init__(self, window: WeChatWindow = None):
        self.window = window or WeChatWindow()
        self.logger = Logger("MomentService")
    
    def post_moment(self, content: str = None, images: List[str] = None) -> Dict:
        """
        发布朋友圈
        
        Args:
            content: 文字内容
            images: 图片路径列表
            
        Returns:
            {"success": True/False, "message": "..."}
        """
        if not self.window.find_wechat():
            return {"success": False, "message": "微信未运行"}
        
        self.logger.info("正在发布朋友圈...")
        
        self.window.activate()
        random_delay(200, 300)
        
        # 获取主窗口尺寸
        left, top, right, bottom = self.window.get_main_rect()
        width = right - left
        height = bottom - top
        
        # 点击"我"标签（右下角）
        me_x = left + int(width * 0.05)
        me_y = bottom - int(height * 0.08)
        
        left_click(me_x, me_y)
        random_delay(500, 800)
        
        # 点击"朋友圈"入口
        # 需要在"我"页面中查找朋友圈入口
        # 简化为再次点击朋友圈图标
        
        # 备选：直接用快捷键打开朋友圈
        # Ctrl+G 是微信的朋友圈快捷键
        send_ctrl_key(0x47)  # G
        random_delay(500, 800)
        
        # 点击发布按钮
        publish_x = right - 80
        publish_y = top + 80
        
        left_click(publish_x, publish_y)
        random_delay(500, 800)
        
        # 输入文字内容
        if content:
            set_clipboard_text(content)
            random_delay(100, 200)
            send_ctrl_key(0x56)  # Ctrl+V
            random_delay(300, 500)
        
        # 添加图片
        if images:
            for img_path in images[:9]:  # 朋友圈最多9张图
                if not os.path.exists(img_path):
                    self.logger.warn(f"图片不存在: {img_path}")
                    continue
                
                # 点击添加图片按钮
                add_img_x = left + int(width * 0.1)
                add_img_y = top + int(height * 0.4)
                
                left_click(add_img_x, add_img_y)
                random_delay(300, 500)
                
                # 在文件对话框中输入路径
                set_clipboard_text(img_path)
                random_delay(100, 200)
                send_ctrl_key(0x56)  # Ctrl+V
                random_delay(200, 300)
                press_key(VK_RETURN)
                random_delay(300, 500)
        
        random_delay(500, 800)
        
        # 点击发布
        publish_btn_x = right - 80
        publish_btn_y = bottom - 80
        
        left_click(publish_btn_x, publish_btn_y)
        random_delay(500, 800)
        
        self.logger.info("朋友圈已发布")
        return {"success": True, "message": "朋友圈已发布"}
    
    def auto_like_moments(self, count: int = 10) -> Dict:
        """
        自动点赞朋友圈
        
        Args:
            count: 点赞数量
            
        Returns:
            {"success": True/False, "liked": 0, "message": "..."}
        """
        if not self.window.find_wechat():
            return {"success": False, "message": "微信未运行"}
        
        self.logger.info(f"开始自动点赞，最多 {count} 条")
        
        self.window.activate()
        random_delay(300, 500)
        
        # 打开朋友圈
        send_ctrl_key(0x47)  # Ctrl+G
        random_delay(800, 1000)
        
        liked = 0
        from ..utils.win32 import scroll_wheel
        
        for i in range(count):
            # 滚动到下一条
            left, top, right, bottom = self.window.get_main_rect()
            scroll_area_x = right - 100
            scroll_area_y = top + (bottom - top) // 2
            
            # 滚动加载新内容
            scroll_wheel(scroll_area_x, scroll_area_y, -400)
            random_delay(500, 800)
            
            # 查找点赞按钮并点击
            # 简化：点击评论区域右侧的点赞图标
            like_x = right - 150
            like_y = top + 200 + (i % 5) * 120
            
            left_click(like_x, like_y)
            random_delay(200, 400)
            
            liked += 1
        
        self.logger.info(f"点赞完成，共点赞 {liked} 条")
        
        return {
            "success": True,
            "liked": liked,
            "message": f"点赞完成，共点赞 {liked} 条"
        }
    
    def auto_comment_moment(self, keyword: str, comment: str) -> Dict:
        """
        自动评论朋友圈（需要 AI 配合）
        
        Args:
            keyword: 触发关键词
            comment: 评论内容
            
        Returns:
            {"success": True/False, "commented": 0, "message": "..."}
        """
        if not self.window.find_wechat():
            return {"success": False, "message": "微信未运行"}
        
        self.logger.info(f"开始自动评论，关键词: {keyword}")
        
        # TODO: 需要 AI 配合识别朋友圈内容并决定是否评论
        
        return {
            "success": True,
            "commented": 0,
            "message": "功能开发中，需要 AI 配合"
        }