# 🚀 GPT-5-nano 配置指南

## 📋 什么是 GPT-5-nano？

**GPT-5-nano** 是 OpenAI GPT-5 系列中最小、最快、最经济的模型（2025年8月发布）。

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **模型名称** | `gpt-5-nano` |
| **发布日期** | 2025年8月 |
| **上下文窗口** | 400K tokens |
| **输入价格** | $1.25/1M tokens (90% 缓存折扣) |
| **输出价格** | $10/1M tokens |
| **速度** | 超快（最低延迟） |
| **用途** | 开发工具、快速交互、实时应用 |

### 💰 成本对比

| 模型 | 输入成本 | 输出成本 | 相对成本 |
|------|---------|---------|---------|
| **gpt-5-nano** | $1.25/1M | $10/1M | 最便宜 ✅ |
| gpt-4o-mini | $0.15/1M | $0.60/1M | 非常便宜 |
| gpt-4o | $2.50/1M | $10.00/1M | 中等 |
| claude-sonnet-4.5 | $3.00/1M | $15.00/1M | 较贵 |

**注意**：虽然 gpt-5-nano 的标价比 gpt-4o-mini 高，但它提供了：
- 更大的上下文窗口 (400K vs 128K)
- 更新的训练数据 (2025 vs 2023)
- GPT-5 的改进功能
- 90% 缓存折扣

---

## 🔧 配置方法

### 方法 1: 使用默认配置（推荐）✅

**本项目已默认配置为 gpt-5-nano！**

直接运行即可：

```bash
# Windows
cd AI_Agents_Forex
python 一键回测完整版.py

# Linux/Mac
cd AI_Agents_Forex
python 一键回测完整版.py
```

### 方法 2: 显式指定模型

```bash
# 明确指定 gpt-5-nano
python 一键回测完整版.py --llm gpt-5-nano

# 使用其他模型
python 一键回测完整版.py --llm gpt-4o-mini
python 一键回测完整版.py --llm claude-sonnet-4.5
```

### 方法 3: 高速回测版本

```bash
# 默认使用 gpt-5-nano
python 一键回测_高速版.py --mode fast

# 指定其他模型
python 一键回测_高速版.py --mode cache --llm gpt-4o-mini
```

---

## 🔑 API 密钥配置

### 步骤 1: 获取 OpenAI API 密钥

1. 访问 [OpenAI Platform](https://platform.openai.com)
2. 注册/登录账号
3. 进入 [API Keys](https://platform.openai.com/api-keys)
4. 点击 "Create new secret key"
5. 复制密钥（格式：`sk-proj-...` 或 `sk-...`）

### 步骤 2: 配置密钥（3 种方式）

#### 方式 A: .env 文件（推荐）✅

在项目根目录创建 `.env` 文件：

```bash
# Windows (PowerShell)
cd AI_Agents_Forex
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Linux/Mac
cd AI_Agents_Forex
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

`.env` 文件内容：
```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选：其他 LLM API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 方式 B: 系统环境变量

**Windows (PowerShell)**:
```powershell
# 临时设置（当前会话）
$env:OPENAI_API_KEY="sk-your-key-here"

# 永久设置（系统）
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
```

**Windows (CMD)**:
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**Linux/Mac**:
```bash
# 临时设置（当前会话）
export OPENAI_API_KEY="sk-your-key-here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### 方式 C: 命令行参数

```bash
python 一键回测完整版.py --api-key sk-your-key-here
```

---

## ✅ 验证配置

### 检查密钥是否正确设置

**Windows (PowerShell)**:
```powershell
echo $env:OPENAI_API_KEY
# 应显示: sk-proj-... 或 sk-...
```

**Linux/Mac**:
```bash
echo $OPENAI_API_KEY
# 应显示: sk-proj-... 或 sk-...
```

### 测试 API 连接

```bash
# 运行快速测试（1天回测）
python 一键回测完整版.py --days 1 --symbols EURUSD

# 或使用极速模式（不调用 API，测试其他组件）
python 一键回测_高速版.py --mode ultra-fast --days 1
```

**成功标志**：
```
✓ LLM 客户端初始化 (gpt-5-nano)
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:src.agents.trading_agents:Technical Agent: LONG (confidence: 0.42)
```

**失败标志**：
```
❌ OpenAI API key not provided
❌ HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 401 Unauthorized"
```

---

## 🎯 默认模型说明

### 当前项目默认配置

```python
# 一键回测完整版.py (第 1130 行)
parser.add_argument(
    '--llm',
    type=str,
    default='gpt-5-nano',  # ✅ 默认模型
    choices=[
        'gpt-5-nano',           # 推荐 ✅
        'gpt-4o-mini',
        'gpt-4o',
        'gpt-4',
        'claude-sonnet-4.5',
        'claude-3.5-sonnet',
        'claude-3-opus',
        'deepseek',
        'gemini',
        'gemini-pro'
    ],
    help='LLM 提供商 (默认: gpt-5-nano)'
)
```

### 为什么选择 gpt-5-nano 作为默认？

| 原因 | 说明 |
|------|------|
| ✅ **速度最快** | 最低延迟，适合回测 |
| ✅ **成本较低** | 90% 缓存折扣 |
| ✅ **上下文大** | 400K tokens |
| ✅ **最新技术** | 2025年8月发布 |
| ✅ **性能足够** | 对于交易决策已足够准确 |

---

## 🔄 切换到其他模型

### 场景 1: 需要更高质量的分析

```bash
# 使用 GPT-4o（更强推理能力）
python 一键回测完整版.py --llm gpt-4o

# 使用 Claude Sonnet 4.5（更好的多步推理）
python 一键回测完整版.py --llm claude-sonnet-4.5
```

### 场景 2: 成本敏感

```bash
# 使用 gpt-4o-mini（最便宜）
python 一键回测完整版.py --llm gpt-4o-mini

# 或使用 DeepSeek（超低成本）
python 一键回测完整版.py --llm deepseek
```

### 场景 3: 不使用 LLM（纯量化）

```bash
# 极速模式（免费）
python 一键回测_高速版.py --mode ultra-fast
```

---

## 📊 支持的所有模型

| 模型 | 提供商 | 成本等级 | 速度 | 推荐用途 |
|------|--------|---------|------|---------|
| **gpt-5-nano** ✅ | OpenAI | 💰 低 | ⚡⚡⚡ 极快 | **默认推荐** |
| gpt-4o-mini | OpenAI | 💰 最低 | ⚡⚡ 快 | 成本敏感 |
| gpt-4o | OpenAI | 💰💰 中 | ⚡⚡ 快 | 高质量分析 |
| gpt-4 | OpenAI | 💰💰💰 高 | ⚡ 中 | 最高质量 |
| claude-sonnet-4.5 | Anthropic | 💰💰 中高 | ⚡⚡ 快 | 复杂推理 |
| claude-3.5-sonnet | Anthropic | 💰💰 中高 | ⚡⚡ 快 | 平衡性能 |
| claude-3-opus | Anthropic | 💰💰💰 高 | ⚡ 中 | 最强推理 |
| deepseek | DeepSeek | 💰 超低 | ⚡⚡ 快 | 超低成本 |
| gemini | Google | 💰💰 中 | ⚡⚡ 快 | Google 生态 |
| gemini-pro | Google | 💰💰 中 | ⚡⚡ 快 | Google 生态 |

---

## 💡 使用建议

### 开发/测试阶段

```bash
# 使用免费的极速模式
python 一键回测_高速版.py --mode ultra-fast --days 30

# 或使用最便宜的 gpt-4o-mini
python 一键回测完整版.py --llm gpt-4o-mini --days 30
```

### 正式回测阶段

```bash
# 使用默认的 gpt-5-nano（平衡速度和成本）
python 一键回测完整版.py --days 90

# 或建立缓存后使用高速模式（不消耗 API）
python 一键回测_高速版.py --mode cache --workers 10
python 一键回测_高速版.py --mode fast --days 180
```

### 生产部署

```bash
# 使用高质量模型
python 一键回测完整版.py --llm gpt-4o --days 365

# 或使用 Claude（更好的推理）
python 一键回测完整版.py --llm claude-sonnet-4.5 --days 365
```

---

## 🆘 常见问题

### Q1: 提示 "OpenAI API key not provided"？

**A**: 检查以下几点：
1. 是否创建了 `.env` 文件？
2. `.env` 文件中是否有 `OPENAI_API_KEY=...`？
3. 密钥格式是否正确（`sk-` 开头）？
4. 是否在项目根目录运行？

```bash
# 检查密钥
cat .env  # Linux/Mac
type .env  # Windows

# 应该看到：
OPENAI_API_KEY=sk-proj-xxxxx...
```

### Q2: API 调用失败 (401 Unauthorized)？

**A**: 密钥无效或过期
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 检查密钥是否有效
3. 重新生成新密钥
4. 更新 `.env` 文件

### Q3: API 调用失败 (429 Rate Limit)？

**A**: 超过 API 配额
1. 检查账户余额：[OpenAI Billing](https://platform.openai.com/account/billing)
2. 添加付款方式
3. 等待速率限制重置
4. 或使用高速缓存模式：
   ```bash
   python 一键回测_高速版.py --mode fast
   ```

### Q4: gpt-5-nano 不可用？

**A**: 可能是以下原因：
1. **API 密钥权限不足**：某些密钥可能没有 GPT-5 访问权限
2. **区域限制**：某些地区可能还未开放
3. **账户类型**：需要付费账户

**解决方案**：
```bash
# 临时使用其他模型
python 一键回测完整版.py --llm gpt-4o-mini

# 或使用纯量化模式（不调用 API）
python 一键回测_高速版.py --mode ultra-fast
```

### Q5: 如何查看 API 消耗？

**A**:
1. 访问 [OpenAI Usage](https://platform.openai.com/usage)
2. 查看详细的 API 调用统计
3. 检查每个模型的使用量和成本

**节省成本技巧**：
```bash
# 1. 使用缓存模式（只调用一次 API）
python 一键回测_高速版.py --mode cache  # 首次建立缓存
python 一键回测_高速版.py --mode fast   # 后续使用缓存

# 2. 使用更便宜的模型
python 一键回测完整版.py --llm gpt-4o-mini

# 3. 减少回测天数
python 一键回测完整版.py --days 30
```

---

## 🎉 快速开始

### 第一次使用

```bash
# 1. 配置 API 密钥
cd AI_Agents_Forex
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 2. 运行测试（1天，验证配置）
python 一键回测完整版.py --days 1

# 3. 看到成功输出后，运行完整回测
python 一键回测完整版.py --days 90
```

### 已有配置

```bash
# 直接运行（使用默认 gpt-5-nano）
cd AI_Agents_Forex
python 一键回测完整版.py
```

---

## 📚 相关文档

- [OpenAI API 文档](https://platform.openai.com/docs)
- [GPT-5 发布说明](https://openai.com/blog/gpt-5)
- [项目完整使用说明](./一键回测使用说明.md)
- [高速回测说明](./高速回测说明.md)

---

**最后更新**: 2025-01-06
**版本**: 1.0.0
**默认模型**: gpt-5-nano ✅
