@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   微信 RPA 机器人 - 服务启动脚本
echo ========================================
echo.

REM 设置项目根目录
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

REM 清理旧进程
echo [1/3] 正在清理旧进程...
python scripts\stop_server.py >nul 2>&1
if errorlevel 1 (
    echo       清理完成（或无需清理）
)

REM 检查 Python
echo [2/3] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 安装依赖
echo [3/3] 安装依赖（如需要）...
pip install psutil requests --quiet --no-warn-script-location
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

REM 启动服务
echo.
echo ========================================
echo   正在启动 RPA 服务...
echo ========================================
echo.

set WEBOT_BACKEND_MODE=1
set HEADLESS_MODE=1
set DISABLE_WEBVIEW=1
set NO_BROWSER=1

python scripts\start_server.py

echo.
echo ========================================
echo   服务已启动！
echo   请访问: http://127.0.0.1:9922/
echo   如需停止，请双击"停止微信RPA.bat"
echo ========================================
echo.

pause