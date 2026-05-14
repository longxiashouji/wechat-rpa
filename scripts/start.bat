@echo off
chcp 65001 >nul
echo ========================================
echo   微信 RPA 机器人 - 启动中
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [2/3] 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
)

echo [3/3] 启动服务...
python -m src.web.server

pause