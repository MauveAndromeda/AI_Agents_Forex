@echo off
REM ============================================================================
REM AI Agents Forex - Windows 自动安装脚本
REM ============================================================================
REM 
REM 这个脚本会：
REM 1. 自动检测并创建虚拟环境
REM 2. 自动安装所有依赖
REM 3. 自动运行回测
REM 
REM 使用方法：双击运行即可！
REM ============================================================================

echo ================================================================================
echo AI Agents Forex - 自动安装脚本
echo ================================================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.8+ 
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python 已安装
echo.

REM 检查是否已有虚拟环境
if exist venv (
    echo ✓ 虚拟环境已存在
) else (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✓ 虚拟环境创建成功
)

echo.
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 正在安装依赖...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ✓ 所有准备工作完成！
echo.
echo ================================================================================
echo 正在启动回测系统...
echo ================================================================================
echo.

python run_backtest.py

pause
