@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   微信 RPA 机器人 - 服务停止脚本
echo ========================================
echo.

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo 正在停止 RPA 服务...
python scripts\stop_server.py

if errorlevel 1 (
    echo.
    echo [提示] 服务可能未运行或已停止
) else (
    echo.
    echo [成功] RPA 服务已停止！
)

echo.
pause