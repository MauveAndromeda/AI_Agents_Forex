#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================================================================
AI Agents Forex - 统一回测入口
===================================================================================

这是项目的主入口，会自动引导你选择最合适的回测模式。

快速开始：
    python run_backtest.py

===================================================================================
"""

import sys
from pathlib import Path

print("="*80)
print("AI Agents Forex - 智能外汇交易回测系统")
print("="*80)
print()

print("欢迎！请选择回测模式：")
print()
print("  [1] 🚀 真实回测 5 年增强版（推荐）")
print("      • 支持真实 MT5 历史数据")
print("      • 智能自适应学习系统")
print("      • 详细调试日志")
print("      • 最多 5 年数据回测")
print()
print("  [2] ⚡ 高速并发回测版")
print("      • 并发 API 调用（10-100倍速）")
print("      • 智能缓存系统")
print("      • 支持纯量化模式")
print()
print("  [3] 📊 标准回测版")
print("      • 完整 8 组件系统")
print("      • 适合快速测试")
print("      • 90 天回测")
print()
print("  [4] 🔍 检查 API 密钥配置")
print("      • 查看 API 密钥位置")
print("      • 诊断配置问题")
print()
print("  [0] 退出")
print()

try:
    choice = input("请选择 [0-4]: ").strip()
    print()

    if choice == '1':
        print("✓ 启动真实回测 5 年增强版...")
        print()
        exec(open("真实回测_5年增强版.py", encoding='utf-8').read())

    elif choice == '2':
        print("✓ 启动高速并发回测版...")
        print()
        exec(open("一键回测_高速版.py", encoding='utf-8').read())

    elif choice == '3':
        print("✓ 启动标准回测版...")
        print()
        exec(open("一键回测完整版.py", encoding='utf-8').read())

    elif choice == '4':
        print("✓ 启动 API 密钥检查工具...")
        print()
        exec(open("check_api_key.py", encoding='utf-8').read())

    elif choice == '0':
        print("👋 再见！")
        sys.exit(0)

    else:
        print("❌ 无效选择，请重试")
        sys.exit(1)

except FileNotFoundError as e:
    print(f"❌ 错误: 找不到脚本文件")
    print(f"   {e}")
    print()
    print("请确保你在项目根目录运行此脚本。")
    sys.exit(1)

except KeyboardInterrupt:
    print()
    print("⚠ 用户取消")
    sys.exit(1)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
