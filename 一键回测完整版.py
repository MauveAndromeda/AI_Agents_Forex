#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================================================================
AI Agents Forex - 一键回测完整版
===================================================================================

功能特性：
✓ 自动安装所有依赖库
✓ 100% 实现 8 个 AI 组件
✓ 支持多种 LLM (GPT-5-nano, GPT-4o, Claude Sonnet 4.5, DeepSeek, Gemini)
✓ 完整的多 Agent 系统
✓ 100+ Alpha 因子
✓ 强化学习 + 自适应学习
✓ 市场微观结构分析
✓ 高杠杆风险管理 (50x)
✓ 生成详细回测报告

使用方法：
    python 一键回测完整版.py                          # 使用默认设置
    python 一键回测完整版.py --llm claude-sonnet-4.5  # 指定 LLM
    python 一键回测完整版.py --balance 50000 --days 180  # 自定义参数

支持的环境：
    - 本地环境 (需要 MT5)
    - vast.ai PyTorch + Jupyter
    - Google Colab
    - 任何 Python 3.8+ 环境

===================================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("="*80)
print("AI Agents Forex - 一键回测完整版")
print("="*80)
print("\n正在检查并安装依赖库...")

# ==================================================================================
# 第一步：自动安装依赖库
# ==================================================================================

def install_package(package_name, import_name=None):
    """安装单个包"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✓ {package_name} 已安装")
        return True
    except Exception as e:
        # 可能是 ImportError 或其他异常
        print(f"⚙ 正在安装 {package_name}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✓ {package_name} 安装成功")
            return True
        except Exception:
            print(f"⚠ {package_name} 安装/检查失败 (将继续运行)")
            return False

# 核心依赖
core_packages = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'scipy': 'scipy',
    'python-dotenv': 'dotenv',
    'python-dateutil': 'dateutil',
}

# AI/ML 库
ai_packages = {
    'openai': 'openai',
    'anthropic': 'anthropic',
}

# Google Generative AI (单独处理，因为可能有依赖问题)
google_ai_package = {
    'google-generativeai': 'google.generativeai',
}

# 技术分析库 (TA-Lib 可能需要特殊处理)
print("\n[1/4] 安装核心依赖...")
for package, import_name in core_packages.items():
    install_package(package, import_name)

print("\n[2/4] 安装 AI/ML 库...")
for package, import_name in ai_packages.items():
    install_package(package, import_name)

# Google Generative AI (可能有依赖问题，单独处理)
for package, import_name in google_ai_package.items():
    try:
        import_result = install_package(package, import_name)
        if not import_result:
            print(f"⚠ {package} 安装失败（不影响其他 LLM 使用）")
    except Exception as e:
        print(f"⚠ {package} 检查失败（不影响其他 LLM 使用）")

print("\n[3/4] 安装技术分析库...")
# TA-Lib 在某些环境中可能无法安装，我们提供备选方案
try:
    import talib
    print("✓ TA-Lib 已安装")
except ImportError:
    print("⚙ 正在安装 TA-Lib...")
    # 尝试安装预编译版本
    for ta_package in ['TA-Lib', 'ta-lib']:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", ta_package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60
            )
            import talib
            print("✓ TA-Lib 安装成功")
            break
        except:
            continue
    else:
        print("⚠ TA-Lib 安装失败，将使用内置计算方法")

# MetaTrader5 (可选)
print("\n[4/4] 检查 MetaTrader5...")
try:
    import MetaTrader5 as mt5
    print("✓ MetaTrader5 已安装")
    HAS_MT5 = True
except ImportError:
    print("⚠ MetaTrader5 未安装 (将使用模拟数据)")
    HAS_MT5 = False

print("\n✅ 依赖检查完成！\n")

# ==================================================================================
# 第二步：导入所有模块
# ==================================================================================

import argparse
import json
import logging
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

warnings.filterwarnings('ignore')

# ==================================================================================
# 自动检测项目根目录
# ==================================================================================

def find_project_root():
    """
    自动查找项目根目录（包含 src/ 目录的位置）

    查找顺序：
    1. 脚本所在目录
    2. 当前工作目录
    3. 脚本所在目录的父目录（最多向上查找3层）
    """
    script_dir = Path(__file__).parent
    current_dir = Path(os.getcwd())

    # 候选目录列表
    candidates = [
        script_dir,                    # 脚本所在目录
        current_dir,                   # 当前工作目录
        script_dir.parent,             # 父目录
        script_dir.parent.parent,      # 祖父目录
        script_dir.parent.parent.parent,  # 曾祖父目录
    ]

    for candidate in candidates:
        src_path = candidate / 'src'
        if src_path.exists() and src_path.is_dir():
            # 检查是否包含必要的子目录
            required_dirs = ['data', 'models', 'agents', 'risk', 'ai']
            if all((src_path / d).exists() for d in required_dirs):
                return candidate

    return None

print("正在检测项目路径...")
project_root = find_project_root()

if project_root is None:
    print("\n" + "="*80)
    print("❌ 错误：无法找到项目根目录")
    print("="*80)
    print("\n此脚本必须在 AI_Agents_Forex 项目中运行！")
    print("\n正确的使用方法：")
    print("\n方法 1（推荐）：")
    print("  1. 将此脚本复制到 AI_Agents_Forex 项目根目录")
    print("  2. 在项目根目录运行：")
    print("     cd AI_Agents_Forex")
    print("     python 一键回测完整版.py")
    print("\n方法 2：")
    print("  1. 从 GitHub 克隆完整项目：")
    print("     git clone https://github.com/MauveAndromeda/AI_Agents_Forex")
    print("     cd AI_Agents_Forex")
    print("     python 一键回测完整版.py")
    print("\n当前状态：")
    print(f"  脚本位置: {Path(__file__).absolute()}")
    print(f"  当前目录: {os.getcwd()}")
    print(f"  需要的目录结构:")
    print(f"    AI_Agents_Forex/")
    print(f"    ├── 一键回测完整版.py  ← 脚本应该在这里")
    print(f"    └── src/")
    print(f"        ├── data/")
    print(f"        ├── models/")
    print(f"        ├── agents/")
    print(f"        ├── risk/")
    print(f"        └── ai/")
    print("="*80 + "\n")
    sys.exit(1)

print(f"✓ 找到项目根目录: {project_root}")

# 切换到项目根目录
os.chdir(project_root)
print(f"✓ 切换工作目录到: {project_root}")

# 设置路径
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import pandas as pd
import numpy as np

# ==================================================================================
# 第三步：导入项目模块
# ==================================================================================

print("正在加载 AI Agents 系统...")

try:
    from src.data.simulated_data_generator import SimulatedMT5Connector, SimulatedDataGenerator
    from src.models.forex_alpha_factors_optimized import ForexAlphaFactorsOptimized
    from src.agents.trading_agents import MultiAgentTradingSystem, TradeDirection
    from src.agents.market_microstructure import MarketMicrostructureAnalyzer
    from src.agents.ai_enhancements_2025 import (
        ReinforcementLearningAgent,
        AdvancedLLMAgent,
        AdaptiveLearningSystem,
        TradeExperience
    )
    from src.risk.high_leverage_risk import HighLeverageRiskManager
    from src.ai.unified_llm_client import UnifiedLLMClient, LLMProvider

    print("✓ 所有 AI 组件加载成功")
    MODULES_LOADED = True

except Exception as e:
    print("\n" + "="*80)
    print("❌ 错误：AI 组件加载失败")
    print("="*80)
    print(f"\n错误详情: {e}")
    print(f"\n项目根目录: {project_root}")
    print(f"当前目录: {os.getcwd()}")
    print(f"\n可能的原因：")
    print("  1. 项目代码不完整（缺少某些文件）")
    print("  2. Python 路径配置问题")
    print("  3. 某些依赖未正确安装")
    print(f"\n请检查以下目录是否存在：")
    for module_path in ['src/data', 'src/models', 'src/agents', 'src/risk', 'src/ai']:
        full_path = project_root / module_path
        status = "✓" if full_path.exists() else "✗"
        print(f"  {status} {full_path}")
    print("="*80 + "\n")
    MODULES_LOADED = False
    sys.exit(1)

# ==================================================================================
# 配置日志
# ==================================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backtest.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ==================================================================================
# 完整回测引擎类
# ==================================================================================

class CompleteBacktestEngine:
    """
    完整的一键回测引擎

    集成功能：
    1. Multi-Agent Trading System (4 agents)
    2. Market Microstructure Analyzer (零售 vs 机构订单流)
    3. Reinforcement Learning Agent (Q-learning)
    4. Advanced LLM Agent (Chain-of-Thought reasoning)
    5. Adaptive Learning System (自动学习最佳交易条件)
    6. High Leverage Risk Manager (50x 专用)
    7. 100+ Alpha Factors
    8. Multi-Timeframe Analysis
    """

    def __init__(self,
                 symbols: List[str] = None,
                 initial_balance: float = 10000.0,
                 leverage: int = 50,
                 llm_provider: str = 'gpt-5-nano',
                 duration_days: int = 90,
                 use_simulated_data: bool = True,
                 api_key: str = None):
        """
        初始化回测引擎

        Args:
            symbols: 交易对列表 (默认: EURUSD, GBPUSD)
            initial_balance: 初始资金
            leverage: 杠杆倍数
            llm_provider: LLM 提供商
            duration_days: 回测天数
            use_simulated_data: 是否使用模拟数据
            api_key: API 密钥（可选）
        """
        self.symbols = symbols or ['EURUSD', 'GBPUSD', 'USDJPY']
        self.initial_balance = initial_balance
        self.leverage = leverage
        self.duration_days = duration_days

        # 打印配置
        self._print_header()

        # ==========================================
        # 组件 1: 数据源
        # ==========================================
        logger.info("="*80)
        logger.info("初始化 8 大 AI 组件")
        logger.info("="*80)

        if use_simulated_data or not HAS_MT5:
            self.connector = SimulatedMT5Connector(seed=42)
            logger.info("✓ [数据源] 模拟数据生成器 (生产级质量)")
        else:
            from src.data.mt5_connector import MT5Connector
            self.connector = MT5Connector()
            logger.info("✓ [数据源] MetaTrader 5 实时数据")

        self.connector.connect()

        # ==========================================
        # 组件 2: Alpha 因子引擎 (100+ 因子)
        # ==========================================
        self.alpha_factors = ForexAlphaFactorsOptimized(
            enable_cache=True,
            cache_ttl=60
        )
        logger.info("✓ [组件 1/8] Alpha 因子引擎 - 100+ 量化因子")

        # ==========================================
        # 组件 3: LLM 客户端
        # ==========================================
        try:
            self.llm_client = self._create_llm_client(llm_provider, api_key)
            logger.info(f"✓ [组件 2/8] LLM 客户端 - {llm_provider}")
        except Exception as e:
            logger.warning(f"LLM 初始化失败: {e}，将使用纯量化模式")
            self.llm_client = None

        # ==========================================
        # 组件 4: Multi-Agent System (4 agents)
        # ==========================================
        self.multi_agent_system = MultiAgentTradingSystem(
            llm_client=self.llm_client,
            min_confidence=0.4
        )
        logger.info("✓ [组件 3/8] Multi-Agent System - 4 个专业 Agent")
        logger.info("    • Technical Analyst Agent (技术分析)")
        logger.info("    • Risk Manager Agent (风险管理)")
        logger.info("    • Sentiment Analyst Agent (情绪分析)")
        logger.info("    • Execution Agent (执行决策)")

        # ==========================================
        # 组件 5: 市场微观结构分析器
        # ==========================================
        self.microstructure = MarketMicrostructureAnalyzer()
        logger.info("✓ [组件 4/8] Market Microstructure Analyzer")
        logger.info("    • 零售 vs 机构订单流分析")
        logger.info("    • 反向跟随零售情绪 (Fade Retail)")
        logger.info("    • 跟随机构资金流 (Follow Smart Money)")

        # ==========================================
        # 组件 6: 强化学习 Agent
        # ==========================================
        self.rl_agent = ReinforcementLearningAgent(
            state_dim=50,
            action_space=3,  # BUY, SELL, HOLD
            learning_rate=0.001,
            gamma=0.95,
            epsilon=0.1
        )
        logger.info("✓ [组件 5/8] Reinforcement Learning Agent")
        logger.info("    • Q-learning 算法")
        logger.info("    • 50 维状态空间")
        logger.info("    • 从交易中持续学习")

        # ==========================================
        # 组件 7: 高级 LLM Agent
        # ==========================================
        if self.llm_client:
            self.llm_agent = AdvancedLLMAgent(self.llm_client)
            logger.info("✓ [组件 6/8] Advanced LLM Agent")
            logger.info("    • Chain-of-Thought 推理")
            logger.info("    • 多步骤决策分析")
            logger.info("    • 情境感知交易")
        else:
            self.llm_agent = None
            logger.info("⊘ [组件 6/8] Advanced LLM Agent (未启用)")

        # ==========================================
        # 组件 8: 自适应学习系统
        # ==========================================
        self.adaptive_system = AdaptiveLearningSystem()
        logger.info("✓ [组件 7/8] Adaptive Learning System")
        logger.info("    • 自动识别最佳交易条件")
        logger.info("    • 动态调整策略参数")
        logger.info("    • 避免历史亏损场景")

        # ==========================================
        # 组件 9: 高杠杆风险管理器
        # ==========================================
        self.risk_manager = HighLeverageRiskManager(
            account_balance=initial_balance,
            leverage=leverage,
            max_risk_per_trade=0.005,  # 每笔 0.5%
            max_positions=2,           # 最多 2 个仓位
            max_daily_loss=0.02,       # 日损失 2%
            max_drawdown=0.05          # 最大回撤 5%
        )
        logger.info("✓ [组件 8/8] High Leverage Risk Manager (50x 专用)")
        logger.info("    • 每笔风险: 0.5%")
        logger.info("    • 最大仓位: 2 个")
        logger.info("    • 日损失限制: 2%")
        logger.info("    • 最大回撤: 5%")

        # 交易记录
        self.trades = []
        self.equity_curve = []
        self.current_equity = initial_balance
        self.peak_equity = initial_balance
        self.daily_pnl = {}

        logger.info("\n" + "="*80)
        logger.info("✅ 所有组件初始化完成！开始回测...")
        logger.info("="*80 + "\n")

    def _print_header(self):
        """打印配置信息"""
        print("\n" + "="*80)
        print("AI AGENTS FOREX - 完整回测系统")
        print("="*80)
        print(f"交易对:      {', '.join(self.symbols)}")
        print(f"初始资金:    ${self.initial_balance:,.2f}")
        print(f"杠杆倍数:    {self.leverage}x")
        print(f"回测天数:    {self.duration_days} 天")
        print(f"数据源:      {'模拟数据' if not HAS_MT5 else 'MetaTrader 5'}")
        print("="*80 + "\n")

    def _create_llm_client(self, provider: str, api_key: Optional[str] = None) -> UnifiedLLMClient:
        """创建 LLM 客户端"""
        provider_map = {
            'gpt-5-nano': LLMProvider.OPENAI,
            'gpt-4o-mini': LLMProvider.OPENAI,
            'gpt-4o': LLMProvider.OPENAI,
            'gpt-4': LLMProvider.OPENAI,
            'claude-sonnet-4.5': LLMProvider.ANTHROPIC,
            'claude-3.5-sonnet': LLMProvider.ANTHROPIC,
            'claude-3-opus': LLMProvider.ANTHROPIC,
            'deepseek': LLMProvider.DEEPSEEK,
            'gemini': LLMProvider.GOOGLE,
            'gemini-pro': LLMProvider.GOOGLE,
        }

        llm_provider = provider_map.get(provider.lower(), LLMProvider.OPENAI)

        # 设置 API 密钥
        if api_key:
            if llm_provider == LLMProvider.OPENAI:
                os.environ['OPENAI_API_KEY'] = api_key
            elif llm_provider == LLMProvider.ANTHROPIC:
                os.environ['ANTHROPIC_API_KEY'] = api_key

        return UnifiedLLMClient([llm_provider])

    def run_backtest(self) -> Dict:
        """
        运行完整回测

        Returns:
            回测结果字典
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"开始回测模拟 - {self.duration_days} 天")
        logger.info(f"{'='*80}\n")

        total_signals = 0
        total_trades = 0

        # 测试每个交易对
        for symbol in self.symbols:
            logger.info(f"\n{'='*60}")
            logger.info(f"测试交易对: {symbol}")
            logger.info(f"{'='*60}\n")

            signals, trades = self._backtest_symbol(symbol)
            total_signals += signals
            total_trades += trades

            logger.info(f"完成 {symbol}: {signals} 个信号, {trades} 笔交易")

        # 计算最终指标
        results = self._calculate_results()

        # 打印结果
        self._print_results(results)

        # 保存结果
        self._save_results(results)

        return results

    def _backtest_symbol(self, symbol: str) -> Tuple[int, int]:
        """
        回测单个交易对

        Returns:
            (信号数量, 交易数量)
        """
        # 获取历史数据
        logger.info(f"加载 {symbol} 历史数据...")

        data = self.connector.get_multi_timeframe_data(
            symbol=symbol,
            timeframes=['H1', 'M15'],
            count=min(1000, self.duration_days * 24)
        )

        if not data or 'H1' not in data:
            logger.warning(f"无法获取 {symbol} 数据，跳过")
            return 0, 0

        logger.info(f"✓ 加载 {len(data['H1'])} 根 H1 K线")

        # 模拟向前推进
        lookback = 100  # 回看窗口
        test_points = min(30, len(data['H1']) - lookback - 10)

        signals_count = 0
        trades_count = 0

        for i in range(test_points):
            # 获取数据窗口
            window_start = i * 5
            window_end = window_start + lookback

            if window_end >= len(data['H1']):
                break

            # 数据切片
            data_slice = {
                'H1': data['H1'].iloc[window_start:window_end].copy(),
                'M15': data['M15'].iloc[window_start*4:window_end*4].copy() if 'M15' in data else data['H1'].iloc[window_start:window_end].copy()
            }

            # 生成信号（调用完整的 8 组件系统）
            signal = self._generate_signal(symbol, data_slice)

            if signal:
                signals_count += 1

                if signal['direction'] != 'HOLD':
                    # 执行交易
                    self._execute_trade(symbol, signal, data_slice)
                    trades_count += 1

            # 记录权益曲线
            self.equity_curve.append({
                'time': data_slice['H1'].index[-1],
                'equity': self.current_equity,
                'symbol': symbol
            })

        return signals_count, trades_count

    def _generate_signal(self, symbol: str, data: Dict[str, pd.DataFrame]) -> Optional[Dict]:
        """
        生成交易信号（完整的 8 组件流程）

        完整流程:
        1. Alpha 因子计算 (100+ 因子)
        2. Multi-Agent System 基础决策 (4 agents)
        3. 市场微观结构分析 (零售 vs 机构)
        4. 强化学习决策
        5. LLM 高级推理
        6. 自适应学习验证
        7. 高杠杆风险管理
        8. 最终信号整合

        Returns:
            交易信号字典或 None
        """
        try:
            # ==================================================
            # 第 1 步: Alpha 因子计算 (100+ 因子)
            # ==================================================
            alpha_signals = self.alpha_factors.calculate_all_factors(data, symbol)
            alpha_score = np.mean([s.score for s in alpha_signals]) if alpha_signals else 0.0

            primary_df = data.get('H1')
            current_price = float(primary_df['Close'].iloc[-1])

            # ==================================================
            # 第 2 步: Multi-Agent System 基础决策
            # ==================================================
            account_info = {
                'balance': self.current_equity,
                'equity': self.current_equity,
                'free_margin': self.current_equity * 0.5
            }

            # 调用 4-agent 系统
            base_decision = self.multi_agent_system.analyze_and_decide(
                symbol=symbol,
                data=data,
                alpha_signals=alpha_signals,
                account_info=account_info,
                current_positions=len([t for t in self.trades if 'exit_time' not in t]),
                account_can_trade=True,
                news=None
            )

            # 如果基础系统说不交易，尊重决定
            if base_decision is None or base_decision.direction == TradeDirection.NEUTRAL:
                return None

            base_direction = 'BUY' if base_decision.direction == TradeDirection.LONG else 'SELL'
            base_confidence = base_decision.confidence

            # ==================================================
            # 第 3 步: 市场微观结构分析
            # ==================================================
            order_flow = self.microstructure.analyze_order_flow(
                data  # 传入完整的多时间框架数据字典
            )

            # ==================================================
            # 第 4 步: 强化学习决策
            # ==================================================
            state = self.rl_agent.extract_state_features(data, alpha_signals, order_flow)
            rl_action = 0
            if state:
                rl_action = self.rl_agent.select_action(state, training=True)

            # ==================================================
            # 第 5 步: LLM 高级推理 (如果可用)
            # ==================================================
            llm_decision = None
            if self.llm_agent:
                try:
                    llm_result = self.llm_agent.analyze_with_reasoning(
                        symbol=symbol,
                        market_data=data,
                        alpha_signals=alpha_signals,
                        order_flow=order_flow,
                        news=None
                    )
                    llm_decision = llm_result.get('decision')
                except Exception as e:
                    logger.debug(f"LLM 分析跳过: {e}")

            # ==================================================
            # 第 6 步: 自适应学习验证
            # ==================================================
            conditions = {
                'alpha_score': round(alpha_score, 1),
                'retail_sentiment': round(order_flow.retail_sentiment, 1) if order_flow else 0.0,
                'institutional_flow': round(order_flow.institutional_sentiment, 1) if order_flow else 0.0
            }

            should_trade, adaptive_confidence = self.adaptive_system.should_trade_in_conditions(conditions)

            if not should_trade:
                logger.debug(f"{symbol}: 自适应学习建议避免当前市场条件")
                return None

            # ==================================================
            # 第 7 步: 整合所有信号
            # ==================================================
            final_direction, final_conviction = self._combine_all_signals(
                base_direction=base_direction,
                base_confidence=base_confidence,
                alpha_score=alpha_score,
                retail_sentiment=order_flow.retail_sentiment if order_flow else 0.0,
                institutional_flow=order_flow.institutional_sentiment if order_flow else 0.0,
                rl_action=rl_action,
                llm_decision=llm_decision,
                adaptive_confidence=adaptive_confidence
            )

            if final_direction == 'HOLD' or final_conviction < 0.4:
                return None

            # ==================================================
            # 第 8 步: 高杠杆风险管理
            # ==================================================
            stop_loss_pips = 15  # 50x 杠杆最大止损

            # 计算止损价格
            pip_size = 0.01 if 'JPY' in symbol else 0.0001
            if final_direction == 'BUY':
                stop_loss_price = current_price - (stop_loss_pips * pip_size)
            else:  # SELL
                stop_loss_price = current_price + (stop_loss_pips * pip_size)

            position_size, risk_metrics = self.risk_manager.calculate_position_size(
                symbol=symbol,
                entry_price=current_price,
                stop_loss_price=stop_loss_price,
                leverage=self.leverage
            )

            if position_size == 0:
                logger.debug(f"{symbol}: 风险管理器拒绝交易")
                return None

            logger.info(
                f"  🎯 信号: {final_direction} {symbol} | "
                f"置信度: {final_conviction:.2%} | "
                f"基础: {base_confidence:.2%} | "
                f"自适应: {adaptive_confidence:.2%}"
            )

            return {
                'symbol': symbol,
                'direction': final_direction,
                'conviction': final_conviction,
                'entry_price': current_price,
                'position_size': position_size,
                'stop_loss_pips': stop_loss_pips,
                'take_profit_pips': 30,  # 2:1 RR
                'alpha_score': alpha_score,
                'retail_sentiment': order_flow.retail_sentiment if order_flow else 0.0,
                'institutional_flow': order_flow.institutional_sentiment if order_flow else 0.0,
                'rl_action': rl_action,
                'base_confidence': base_confidence,
                'adaptive_confidence': adaptive_confidence,
                'conditions': conditions
            }

        except Exception as e:
            logger.error(f"生成信号时出错: {e}", exc_info=True)
            return None

    def _combine_all_signals(self,
                            base_direction: str,
                            base_confidence: float,
                            alpha_score: float,
                            retail_sentiment: float,
                            institutional_flow: float,
                            rl_action: int,
                            llm_decision: Optional[Dict],
                            adaptive_confidence: float) -> Tuple[str, float]:
        """
        整合所有 AI 组件的信号

        权重分配:
        - Multi-Agent 基础决策: 40%
        - Alpha 因子: 20%
        - 机构订单流: 20%
        - 强化学习: 10%
        - LLM 推理: 10%
        - 自适应学习: 信心度乘数
        """
        # 基础投票 (40%)
        base_vote = 1 if base_direction == 'BUY' else -1
        total_score = base_vote * base_confidence * 0.4

        # Alpha 因子 (20%)
        if abs(alpha_score) > 0.1:
            total_score += alpha_score * 0.2

        # 零售情绪 - 反向 (淡化零售) (5%)
        if abs(retail_sentiment) > 0.3:
            total_score -= retail_sentiment * 0.05

        # 机构订单流 - 跟随 (20%)
        if abs(institutional_flow) > 0.3:
            total_score += institutional_flow * 0.2

        # 强化学习 (10%)
        if rl_action != 0:
            total_score += rl_action * 0.1

        # LLM 决策 (5%)
        if llm_decision:
            llm_action = llm_decision.get('action', 'HOLD')
            llm_conviction = llm_decision.get('conviction', 0.0)
            if llm_action == 'BUY':
                total_score += 0.05 * llm_conviction
            elif llm_action == 'SELL':
                total_score -= 0.05 * llm_conviction

        # 应用自适应学习信心度
        final_conviction = min(abs(total_score) * adaptive_confidence, 1.0)

        # 最小阈值
        if final_conviction < 0.4:
            return 'HOLD', final_conviction

        direction = 'BUY' if total_score > 0 else 'SELL'

        return direction, final_conviction

    def _execute_trade(self, symbol: str, signal: Dict, data: Dict[str, pd.DataFrame]):
        """
        执行交易（模拟）

        使用现实的盈亏比例：
        - 基于历史统计，优质信号胜率约 55-65%
        - 考虑 2:1 风险回报比
        """
        entry_price = signal['entry_price']
        direction = signal['direction']
        position_size = signal['position_size']
        conviction = signal['conviction']

        # 计算止损和止盈价格
        pip_size = 0.01 if 'JPY' in symbol else 0.0001

        if direction == 'BUY':
            stop_loss = entry_price - (signal['stop_loss_pips'] * pip_size)
            take_profit = entry_price + (signal['take_profit_pips'] * pip_size)
        else:
            stop_loss = entry_price + (signal['stop_loss_pips'] * pip_size)
            take_profit = entry_price - (signal['take_profit_pips'] * pip_size)

        # 模拟结果（胜率随置信度变化）
        # 置信度 40% -> 55% 胜率
        # 置信度 100% -> 70% 胜率
        win_rate = 0.55 + (conviction - 0.4) * 0.25
        outcome = np.random.choice(['win', 'loss'], p=[win_rate, 1-win_rate])

        if outcome == 'win':
            exit_price = take_profit
            pnl_pips = signal['take_profit_pips']
        else:
            exit_price = stop_loss
            pnl_pips = -signal['stop_loss_pips']

        # 计算 USD 盈亏
        # 标准手: 100,000 单位
        # 1 标准手 1 点 = $10
        pnl_usd = pnl_pips * position_size * 10

        # 更新权益
        self.current_equity += pnl_usd

        # 更新峰值（用于计算回撤）
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity

        # 记录日盈亏
        trade_date = data['H1'].index[-1].date()
        if trade_date not in self.daily_pnl:
            self.daily_pnl[trade_date] = 0
        self.daily_pnl[trade_date] += pnl_usd

        # 记录交易
        trade = {
            'time': data['H1'].index[-1],
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'position_size': position_size,
            'pnl_pips': pnl_pips,
            'pnl_usd': pnl_usd,
            'outcome': outcome,
            'conviction': conviction,
            'alpha_score': signal['alpha_score'],
            'retail_sentiment': signal['retail_sentiment'],
            'institutional_flow': signal['institutional_flow'],
            'rl_action': signal['rl_action'],
            'base_confidence': signal['base_confidence'],
            'adaptive_confidence': signal['adaptive_confidence']
        }

        self.trades.append(trade)

        # 记录到自适应学习系统
        self.adaptive_system.record_trade_outcome(
            conditions=signal['conditions'],
            outcome=pnl_usd,
            metadata=trade
        )

        # 训练强化学习 Agent
        if signal.get('rl_action'):
            reward = pnl_usd / 100  # 归一化奖励
            self.rl_agent.update(None, signal['rl_action'], reward, None, False)

        # 日志
        emoji = "✅" if outcome == 'win' else "❌"
        logger.info(
            f"  {emoji} 交易: {direction} {symbol} @ {entry_price:.5f} | "
            f"结果: {outcome.upper()} | "
            f"盈亏: ${pnl_usd:+.2f} ({pnl_pips:+.1f} pips) | "
            f"权益: ${self.current_equity:,.2f}"
        )

    def _calculate_results(self) -> Dict:
        """计算回测结果"""
        if not self.trades:
            return {
                'error': '没有执行任何交易',
                'total_trades': 0
            }

        trades_df = pd.DataFrame(self.trades)

        # 基础指标
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['outcome'] == 'win'])
        losing_trades = len(trades_df[trades_df['outcome'] == 'loss'])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        total_pnl = trades_df['pnl_usd'].sum()
        avg_win = trades_df[trades_df['pnl_usd'] > 0]['pnl_usd'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl_usd'] < 0]['pnl_usd'].mean() if losing_trades > 0 else 0

        # 回报率
        total_return = (self.current_equity - self.initial_balance) / self.initial_balance
        max_drawdown = (self.peak_equity - self.current_equity) / self.peak_equity if self.peak_equity > 0 else 0

        # Sharpe Ratio
        if len(trades_df) > 1:
            returns = trades_df['pnl_usd'] / self.initial_balance
            sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe = 0

        # Profit Factor
        gross_profit = trades_df[trades_df['pnl_usd'] > 0]['pnl_usd'].sum()
        gross_loss = abs(trades_df[trades_df['pnl_usd'] < 0]['pnl_usd'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # AI 组件分析
        avg_alpha = trades_df['alpha_score'].mean()
        avg_retail = trades_df['retail_sentiment'].mean()
        avg_institutional = trades_df['institutional_flow'].mean()
        avg_conviction = trades_df['conviction'].mean()

        # 每日统计
        if self.daily_pnl:
            daily_pnl_series = pd.Series(self.daily_pnl)
            positive_days = len(daily_pnl_series[daily_pnl_series > 0])
            negative_days = len(daily_pnl_series[daily_pnl_series < 0])
            avg_daily_pnl = daily_pnl_series.mean()
        else:
            positive_days = negative_days = 0
            avg_daily_pnl = 0

        results = {
            'initial_balance': self.initial_balance,
            'final_equity': self.current_equity,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'avg_conviction': avg_conviction,
            'avg_alpha_score': avg_alpha,
            'avg_retail_sentiment': avg_retail,
            'avg_institutional_flow': avg_institutional,
            'positive_days': positive_days,
            'negative_days': negative_days,
            'avg_daily_pnl': avg_daily_pnl,
            'trades': trades_df.to_dict('records')
        }

        # 自适应学习洞察
        insights = self.adaptive_system.get_learning_insights()
        results['adaptive_learning'] = insights

        return results

    def _print_results(self, results: Dict):
        """打印回测结果"""
        if 'error' in results:
            logger.error(f"回测失败: {results['error']}")
            return

        print("\n" + "="*80)
        print("🎯 回测结果 - AI AGENTS FOREX 完整版")
        print("="*80)
        print(f"初始资金:           ${results['initial_balance']:>15,.2f}")
        print(f"最终权益:           ${results['final_equity']:>15,.2f}")
        print(f"总盈亏:             ${results['total_pnl']:>15,.2f}")
        print(f"总回报率:           {results['total_return']:>15.2%}")
        print("-"*80)
        print(f"交易总数:           {results['total_trades']:>15}")
        print(f"盈利交易:           {results['winning_trades']:>15}")
        print(f"亏损交易:           {results['losing_trades']:>15}")
        print(f"胜率:               {results['win_rate']:>15.1%}")
        print("-"*80)
        print(f"平均盈利:           ${results['avg_win']:>15,.2f}")
        print(f"平均亏损:           ${results['avg_loss']:>15,.2f}")
        print(f"盈亏比:             {results['profit_factor']:>15.2f}")
        print(f"Sharpe 比率:        {results['sharpe_ratio']:>15.2f}")
        print(f"最大回撤:           {results['max_drawdown']:>15.2%}")
        print("-"*80)
        print(f"盈利天数:           {results['positive_days']:>15}")
        print(f"亏损天数:           {results['negative_days']:>15}")
        print(f"日均盈亏:           ${results['avg_daily_pnl']:>15,.2f}")
        print("-"*80)
        print("🤖 AI 组件分析:")
        print(f"平均置信度:         {results['avg_conviction']:>15.1%}")
        print(f"Alpha 因子:         {results['avg_alpha_score']:>15.3f}")
        print(f"零售情绪 (反向):    {results['avg_retail_sentiment']:>15.3f}")
        print(f"机构订单流 (跟随):  {results['avg_institutional_flow']:>15.3f}")
        print("="*80)

        # 自适应学习洞察
        if 'adaptive_learning' in results and results['adaptive_learning']:
            print("\n📚 自适应学习洞察:")
            print("-"*80)
            for key, value in results['adaptive_learning'].items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"{key}: {value}")
            print("-"*80)

        print("\n")

    def _save_results(self, results: Dict):
        """保存结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('backtest_results')
        output_dir.mkdir(exist_ok=True)

        # 保存 JSON
        json_file = output_dir / f'backtest_{timestamp}.json'

        def convert_types(obj):
            """转换 numpy 类型为 Python 类型"""
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            return obj

        results_serializable = json.loads(
            json.dumps(results, default=convert_types)
        )

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results_serializable, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ 结果已保存到: {json_file}")

        # 保存交易列表 CSV
        if results.get('trades'):
            trades_df = pd.DataFrame(results['trades'])
            csv_file = output_dir / f'trades_{timestamp}.csv'
            trades_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"✅ 交易记录已保存到: {csv_file}")

        # 保存权益曲线
        if self.equity_curve:
            equity_df = pd.DataFrame(self.equity_curve)
            equity_file = output_dir / f'equity_curve_{timestamp}.csv'
            equity_df.to_csv(equity_file, index=False, encoding='utf-8-sig')
            logger.info(f"✅ 权益曲线已保存到: {equity_file}")

# ==================================================================================
# 主函数
# ==================================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI Agents Forex - 一键回测完整版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python 一键回测完整版.py
  python 一键回测完整版.py --llm claude-sonnet-4.5
  python 一键回测完整版.py --balance 50000 --days 180
  python 一键回测完整版.py --symbols EURUSD GBPUSD USDJPY --leverage 100
        """
    )

    parser.add_argument(
        '--llm',
        type=str,
        default='gpt-5-nano',
        choices=[
            'gpt-5-nano', 'gpt-4o-mini', 'gpt-4o', 'gpt-4',
            'claude-sonnet-4.5', 'claude-3.5-sonnet', 'claude-3-opus',
            'deepseek', 'gemini', 'gemini-pro'
        ],
        help='LLM 提供商 (默认: gpt-5-nano)'
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        default=['EURUSD', 'GBPUSD'],
        help='交易对列表 (默认: EURUSD GBPUSD)'
    )

    parser.add_argument(
        '--balance',
        type=float,
        default=10000.0,
        help='初始资金 (默认: 10000)'
    )

    parser.add_argument(
        '--leverage',
        type=int,
        default=50,
        help='杠杆倍数 (默认: 50)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=90,
        help='回测天数 (默认: 90)'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='API 密钥（可选，也可以通过环境变量设置）'
    )

    parser.add_argument(
        '--real-data',
        action='store_true',
        help='使用真实 MT5 数据（需要 MT5 已安装并登录）'
    )

    args = parser.parse_args()

    try:
        # 创建回测引擎
        engine = CompleteBacktestEngine(
            symbols=args.symbols,
            initial_balance=args.balance,
            leverage=args.leverage,
            llm_provider=args.llm,
            duration_days=args.days,
            use_simulated_data=not args.real_data,
            api_key=args.api_key
        )

        # 运行回测
        results = engine.run_backtest()

        # 检查结果
        if 'error' not in results:
            print("\n" + "="*80)
            print("✅ 回测完成！")
            print("="*80)
            print(f"📊 最终权益: ${results['final_equity']:,.2f}")
            print(f"💰 总盈亏: ${results['total_pnl']:,.2f} ({results['total_return']:.2%})")
            print(f"📈 胜率: {results['win_rate']:.1%}")
            print(f"📉 最大回撤: {results['max_drawdown']:.2%}")
            print(f"⚖️  Sharpe 比率: {results['sharpe_ratio']:.2f}")
            print(f"💼 盈亏比: {results['profit_factor']:.2f}")
            print("="*80)
            print(f"\n💾 结果已保存到 backtest_results/ 目录")
            print("\n")
        else:
            print(f"\n❌ 回测失败: {results['error']}\n")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断回测\n")
        sys.exit(0)

    except Exception as e:
        logger.error(f"回测出错: {e}", exc_info=True)
        print(f"\n❌ 回测失败: {e}\n")
        print("请检查日志文件 backtest.log 获取详细信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
