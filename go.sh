@echo off
chcp 65001 >nul
setlocal

REM ===== 卫星壁纸网页设置面板启动脚本 =====
REM 双击本文件：若服务已在运行则仅打开浏览器，否则启动服务并自动打开浏览器。
REM 关闭弹出的命令行窗口即停止服务。

set "URL=http://127.0.0.1:7788/"

REM 检测端口是否已被占用
netstat -ano | findstr ":7788" | findstr "LISTENING" >nul
if not errorlevel 1 (
    start "" "%URL%"
    exit /b 0
)

REM 在项目目录内启动服务（防止相对路径错误）
cd /d "%~dp0"
start "SLW 设置面板" "D:\Program\miniconda3\python.exe" slw_frontend.py
exit /b 0
