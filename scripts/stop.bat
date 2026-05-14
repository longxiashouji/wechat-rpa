@echo off
chcp 65001 >nul
echo ========================================
echo   微信 RPA 机器人 - 停止
echo ========================================
echo.

:: 通过端口号查找并结束进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9922 ^| findstr LISTENING') do (
    echo 正在停止 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo 已停止服务
pause