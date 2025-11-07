#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 API 密钥配置位置
"""

import os
from pathlib import Path

print("=" * 80)
print("API 密钥配置检查工具")
print("=" * 80)

# 1. 检查环境变量
print("\n1️⃣  检查环境变量:")
env_key = os.getenv('OPENAI_API_KEY')
if env_key:
    masked_key = f"{env_key[:10]}...{env_key[-4:]}"
    print(f"   ✓ 找到 OPENAI_API_KEY: {masked_key}")
    print(f"   📍 来源: 环境变量")
else:
    print("   ✗ 未找到环境变量 OPENAI_API_KEY")

# 2. 检查 .env 文件
print("\n2️⃣  检查 .env 文件:")
env_file = Path('.env')
if env_file.exists():
    print(f"   ✓ 找到 .env 文件: {env_file.absolute()}")

    try:
        content = env_file.read_text(encoding='utf-8')
        lines = content.strip().split('\n')

        found_keys = []
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                if 'API_KEY' in line:
                    key_name = line.split('=')[0].strip()
                    key_value = line.split('=')[1].strip() if '=' in line else ''
                    if key_value:
                        masked = f"{key_value[:10]}...{key_value[-4:]}" if len(key_value) > 14 else "***"
                        found_keys.append(f"      • {key_name} = {masked}")

        if found_keys:
            print("   📝 找到以下密钥:")
            for key in found_keys:
                print(key)
        else:
            print("   ⚠ .env 文件存在但未找到 API 密钥")

    except Exception as e:
        print(f"   ⚠ 读取 .env 文件失败: {e}")
else:
    print("   ✗ 未找到 .env 文件")

# 3. 检查虚拟环境激活脚本
print("\n3️⃣  检查虚拟环境:")
venv_paths = [
    Path('.venv/Scripts/activate.ps1'),  # Windows PowerShell
    Path('.venv/Scripts/activate.bat'),  # Windows CMD
    Path('.venv/bin/activate'),          # Linux/Mac
]

venv_found = False
for venv_path in venv_paths:
    if venv_path.exists():
        venv_found = True
        print(f"   ✓ 找到虚拟环境: {venv_path}")

        try:
            content = venv_path.read_text(encoding='utf-8')
            if 'OPENAI_API_KEY' in content:
                print("   📝 激活脚本中包含 OPENAI_API_KEY 设置")
            else:
                print("   ℹ 激活脚本中未设置 OPENAI_API_KEY")
        except:
            pass

if not venv_found:
    print("   ℹ 未找到虚拟环境")

# 4. 总结
print("\n" + "=" * 80)
print("📊 总结:")
print("=" * 80)

if env_key:
    print("✅ API 密钥已配置，可以正常调用 OpenAI API")
    print("\n💡 你的 API 密钥可能来自:")
    print("   • 系统环境变量（永久配置）")
    print("   • PowerShell 会话变量（临时配置）")
    print("   • .env 文件（推荐方式）")
    print("   • 虚拟环境激活脚本")
else:
    print("⚠ 未检测到 API 密钥配置")
    print("\n建议配置方法:")
    print("   1. 创建 .env 文件: echo OPENAI_API_KEY=sk-your-key-here > .env")
    print("   2. 或设置环境变量: $env:OPENAI_API_KEY='sk-your-key-here'")

print("\n" + "=" * 80)
