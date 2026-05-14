# -*- coding: utf-8 -*-
"""
通讯录服务模块 - 完全自研
负责获取通讯录、同步好友等
"""

import time
from typing import List, Dict, Optional

from ..core.window import WeChatWindow
from ..utils.common import Logger, random_delay


class ContactService:
    """通讯录服务类"""
    
    def __init__(self, window: WeChatWindow = None):
        self.window = window or WeChatWindow()
        self.logger = Logger("ContactService")
        self._contacts_cache = []
    
    def get_contacts(self, refresh: bool = False) -> List[Dict]:
        """
        获取通讯录
        
        注意：微信桌面版通讯录获取需要特定操作路径
        这里通过模拟 UI 操作来获取
        
        Returns:
            [{"name": "张三", "wxid": "xxx", "remark": "备注", "tag": "同事"}, ...]
        """
        if not self._contacts_cache or refresh:
            self._contacts_cache = self._fetch_contacts()
        
        return self._contacts_cache
    
    def _fetch_contacts(self) -> List[Dict]:
        """实际获取通讯录（通过 UI 操作）"""
        if not self.window.find_wechat():
            return []
        
        self.logger.info("正在获取通讯录...")
        
        # 点击通讯录标签
        self.window.activate()
        random_delay(200, 300)
        
        left, top, right, bottom = self.window.get_main_rect()
        width = right - left
        height = bottom - top
        
        # 通讯录入口位置（左侧边栏）
        contact_x = left + int(width * 0.05)
        contact_y = top + int(height * 0.25)
        
        from ..utils.win32 import left_click
        left_click(contact_x, contact_y)
        random_delay(500, 800)
        
        # 通讯录加载后，需要滚动获取
        contacts = []
        
        # 模拟滚动加载
        for _ in range(3):
            from ..utils.win32 import scroll_wheel
            scroll_wheel(right - 50, top + height // 2, -300)
            random_delay(200, 400)
        
        # 通过截图+AI 解析方式获取
        # 这里仅记录，实际需要 AI/OCR 参与
        screenshot = self.window.screenshot()
        
        self.logger.info(f"通讯录截图已保存: {screenshot}")
        
        return contacts
    
    def sync_contacts(self) -> Dict:
        """
        同步通讯录
        
        Returns:
            {"success": True/False, "count": 0, "message": "..."}
        """
        if not self.window.find_wechat():
            return {"success": False, "message": "微信未运行"}
        
        self.logger.info("正在同步通讯录...")
        
        # 点击通讯录
        self.window.activate()
        random_delay(200, 300)
        
        # 滚动通讯录触发加载
        left, top, right, bottom = self.window.get_main_rect()
        scroll_area_x = right - 100
        scroll_area_y = top + (bottom - top) // 2
        
        from ..utils.win32 import scroll_wheel
        
        for i in range(5):
            scroll_wheel(scroll_area_x, scroll_area_y, -200)
            random_delay(300, 500)
        
        # 获取完整通讯录
        self._contacts_cache = self._fetch_contacts()
        
        return {
            "success": True,
            "count": len(self._contacts_cache),
            "message": f"同步完成，共 {len(self._contacts_cache)} 个联系人"
        }
    
    def search_contact(self, keyword: str) -> Optional[Dict]:
        """
        搜索联系人
        
        Args:
            keyword: 关键词（备注名/昵称/微信号）
            
        Returns:
            联系人信息或 None
        """
        contacts = self.get_contacts()
        
        keyword_lower = keyword.lower()
        for contact in contacts:
            if (keyword_lower in contact.get("name", "").lower() or
                keyword_lower in contact.get("remark", "").lower() or
                keyword_lower in contact.get("wxid", "").lower()):
                return contact
        
        return None
    
    def get_contact_info(self, name: str) -> Optional[Dict]:
        """
        获取联系人详细信息
        
        Args:
            name: 联系人名称
            
        Returns:
            联系人详细信息
        """
        # 打开联系人聊天窗口
        if not self.window.open_chat_by_search(name):
            return None
        
        # 点击头像获取更多信息
        random_delay(500, 800)
        
        left, top, right, bottom = self.window.get_main_rect()
        
        # 头像位置（右上角）
        avatar_x = right - 80
        avatar_y = top + 80
        
        from ..utils.win32 import left_click
        left_click(avatar_x, avatar_y)
        random_delay(500, 800)
        
        # 截图保存信息
        screenshot = self.window.screenshot()
        
        return {
            "name": name,
            "screenshot": screenshot,
            "message": "详细信息需查看截图"
        }