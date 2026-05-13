#!/usr/bin/env python3
"""
微信 RPA 机器人 - 服务停止脚本
用于停止 RPA 后端服务 (service.exe)
"""

import os
import sys
import socket
import psutil
import time


def find_rpa_processes() -> list:
    """查找 RPA 相关进程"""
    rpa_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.name().lower()
            cmdline = ' '.join(proc.cmdline()).lower() if proc.cmdline() else ''

            if 'service' in name or 'service.exe' in cmdline:
                rpa_procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return rpa_procs


def kill_process(proc) -> bool:
    """尝试杀死进程"""
    try:
        proc.kill()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def main():
    print("=" * 50)
    print("  微信 RPA 机器人 - 服务停止")
    print("=" * 50)
    print()

    # 查找 RPA 进程
    print("[1/2] 查找 RPA 进程...")
    rpa_procs = find_rpa_processes()

    if not rpa_procs:
        print("  未找到 RPA 服务进程")
        print()
        print("=" * 50)
        print("  ✓ 服务可能已停止或未运行")
        print("=" * 50)
        return True

    print(f"  找到 {len(rpa_procs)} 个 RPA 进程")

    # 终止进程
    print("[2/2] 停止 RPA 服务...")
    killed = []
    for proc in rpa_procs:
        try:
            print(f"  终止: {proc.name()} (PID: {proc.pid})")
            if kill_process(proc):
                killed.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"  无法终止: {e}")

    # 等待进程退出
    time.sleep(1)

    # 检查是否还有残留
    still_running = []
    for proc in rpa_procs:
        try:
            if proc.is_running():
                still_running.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    print()
    if still_running:
        print("  以下进程可能需要手动停止:")
        for proc in still_running:
            print(f"    - {proc.name()} (PID: {proc.pid})")
        print("  请打开任务管理器手动结束")
    else:
        print("=" * 50)
        print("  ✓ RPA 服务已停止")
        print("=" * 50)

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)