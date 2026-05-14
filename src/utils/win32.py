# -*- coding: utf-8 -*-
"""
Win32 API 封装模块 - 完全自研
提供 Windows 系统级 API 调用：鼠标、键盘、窗口、剪贴板等
"""

import ctypes
import time
import win32gui
import win32con
import win32api
import win32clipboard
from typing import Optional, Tuple


# ==================== 鼠标操作 ====================
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_WHEEL = 0x0800


def set_cursor_pos(x: int, y: int) -> None:
    """设置鼠标位置"""
    ctypes.windll.user32.SetCursorPos(x, y)


def get_cursor_pos() -> Tuple[int, int]:
    """获取鼠标位置"""
    point = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


def left_click(x: int, y: int, delay: float = 0.05) -> None:
    """左键点击指定坐标"""
    set_cursor_pos(x, y)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(delay)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def left_double_click(x: int, y: int) -> None:
    """左键双击指定坐标"""
    left_click(x, y, 0.02)
    time.sleep(0.05)
    left_click(x, y, 0.02)


def right_click(x: int, y: int) -> None:
    """右键点击指定坐标"""
    set_cursor_pos(x, y)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def scroll_wheel(x: int, y: int, delta: int = 120) -> None:
    """滚动鼠标滚轮"""
    set_cursor_pos(x, y)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)


def drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int, steps: int = 10) -> None:
    """鼠标拖拽"""
    set_cursor_pos(start_x, start_y)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    
    for i in range(steps + 1):
        x = int(start_x + (end_x - start_x) * i / steps)
        y = int(start_y + (end_y - start_y) * i / steps)
        set_cursor_pos(x, y)
        time.sleep(0.02)
    
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


# ==================== 键盘操作 ====================
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001


def key_down(vk_code: int) -> None:
    """按下按键"""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)


def key_up(vk_code: int) -> None:
    """释放按键"""
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def press_key(vk_code: int, delay: float = 0.05) -> None:
    """按下并释放一个按键"""
    key_down(vk_code)
    time.sleep(delay)
    key_up(vk_code)


def send_ctrl_key(vk_code: int) -> None:
    """发送 Ctrl + 按键组合"""
    key_down(0x11)  # VK_CONTROL
    time.sleep(0.02)
    key_down(vk_code)
    time.sleep(0.02)
    key_up(vk_code)
    time.sleep(0.02)
    key_up(0x11)


def send_text(text: str) -> None:
    """发送文本（通过剪贴板粘贴）"""
    # 保存当前剪贴板内容
    old_clipboard = ""
    try:
        win32clipboard.OpenClipboard()
        old_clipboard = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    except:
        pass
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
    
    # 设置新内容
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()
    
    time.sleep(0.05)
    
    # Ctrl+V 粘贴
    send_ctrl_key(0x56)  # V
    
    time.sleep(0.05)
    
    # 恢复原剪贴板内容（异步恢复，避免影响后续操作）
    def restore_clipboard():
        time.sleep(0.3)
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            if old_clipboard:
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, old_clipboard)
            win32clipboard.CloseClipboard()
        except:
            pass
    
    import threading
    threading.Thread(target=restore_clipboard, daemon=True).start()


# ==================== 窗口操作 ====================

def find_window(class_name: Optional[str] = None, window_name: Optional[str] = None) -> Optional[int]:
    """查找窗口句柄"""
    return win32gui.FindWindow(class_name, window_name)


def find_window_ex(parent: int, after: int, class_name: Optional[str], window_name: Optional[str]) -> Optional[int]:
    """查找子窗口"""
    return win32gui.FindWindowEx(parent, after, class_name, window_name)


def get_window_text(hwnd: int) -> str:
    """获取窗口标题"""
    try:
        length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
        buffer = win32gui.PyGetBuffer(hwnd, length)
        return win32gui.PyGetString(hwnd, length - 1)
    except:
        return ""


def set_window_text(hwnd: int, text: str) -> None:
    """设置窗口标题"""
    win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)


def set_foreground_window(hwnd: int) -> bool:
    """将窗口置前"""
    try:
        # 先尝试 AttachThreadInput 解决跨线程问题
        target_tid = win32gui.GetWindowThreadProcessId(hwnd)[0]
        current_tid = win32api.GetCurrentThreadId()
        if target_tid != current_tid:
            ctypes.windll.user32.AttachThreadInput(current_tid, target_tid, True)
            win32gui.SetForegroundWindow(hwnd)
            ctypes.windll.user32.AttachThreadInput(current_tid, target_tid, False)
        else:
            win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        print(f"SetForegroundWindow failed: {e}")
        return False


def show_window(hwnd: int, show_cmd: int = win32con.SW_SHOW) -> None:
    """显示/隐藏窗口"""
    win32gui.ShowWindow(hwnd, show_cmd)


def maximize_window(hwnd: int) -> None:
    """最大化窗口"""
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


def restore_window(hwnd: int) -> None:
    """还原窗口"""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """获取窗口矩形区域 (left, top, right, bottom)"""
    try:
        return win32gui.GetWindowRect(hwnd)
    except:
        return (0, 0, 0, 0)


def get_client_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """获取窗口客户区矩形"""
    try:
        return win32gui.GetClientRect(hwnd)
    except:
        return (0, 0, 0, 0)


def window_to_screen(hwnd: int, x: int, y: int) -> Tuple[int, int]:
    """将窗口内坐标转换为屏幕坐标"""
    point = ctypes.wintypes.POINT(x, y)
    ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(point))
    return point.x, point.y


def screen_to_window(hwnd: int, x: int, y: int) -> Tuple[int, int]:
    """将屏幕坐标转换为窗口内坐标"""
    point = ctypes.wintypes.POINT(x, y)
    ctypes.windll.user32.ScreenToClient(hwnd, ctypes.byref(point))
    return point.x, point.y


def get_foreground_window() -> int:
    """获取当前焦点窗口"""
    return win32gui.GetForegroundWindow()


def get_window_class_name(hwnd: int) -> str:
    """获取窗口类名"""
    try:
        return win32gui.GetClassName(hwnd)
    except:
        return ""


def enum_child_windows(hwnd: int) -> list:
    """枚举所有子窗口"""
    windows = []
    
    def callback(h, _):
        windows.append(h)
        return True
    
    try:
        win32gui.EnumChildWindows(hwnd, callback, None)
    except:
        pass
    
    return windows


def find_child_window(parent: int, class_name: str = None, window_name: str = None) -> Optional[int]:
    """在父窗口中查找子窗口"""
    return win32gui.FindWindowEx(parent, 0, class_name, window_name)


def send_message(hwnd: int, msg: int, wparam: int = 0, lparam: int = 0) -> int:
    """发送消息到窗口"""
    return win32gui.SendMessage(hwnd, msg, wparam, lparam)


def post_message(hwnd: int, msg: int, wparam: int = 0, lparam: int = 0) -> bool:
    """投递消息到窗口消息队列"""
    return win32gui.PostMessage(hwnd, msg, wparam, lparam)


# ==================== 进程操作 ====================

def find_process(name: str) -> list:
    """查找进程，返回 [(pid, exe_path), ...]"""
    import psutil
    results = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['name'] == name:
                results.append((proc.info['pid'], proc.info['exe']))
        except:
            pass
    return results


def get_process_path(pid: int) -> str:
    """获取进程路径"""
    import psutil
    try:
        return psutil.Process(pid).exe()
    except:
        return ""


# ==================== 剪贴板操作 ====================

def get_clipboard_text() -> str:
    """获取剪贴板文本"""
    text = ""
    try:
        win32clipboard.OpenClipboard()
        text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    except:
        pass
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
    return text


def set_clipboard_text(text: str) -> None:
    """设置剪贴板文本"""
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass


# ==================== Win32 常量 ====================

# 虚拟键码
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_TAB = 0x09
VK_DELETE = 0x2E
VK_BACK = 0x08
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28

# 窗口显示命令
SW_HIDE = 0
SW_SHOW = 5
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9

# 消息
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
EM_REPLACESEL = 0x00C2
EM_GETSEL = 0x00B0
EM_SETSEL = 0x00B1