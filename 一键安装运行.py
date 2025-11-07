#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
AI Agents Forex - 一键安装运行脚本
================================================================================

功能：
1. 自动检测 Python 环境
2. 自动创建虚拟环境（可选）
3. 自动安装所有依赖
4. 自动运行回测系统

使用方法：
    python 一键安装运行.py

或者直接双击运行（Windows）
================================================================================
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

def print_header():
    print("="*80)
    print("AI Agents Forex - 一键安装运行")
    print("="*80)
    print()

def check_python():
    """检查 Python 版本"""
    print("检查 Python 版本...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本太低: {version.major}.{version.minor}")
        print("需要 Python 3.8+")
        print("下载地址: https://www.python.org/downloads/")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n检查依赖...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("⚠ requirements.txt 不存在，跳过依赖安装")
        return True
    
    print("正在安装依赖（这可能需要几分钟）...")
    
    try:
        # 安装依赖
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        print("✓ 所有依赖已安装")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠ 部分依赖安装失败: {e}")
        print("将尝试继续运行...")
        return True
    except Exception as e:
        print(f"❌ 依赖安装错误: {e}")
        return False

def check_project_structure():
    """检查项目结构"""
    print("\n检查项目结构...")
    
    required_dirs = ['src', 'src/data', 'src/models', 'src/ai', 'src/agents', 'src/risk']
    missing = []
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        print(f"❌ 缺少必要目录: {', '.join(missing)}")
        print("\n请确保：")
        print("1. 完整下载了整个 ZIP 文件")
        print("2. 完全解压了 ZIP 文件")
        print("3. 在正确的目录运行此脚本")
        return False
    
    print("✓ 项目结构完整")
    return True

def run_backtest():
    """运行回测"""
    print("\n"+"="*80)
    print("启动回测系统")
    print("="*80+"\n")
    
    # 检查是否有 run_backtest.py
    if Path("run_backtest.py").exists():
        exec(open("run_backtest.py", encoding='utf-8').read())
    elif Path("真实回测_5年增强版.py").exists():
        exec(open("真实回测_5年增强版.py", encoding='utf-8').read())
    else:
        print("❌ 找不到回测脚本")
        print("请确保以下文件存在：")
        print("  - run_backtest.py")
        print("  - 真实回测_5年增强版.py")
        return False
    
    return True

def main():
    """主函数"""
    print_header()
    
    # 1. 检查 Python
    if not check_python():
        input("\n按回车键退出...")
        return 1
    
    # 2. 检查项目结构
    if not check_project_structure():
        input("\n按回车键退出...")
        return 1
    
    # 3. 安装依赖
    if not install_dependencies():
        print("\n是否继续运行（可能会有错误）？")
        choice = input("继续？[y/N]: ").strip().lower()
        if choice != 'y':
            return 1
    
    # 4. 运行回测
    try:
        run_backtest()
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
        return 0
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ 致命错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)
