#!/usr/bin/env python3
"""
微信 RPA 机器人 - 服务启动脚本
用于启动 RPA 后端服务 (service.exe)
"""

import os
import sys
import subprocess
import time
import socket
import psutil

SERVICE_PORT = 9922
SERVICE_HOST = '127.0.0.1'


def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((SERVICE_HOST, port))
            return True
        except (ConnectionRefusedError, OSError):
            return False


def find_process_by_port(port: int) -> list:
    """查找占用指定端口的进程"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.net_connections():
                if conn.laddr.port == port:
                    processes.append(proc)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes


def kill_processes_on_port(port: int) -> None:
    """杀死占用指定端口的进程"""
    procs = find_process_by_port(port)
    for proc in procs:
        try:
            print(f"  正在终止进程: {proc.name()} (PID: {proc.pid})")
            proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"  无法终止进程: {e}")


def wait_for_service_ready(timeout: int = 30) -> bool:
    """等待服务就绪"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(SERVICE_PORT):
            # 尝试 HTTP 请求确认服务就绪
            try:
                import requests
                resp = requests.get(
                    f'http://{SERVICE_HOST}:{SERVICE_PORT}/docs',
                    timeout=5,
                    proxies={"http": None, "https": None}
                )
                if resp.status_code == 200:
                    print("  ✓ RPA 服务已就绪")
                    return True
            except Exception:
                pass
        time.sleep(1)
    return False


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    service_exe = os.path.join(root_dir, '..', '..', 'service.exe')

    if not os.path.exists(service_exe):
        service_exe = os.path.join(root_dir, '..', 'service.exe')

    print("=" * 50)
    print("  微信 RPA 机器人 - 服务启动")
    print("=" * 50)
    print()

    # 检查端口占用
    print("[1/4] 检查端口占用...")
    if is_port_in_use(SERVICE_PORT):
        print(f"  端口 {SERVICE_PORT} 已被占用，正在清理...")
        kill_processes_on_port(SERVICE_PORT)
        time.sleep(2)

    # 检查 service.exe
    print("[2/4] 检查 RPA 后端...")
    if not os.path.exists(service_exe):
        service_exe = os.path.join(root_dir, 'service.exe')

    if not os.path.exists(service_exe):
        print(f"  ✗ 未找到 service.exe")
        print(f"  请从以下地址下载并放置到项目根目录:")
        print(f"  https://github.com/LeoMusk/wechat-rpa-bot-skill/releases")
        return False

    print(f"  ✓ 找到: {service_exe}")

    # 设置环境变量
    print("[3/4] 配置环境变量...")
    env = os.environ.copy()
    env['WEBOT_BACKEND_MODE'] = '1'
    env['HEADLESS_MODE'] = '1'
    env['DISABLE_WEBVIEW'] = '1'
    env['NO_BROWSER'] = '1'

    # 启动服务
    print("[4/4] 启动 RPA 服务...")
    try:
        subprocess.Popen(
            [service_exe],
            env=env,
            cwd=os.path.dirname(service_exe),
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        print("  ✓ service.exe 已启动")
    except Exception as e:
        print(f"  ✗ 启动失败: {e}")
        return False

    # 等待服务就绪
    print()
    print("  等待服务初始化...")
    if wait_for_service_ready():
        print()
        print("=" * 50)
        print("  ✓ 微信 RPA 服务启动成功！")
        print(f"  请访问: http://{SERVICE_HOST}:{SERVICE_PORT}/")
        print("=" * 50)
        return True
    else:
        print()
        print("  ✗ 服务启动超时，请检查:")
        print("  1. 微信 4.1.7 是否已安装并登录")
        print("  2. service.exe 是否完整")
        print("  3. 是否有杀毒软件阻止")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)