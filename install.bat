@echo off
chcp 65001 >nul
title DentalPilot AI - 一键安装与启动

echo.
echo ============================================================
echo   DentalPilot AI - 口腔影像分析工具
echo   一键安装与启动脚本
echo ============================================================
echo.

REM ============ 步骤 1：检测 Python ============
echo [1/6] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] 未检测到 Python，请先安装 Python 3.10+
    echo     下载地址: https://www.python.org/downloads/
    echo     安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)
python --version
echo.

REM ============ 步骤 2：检测 Git ============
echo [2/6] 检查 Git 环境...
git --version >nul 2>&1
if errorlevel 1 (
    echo [X] 未检测到 Git，请先安装 Git
    echo     下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)
git --version
echo.

REM ============ 步骤 3：进入项目目录 ============
echo [3/6] 进入项目目录 E:\口腔影像aov...
cd /d E:\口腔影像aov
if not exist "%CD%" (
    echo [X] 目录不存在: E:\口腔影像aov
    pause
    exit /b 1
)

REM ============ 步骤 4：拉取代码 ============
echo [4/6] 拉取 GitHub 代码...
if not exist ".git" (
    git clone https://github.com/air199009/pin-guan-oral.git temp_clone
    xcopy /E /I /Y temp_clone\* .
    xcopy /E /I /Y temp_clone\.env.example .
    rmdir /S /Q temp_clone
) else (
    git pull origin main
)
echo.

REM ============ 步骤 5：安装依赖 ============
echo [5/6] 安装 Python 依赖（首次需要 2-3 分钟）...
pip install -r requirements.txt --break-system-packages
echo.

REM ============ 步骤 6：配置 .env ============
echo [6/6] 配置环境变量...
if not exist ".env" (
    copy .env.example .env >nul
    echo.
    echo ============================================================
    echo   需要你填入 Minimax API Key
    echo   请在打开的记事本里把 MINIMAX_API_KEY= 后填上你的 key
    echo   填好后按 Ctrl+S 保存，关闭记事本
    echo ============================================================
    echo.
    notepad .env
    echo 按任意键继续启动服务...
    pause >nul
) else (
    echo .env 已存在，跳过编辑
    echo.
)

echo.
echo ============================================================
echo   准备启动 DentalPilot AI 服务...
echo   启动后浏览器会自动打开 http://127.0.0.1:7860
echo   关闭此窗口即可停止服务
echo ============================================================
echo.

python app.py

pause
