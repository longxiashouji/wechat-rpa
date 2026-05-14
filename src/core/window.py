# -*- coding: utf-8 -*-
"""
微信窗口管理模块 - 完全自研
负责查找、识别、操作微信窗口
"""

import time
import win32gui
import win32con
from typing import Optional, Tuple, List, Dict

from ..utils.win32 import (
    find_window, find_window_ex, set_foreground_window, 
    get_window_rect, get_window_text, get_window_class_name,
    enum_child_windows, send_message, press_key, VK_RETURN,
    left_click, set_cursor_pos, get_cursor_pos, scroll_wheel,
    find_child_window, WM_SETTEXT, EM_REPLACESEL
)
from ..utils.common import Logger, random_delay, wait_for_condition


class WeChatWindow:
    """微信窗口管理类"""
    
    # 微信窗口类名（通过 Spy++ 获取的实际类名）
    MAIN_WINDOW_CLASS = "WeChatMainWndForPC"
    CHAT_WINDOW_CLASS = "ChatWnd"
    EDITOR_CLASS = "RichEdit20W"
    SEARCH_CLASS = "Edit"
    
    def __init__(self):
        self.logger = Logger("WeChatWindow")
        self.main_hwnd: Optional[int] = None
        self.current_chat_hwnd: Optional[int] = None
        self._cache = {}
    
    def find_wechat(self) -> bool:
        """查找微信主窗口"""
        # 方法1：按类名查找
        self.main_hwnd = find_window(self.MAIN_WINDOW_CLASS, None)
        
        if not self.main_hwnd:
            # 方法2：按窗口名查找（备用）
            self.main_hwnd = find_window(None, "微信")
        
        if not self.main_hwnd:
            # 方法3：遍历所有窗口
            self.main_hwnd = self._find_wechat_by_process()
        
        if self.main_hwnd:
            self.logger.info(f"找到微信主窗口: {self.main_hwnd}")
            return True
        
        self.logger.warn("未找到微信主窗口")
        return False
    
    def _find_wechat_by_process(self) -> Optional[int]:
        """通过进程名查找微信窗口"""
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'WeChat' in proc.info['name']:
                    # 找到进程，遍历其窗口
                    def callback(hwnd, _):
                        if get_window_class_name(hwnd) == self.MAIN_WINDOW_CLASS:
                            return False  # 找到就停止
                        return True  # 继续找
                    
                    # 枚举所有窗口找微信
                    result = [0]
                    def enum_callback(hwnd, _):
                        class_name = get_window_class_name(hwnd)
                        if class_name and ('WeChat' in class_name or 'Chat' in class_name):
                            result[0] = hwnd
                            return False
                        return True
                    
                    try:
                        win32gui.EnumWindows(enum_callback, None)
                        if result[0]:
                            return result[0]
                    except:
                        pass
            except:
                pass
        return None
    
    def is_wechat_running(self) -> bool:
        """检查微信是否在运行"""
        if not self.main_hwnd:
            return self.find_wechat()
        
        # 检查窗口是否有效
        try:
            return win32gui.IsWindowVisible(self.main_hwnd)
        except:
            return False
    
    def activate(self) -> bool:
        """激活微信窗口（置前）"""
        if not self.main_hwnd:
            if not self.find_wechat():
                return False
        
        result = set_foreground_window(self.main_hwnd)
        if result:
            self.logger.debug("微信窗口已激活")
        return result
    
    def get_main_rect(self) -> Tuple[int, int, int, int]:
        """获取主窗口区域"""
        if not self.main_hwnd:
            return (0, 0, 0, 0)
        return get_window_rect(self.main_hwnd)
    
    def _find_control(self, parent: int, class_name: str = None, 
                      window_name: str = None, index: int = 0) -> Optional[int]:
        """在父窗口中查找控件"""
        hwnd = find_window_ex(parent, 0, class_name, window_name)
        
        # 如果指定了索引，继续往下找
        for _ in range(index):
            hwnd = find_window_ex(parent, hwnd, class_name, window_name)
        
        return hwnd
    
    def _find_child_by_class(self, parent: int, class_name: str, 
                             deep: bool = True) -> List[int]:
        """查找所有匹配类名的子窗口"""
        results = []
        
        def callback(hwnd, _):
            if get_window_class_name(hwnd) == class_name:
                results.append(hwnd)
            if deep:
                try:
                    win32gui.EnumChildWindows(hwnd, callback, None)
                except:
                    pass
            return True
        
        try:
            win32gui.EnumChildWindows(parent, callback, None)
        except:
            pass
        
        return results
    
    def _find_child_by_text(self, parent: int, text: str, 
                            exact: bool = False) -> Optional[int]:
        """通过文本查找子窗口"""
        all_childs = []
        
        def callback(hwnd, _):
            all_childs.append(hwnd)
            return True
        
        try:
            win32gui.EnumChildWindows(parent, callback, None)
        except:
            pass
        
        for hwnd in all_childs:
            try:
                wnd_text = get_window_text(hwnd)
                if wnd_text:
                    if exact:
                        if text in wnd_text:
                            return hwnd
                    else:
                        if text in wnd_text:
                            return hwnd
            except:
                pass
        
        return None
    
    def open_chat_by_search(self, name: str) -> bool:
        """通过搜索打开聊天窗口"""
        if not self.activate():
            return False
        
        time.sleep(0.2)
        
        # 获取主窗口大小
        left, top, right, bottom = self.get_main_rect()
        width = right - left
        height = bottom - top
        
        # 点击搜索图标（通常在左上角）
        # 搜索图标位置：主界面顶部居中偏左
        search_x = left + int(width * 0.15)
        search_y = top + int(height * 0.05)
        
        self.logger.info(f"点击搜索图标: ({search_x}, {search_y})")
        left_click(search_x, search_y)
        random_delay(100, 200)
        
        # 查找搜索输入框
        search_input_hwnd = None
        for _ in range(3):
            # 在主窗口中找 Edit 类型的输入框
            all_edits = self._find_child_by_class(self.main_hwnd, "Edit")
            if all_edits:
                search_input_hwnd = all_edits[0]
                break
            time.sleep(0.2)
        
        if not search_input_hwnd:
            # 尝试直接键盘输入（搜索框已聚焦）
            pass
        
        # 输入搜索内容
        time.sleep(0.2)
        
        # 清除已有内容
        press_key(0x11)  # Ctrl
        press_key(0x41)  # A
        random_delay(50, 100)
        press_key(0x08)  # Backspace
        
        # 输入搜索关键字
        self._input_text_to_window(search_input_hwnd or self.main_hwnd, name)
        random_delay(200, 400)
        
        # 按回车确认搜索
        press_key(VK_RETURN)
        random_delay(300, 500)
        
        # 再次按回车进入聊天
        press_key(VK_RETURN)
        random_delay(300, 500)
        
        # 记录当前聊天窗口
        self.current_chat_hwnd = self.main_hwnd
        
        self.logger.info(f"已打开与 {name} 的聊天")
        return True
    
    def _input_text_to_window(self, hwnd: int, text: str) -> None:
        """向窗口发送文本"""
        # 方法1: 使用剪贴板（最可靠）
        from ..utils.win32 import set_clipboard_text, send_ctrl_key
        import win32clipboard
        
        # 保存原剪贴板内容
        old_text = ""
        try:
            win32clipboard.OpenClipboard()
            old_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        except:
            pass
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        
        # 设置新文本到剪贴板
        set_clipboard_text(text)
        random_delay(50, 100)
        
        # Ctrl+V 粘贴
        send_ctrl_key(0x56)  # V
        random_delay(100, 200)
        
        # 恢复原剪贴板
        def restore():
            time.sleep(0.3)
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                if old_text:
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, old_text)
                win32clipboard.CloseClipboard()
            except:
                pass
        
        import threading
        threading.Thread(target=restore, daemon=True).start()
    
    def send_text_message(self, message: str) -> bool:
        """发送文本消息到当前聊天窗口"""
        if not self.activate():
            return False
        
        random_delay(100, 200)
        
        # 查找消息输入框
        input_hwnd = self._find_message_input()
        
        if not input_hwnd:
            self.logger.warn("未找到消息输入框，尝试直接发送")
            input_hwnd = self.current_chat_hwnd or self.main_hwnd
        
        # 发送文本
        self._input_text_to_window(input_hwnd, message)
        random_delay(100, 200)
        
        # 按回车发送
        press_key(VK_RETURN)
        
        self.logger.info("消息已发送")
        return True
    
    def _find_message_input(self) -> Optional[int]:
        """查找消息输入框"""
        # 方法1: 在主窗口中查找 Edit 类型的输入框
        all_edits = self._find_child_by_class(self.main_hwnd, "Edit")
        for edit in all_edits:
            rect = get_window_rect(edit)
            if rect[2] - rect[0] > 100:  # 宽度大于100的是可能的输入框
                return edit
        
        # 方法2: 查找 RichEdit 类型的输入框
        all_richedit = self._find_child_by_class(self.main_hwnd, "RichEdit20W")
        for edit in all_richedit:
            rect = get_window_rect(edit)
            if rect[2] - rect[0] > 100:
                return edit
        
        return None
    
    def get_ui_tree(self, hwnd: int = None) -> Dict:
        """获取窗口 UI 树结构（用于调试）"""
        if hwnd is None:
            hwnd = self.main_hwnd or 0
        
        tree = {
            "hwnd": hwnd,
            "class": get_window_class_name(hwnd),
            "text": get_window_text(hwnd),
            "rect": get_window_rect(hwnd),
            "children": []
        }
        
        def callback(child_hwnd, _):
            child_tree = self.get_ui_tree(child_hwnd)
            tree["children"].append(child_tree)
            return True
        
        try:
            win32gui.EnumChildWindows(hwnd, callback, None)
        except:
            pass
        
        return tree
    
    def dump_controls(self) -> List[Dict]:
        """导出窗口所有控件信息（用于调试）"""
        if not self.main_hwnd:
            return []
        
        controls = []
        
        def callback(hwnd, _):
            controls.append({
                "hwnd": hwnd,
                "class": get_window_class_name(hwnd),
                "text": get_window_text(hwnd),
                "rect": get_window_rect(hwnd)
            })
            return True
        
        try:
            win32gui.EnumChildWindows(self.main_hwnd, callback, None)
        except:
            pass
        
        return controls
    
    def screenshot(self, save_path: str = None) -> Optional[str]:
        """截取微信窗口"""
        import win32gui
        import win32ui
        import win32con
        from PIL import Image
        
        if not self.main_hwnd:
            return None
        
        left, top, right, bottom = get_window_rect(self.main_hwnd)
        width = right - left
        height = bottom - top
        
        # 创建设备上下文
        hwndDC = win32gui.GetWindowDC(self.main_hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        # 创建位图
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        
        # 复制窗口内容
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        
        # 保存到文件
        if save_path is None:
            import time
            save_path = f"screenshot_{int(time.time())}.png"
        
        saveBitMap.SaveBitmapFile(saveDC, save_path)
        
        # 清理
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.main_hwnd, hwndDC)
        
        return save_path