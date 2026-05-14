# -*- coding: utf-8 -*-
"""
通用工具模块
"""

import time
import random
import hashlib
from typing import Optional, Callable
from functools import wraps


def generate_machine_code() -> str:
    """生成机器码（基于CPU、主板、磁盘等硬件信息）"""
    import psutil
    
    # 组合多个硬件标识
    parts = []
    
    # CPU ID
    try:
        cpu_id = hashlib.md5(psutil.cpu_freq().__str__().encode()).hexdigest()[:8]
        parts.append(cpu_id)
    except:
        pass
    
    # 主板序列号（通过cmd）
    import subprocess
    try:
        result = subprocess.run(
            ['wmic', 'baseboard', 'get', 'SerialNumber'],
            capture_output=True, text=True, timeout=2
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            serial = lines[1].strip()
            if serial and serial != 'SerialNumber':
                parts.append(hashlib.md5(serial.encode()).hexdigest()[:8])
    except:
        pass
    
    # 磁盘序列号
    try:
        result = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'SerialNumber'],
            capture_output=True, text=True, timeout=2
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            serial = lines[1].strip()
            if serial:
                parts.append(hashlib.md5(serial.encode()).hexdigest()[:8])
    except:
        pass
    
    # 合并生成机器码
    if not parts:
        parts = [str(time.time())]
    
    return '-'.join(parts[:4])


def retry(max_attempts: int = 3, delay: float = 0.5, exceptions: tuple = (Exception,)):
    """重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator


def random_delay(min_ms: int = 50, max_ms: int = 150) -> None:
    """随机延迟，模拟人类操作"""
    delay = random.randint(min_ms, max_ms) / 1000.0
    time.sleep(delay)


def wait_for_condition(condition: Callable[[], bool], timeout: float = 10, 
                       interval: float = 0.3, default: bool = False) -> bool:
    """等待条件满足"""
    start = time.time()
    while time.time() - start < timeout:
        if condition():
            return True
        time.sleep(interval)
    return default


def get_timestamp() -> int:
    """获取当前时间戳（秒）"""
    return int(time.time())


def get_timestamp_ms() -> int:
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)


def format_timestamp(ts: int = None) -> str:
    """格式化时间戳为可读字符串"""
    if ts is None:
        ts = get_timestamp()
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def safe_run(func: Callable, default=None, exceptions: tuple = (Exception,)):
    """安全执行函数，返回默认值"""
    try:
        return func()
    except exceptions:
        return default


def log(msg: str, level: str = "INFO") -> None:
    """统一日志输出"""
    timestamp = format_timestamp()
    print(f"[{timestamp}] [{level}] {msg}")


class Logger:
    """日志记录器"""
    
    def __init__(self, tag: str = "WeChatRPA"):
        self.tag = tag
    
    def info(self, msg: str) -> None:
        log(f"[{self.tag}] {msg}", "INFO")
    
    def warn(self, msg: str) -> None:
        log(f"[{self.tag}] {msg}", "WARN")
    
    def error(self, msg: str) -> None:
        log(f"[{self.tag}] {msg}", "ERROR")
    
    def debug(self, msg: str) -> None:
        log(f"[{self.tag}] {msg}", "DEBUG")