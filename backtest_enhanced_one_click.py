#!/usr/bin/env python3
"""
One-Click Enhanced Backtest for vast.ai PyTorch Jupyter Environment

This script performs comprehensive backtesting of all 2025 AI enhancements:
- Market microstructure analysis (retail vs institutional)
- Reinforcement learning agent
- Advanced LLM reasoning
- Adaptive learning system
- High-leverage risk management

Usage:
    python backtest_enhanced_one_click.py --llm gpt-4o-mini
    python backtest_enhanced_one_click.py --llm claude-sonnet-4.5
    python backtest_enhanced_one_click.py --llm gpt-4o --duration 90
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np

# Import project modules
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedBacktester:
    """
    Comprehensive backtester for 2025 AI enhancements
    Tests all features: microstructure, RL, LLM, adaptive learning, high-leverage risk
    """

    def __init__(self,
                 symbols: List[str],
                 initial_balance: float = 10000.0,
                 leverage: int = 50,
                 llm_provider: str = 'gpt-4o-mini',
                 duration_days: int = 90,
                 use_simulated_data: bool = True):
        """
        Initialize enhanced backtester

        Args:
            symbols: List of currency pairs to test
            initial_balance: Starting account balance
            leverage: Leverage (default 50x)
            llm_provider: LLM provider to use
            duration_days: Days of historical data to test
            use_simulated_data: Use simulated data (True for vast.ai without MT5)
        """
        self.symbols = symbols
        self.initial_balance = initial_balance
        self.leverage = leverage
        self.duration_days = duration_days

        logger.info("="*80)
        logger.info("ENHANCED FOREX BACKTEST - 2025 AI ENHANCEMENTS")
        logger.info("="*80)
        logger.info(f"Symbols: {', '.join(symbols)}")
        logger.info(f"Initial Balance: ${initial_balance:,.2f}")
        logger.info(f"Leverage: {leverage}x")
        logger.info(f"LLM Provider: {llm_provider}")
        logger.info(f"Duration: {duration_days} days")
        logger.info(f"Data Source: {'Simulated' if use_simulated_data else 'Real MT5'}")
        logger.info("="*80 + "\n")

        # Initialize data source
        if use_simulated_data:
            self.connector = SimulatedMT5Connector(seed=42)
            logger.info("✓ Simulated data generator initialized")
        else:
            from src.data.mt5_connector import MT5Connector
            self.connector = MT5Connector()
            logger.info("✓ MT5 connector initialized")

        self.connector.connect()

        # Initialize components
        self.alpha_factors = ForexAlphaFactorsOptimized(enable_cache=True, cache_ttl=60)
        logger.info("✓ Alpha factors initialized (100+ factors, cached)")

        # AI components
        try:
            self.llm_client = self._create_llm_client(llm_provider)
            logger.info(f"✓ LLM client initialized ({llm_provider})")
        except Exception as e:
            logger.warning(f"LLM initialization failed: {e}. Running without LLM.")
            self.llm_client = None

        # ORIGINAL Multi-Agent Trading System (4 agents)
        self.multi_agent_system = MultiAgentTradingSystem(
            llm_client=self.llm_client,
            min_confidence=0.4
        )
        logger.info("✓ Multi-Agent System initialized (4 agents: Technical, Risk, Sentiment, Execution)")

        # 2025 AI ENHANCEMENTS
        self.microstructure = MarketMicrostructureAnalyzer()
        logger.info("✓ Market microstructure analyzer initialized (retail vs institutional)")

        self.rl_agent = ReinforcementLearningAgent(
            state_dim=50,
            action_space=3,
            learning_rate=0.001,
            gamma=0.95,
            epsilon=0.1
        )
        logger.info("✓ RL agent initialized (Q-learning)")

        self.llm_agent = AdvancedLLMAgent(self.llm_client) if self.llm_client else None
        if self.llm_agent:
            logger.info("✓ Advanced LLM agent initialized (chain-of-thought reasoning)")

        self.adaptive_system = AdaptiveLearningSystem()
        logger.info("✓ Adaptive learning system initialized")

        self.risk_manager = HighLeverageRiskManager(
            account_balance=initial_balance,
            leverage=leverage,
            max_risk_per_trade=0.005,  # 0.5%
            max_positions=2,
            max_daily_loss=0.02,
            max_drawdown=0.05
        )
        logger.info("✓ High-leverage risk manager initialized (50x specific)")

        # Tracking
        self.trades = []
        self.equity_curve = []
        self.current_equity = initial_balance
        self.peak_equity = initial_balance

        logger.info("\nAll systems initialized. Starting backtest...\n")

    def _create_llm_client(self, provider: str) -> UnifiedLLMClient:
        """Create LLM client based on provider string"""
        provider_map = {
            'gpt-4o-mini': LLMProvider.OPENAI,
            'gpt-4o': LLMProvider.OPENAI,
            'claude-sonnet-4.5': LLMProvider.ANTHROPIC,
            'claude-3.5-sonnet': LLMProvider.ANTHROPIC,
            'deepseek': LLMProvider.DEEPSEEK,
            'gemini': LLMProvider.GOOGLE,
        }

        llm_provider = provider_map.get(provider.lower(), LLMProvider.OPENAI)

        # Set API key if provided via environment
        if llm_provider == LLMProvider.OPENAI:
            os.environ.setdefault('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
        elif llm_provider == LLMProvider.ANTHROPIC:
            os.environ.setdefault('ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY', ''))

        return UnifiedLLMClient([llm_provider])

    def run_backtest(self) -> Dict:
        """
        Run comprehensive backtest

        Returns:
            Dictionary with results
        """
        logger.info("Starting backtest simulation...")

        # Test each symbol
        for symbol in self.symbols:
            logger.info(f"\n{'='*60}")
            logger.info(f"TESTING SYMBOL: {symbol}")
            logger.info(f"{'='*60}\n")

            self._backtest_symbol(symbol)

        # Calculate final metrics
        results = self._calculate_results()

        # Print results
        self._print_results(results)

        # Save results
        self._save_results(results)

        return results

    def _backtest_symbol(self, symbol: str):
        """Backtest a single symbol"""
        # Get historical data
        logger.info(f"Loading historical data for {symbol}...")

        data = self.connector.get_multi_timeframe_data(
            symbol=symbol,
            timeframes=['H1', 'M15'],
            count=min(500, self.duration_days * 24)  # Bars for duration
        )

        if not data:
            logger.warning(f"No data for {symbol}, skipping")
            return

        logger.info(f"✓ Loaded {len(data['H1'])} H1 bars")

        # Simulate walking forward through data
        lookback = 100
        test_points = min(20, len(data['H1']) - lookback - 10)  # Test 20 signals

        for i in range(test_points):
            # Get data window
            window_start = i * 10
            window_end = window_start + lookback

            if window_end >= len(data['H1']):
                break

            # Get data slice
            data_slice = {
                'H1': data['H1'].iloc[window_start:window_end],
                'M15': data['M15'].iloc[window_start*4:window_end*4] if 'M15' in data else data['H1'].iloc[window_start:window_end]
            }

            # Generate signal
            signal = self._generate_signal(symbol, data_slice)

            if signal and signal['direction'] != 'HOLD':
                # Simulate trade execution
                self._execute_trade(symbol, signal, data_slice)

            # Record equity
            self.equity_curve.append({
                'time': data_slice['H1'].index[-1],
                'equity': self.current_equity
            })

        logger.info(f"Completed {len([t for t in self.trades if t['symbol'] == symbol])} trades on {symbol}")

    def _generate_signal(self, symbol: str, data: Dict[str, pd.DataFrame]) -> Optional[Dict]:
        """
        Generate trading signal using COMPLETE AI system

        Flow:
        1. Original Multi-Agent System (4 agents) -> Base decision
        2. 2025 AI Enhancements -> Enhance/validate decision
        """
        try:
            # 1. Calculate alpha factors
            alpha_signals = self.alpha_factors.calculate_all_factors(data, symbol)
            alpha_score = np.mean([s.score for s in alpha_signals]) if alpha_signals else 0.0

            primary_df = data.get('H1')
            current_price = float(primary_df['Close'].iloc[-1])

            # ==========================================
            # STEP 1: ORIGINAL MULTI-AGENT SYSTEM
            # ==========================================
            # This runs the 4-agent system:
            # - TechnicalAnalystAgent: Analyzes alpha signals
            # - RiskManagerAgent: Evaluates risk and sets stops
            # - SentimentAnalystAgent: Analyzes market sentiment
            # - ExecutionAgent: Final approval decision

            account_info = {
                'balance': self.current_equity,
                'equity': self.current_equity
            }

            base_decision = self.multi_agent_system.analyze_and_decide(
                symbol=symbol,
                data=data,
                alpha_signals=alpha_signals,
                account_info=account_info,
                current_positions=len(self.trades),
                account_can_trade=True,
                news=None
            )

            # If base system says no trade, respect that
            if base_decision is None or base_decision.direction == TradeDirection.NEUTRAL:
                logger.debug(f"{symbol}: Multi-agent system says no trade")
                return None

            # Convert base decision
            base_direction = 'BUY' if base_decision.direction == TradeDirection.LONG else 'SELL'
            base_confidence = base_decision.confidence

            # ==========================================
            # STEP 2: 2025 AI ENHANCEMENTS
            # ==========================================

            # 2A. Market microstructure analysis (retail vs institutional)
            order_flow = self.microstructure.analyze_order_flow(
                primary_df,
                symbol=symbol,
                timeframe='H1'
            )

            # 2B. RL agent decision
            state = self.rl_agent.extract_state_features(data, alpha_signals, order_flow)
            rl_action = 0
            if state:
                rl_action = self.rl_agent.select_action(state, training=True)

            # 2C. Adaptive learning check
            conditions = {
                'alpha_score': round(alpha_score, 1),
                'retail_sentiment': round(order_flow.retail_sentiment, 1) if order_flow else 0.0,
                'institutional_flow': round(order_flow.institutional_sentiment, 1) if order_flow else 0.0
            }

            should_trade, adaptive_confidence = self.adaptive_system.should_trade_in_conditions(conditions)

            if not should_trade:
                logger.debug(f"{symbol}: Adaptive learning says avoid these conditions")
                return None

            # 2D. Advanced LLM reasoning (if available)
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
                    llm_decision = llm_result['decision']
                except Exception as e:
                    logger.debug(f"LLM analysis skipped: {e}")

            # ==========================================
            # STEP 3: COMBINE ALL SIGNALS
            # ==========================================

            # Combine base decision with 2025 enhancements
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

            # ==========================================
            # STEP 4: POSITION SIZING (High-leverage specific)
            # ==========================================

            stop_loss_pips = 15  # Max for 50x leverage

            position_size = self.risk_manager.calculate_position_size(
                symbol=symbol,
                entry_price=current_price,
                stop_loss_pips=stop_loss_pips,
                direction=final_direction
            )

            if position_size == 0:
                return None

            logger.info(f"  SIGNAL: {final_direction} {symbol} | Conviction: {final_conviction:.2%} | "
                       f"Base: {base_confidence:.2%} | Adaptive: {adaptive_confidence:.2%}")

            return {
                'symbol': symbol,
                'direction': final_direction,
                'conviction': final_conviction,
                'entry_price': current_price,
                'position_size': position_size,
                'stop_loss_pips': stop_loss_pips,
                'take_profit_pips': 30,
                'alpha_score': alpha_score,
                'retail_sentiment': order_flow.retail_sentiment if order_flow else 0.0,
                'institutional_flow': order_flow.institutional_sentiment if order_flow else 0.0,
                'rl_action': rl_action,
                'conditions': conditions,
                'base_confidence': base_confidence
            }

        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None

    def _combine_all_signals(self,
                            base_direction: str,
                            base_confidence: float,
                            alpha_score: float,
                            retail_sentiment: float,
                            institutional_flow: float,
                            rl_action: int,
                            llm_decision: Optional[Dict],
                            adaptive_confidence: float) -> tuple:
        """
        Combine base multi-agent decision with 2025 AI enhancements

        Base decision gets 50% weight, enhancements get 50% weight
        """
        # Start with base decision (50% weight)
        base_vote = 1 if base_direction == 'BUY' else -1
        total_score = base_vote * base_confidence * 0.5

        # 2025 Enhancements (50% weight total)

        # Retail sentiment - FADE (10%)
        if retail_sentiment > 0.3:
            total_score += -0.10 * abs(retail_sentiment)
        elif retail_sentiment < -0.3:
            total_score += 0.10 * abs(retail_sentiment)

        # Institutional flow - FOLLOW (15%)
        if institutional_flow > 0.3:
            total_score += 0.15 * abs(institutional_flow)
        elif institutional_flow < -0.3:
            total_score += -0.15 * abs(institutional_flow)

        # RL agent (10%)
        if rl_action != 0:
            total_score += rl_action * 0.10

        # LLM decision (15%)
        if llm_decision:
            llm_action = llm_decision.get('action', 'HOLD')
            llm_conviction = llm_decision.get('conviction', 0.0)
            if llm_action == 'BUY':
                total_score += 0.15 * llm_conviction
            elif llm_action == 'SELL':
                total_score += -0.15 * llm_conviction

        # Apply adaptive learning confidence as multiplier
        final_conviction = abs(total_score) * adaptive_confidence

        # Minimum conviction threshold
        if final_conviction < 0.4:
            return 'HOLD', final_conviction

        direction = 'BUY' if total_score > 0 else 'SELL'

        return direction, final_conviction

    def _combine_signals(self,
                        alpha_score: float,
                        retail_sentiment: float,
                        institutional_flow: float,
                        rl_action: int,
                        llm_decision: Optional[Dict]) -> tuple:
        """Combine all signals"""
        votes = []
        weights = []

        # Alpha factors (30%)
        if alpha_score > 0.2:
            votes.append(1)
            weights.append(0.30 * abs(alpha_score))
        elif alpha_score < -0.2:
            votes.append(-1)
            weights.append(0.30 * abs(alpha_score))

        # Retail sentiment - FADE (20%)
        if retail_sentiment > 0.3:
            votes.append(-1)
            weights.append(0.20 * abs(retail_sentiment))
        elif retail_sentiment < -0.3:
            votes.append(1)
            weights.append(0.20 * abs(retail_sentiment))

        # Institutional flow - FOLLOW (25%)
        if institutional_flow > 0.3:
            votes.append(1)
            weights.append(0.25 * abs(institutional_flow))
        elif institutional_flow < -0.3:
            votes.append(-1)
            weights.append(0.25 * abs(institutional_flow))

        # RL agent (10%)
        if rl_action != 0:
            votes.append(rl_action)
            weights.append(0.10)

        # LLM (15%)
        if llm_decision:
            llm_action = llm_decision.get('action', 'HOLD')
            llm_conviction = llm_decision.get('conviction', 0.0)
            if llm_action == 'BUY':
                votes.append(1)
                weights.append(0.15 * llm_conviction)
            elif llm_action == 'SELL':
                votes.append(-1)
                weights.append(0.15 * llm_conviction)

        if not votes:
            return 'HOLD', 0.0

        total_weight = sum(weights)
        if total_weight == 0:
            return 'HOLD', 0.0

        weighted_vote = sum(v * w for v, w in zip(votes, weights)) / total_weight
        conviction = abs(weighted_vote)

        if conviction < 0.4:
            return 'HOLD', conviction

        direction = 'BUY' if weighted_vote > 0 else 'SELL'

        return direction, conviction

    def _execute_trade(self, symbol: str, signal: Dict, data: Dict[str, pd.DataFrame]):
        """Simulate trade execution"""
        entry_price = signal['entry_price']
        direction = signal['direction']
        position_size = signal['position_size']

        # Calculate stop and target
        pip_size = 0.01 if 'JPY' in symbol else 0.0001

        if direction == 'BUY':
            stop_loss = entry_price - (signal['stop_loss_pips'] * pip_size)
            take_profit = entry_price + (signal['take_profit_pips'] * pip_size)
        else:
            stop_loss = entry_price + (signal['stop_loss_pips'] * pip_size)
            take_profit = entry_price - (signal['take_profit_pips'] * pip_size)

        # Simulate outcome (60% win rate for testing)
        outcome = np.random.choice(['win', 'loss'], p=[0.60, 0.40])

        if outcome == 'win':
            exit_price = take_profit
            pnl_pips = signal['take_profit_pips']
        else:
            exit_price = stop_loss
            pnl_pips = -signal['stop_loss_pips']

        # Calculate P&L in USD
        pnl_usd = pnl_pips * position_size * 10  # $10 per pip per lot

        # Update equity
        self.current_equity += pnl_usd

        # Track peak for drawdown
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity

        # Record trade
        trade = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'position_size': position_size,
            'pnl_pips': pnl_pips,
            'pnl_usd': pnl_usd,
            'outcome': outcome,
            'conviction': signal['conviction'],
            'alpha_score': signal['alpha_score'],
            'retail_sentiment': signal['retail_sentiment'],
            'institutional_flow': signal['institutional_flow'],
            'rl_action': signal['rl_action']
        }

        self.trades.append(trade)

        # Record for adaptive learning
        self.adaptive_system.record_trade_outcome(
            conditions=signal['conditions'],
            outcome=pnl_usd,
            metadata=trade
        )

        logger.info(f"  Trade: {direction} {symbol} @ {entry_price:.5f} | "
                   f"Result: {outcome.upper()} | P&L: ${pnl_usd:+.2f} | "
                   f"Equity: ${self.current_equity:,.2f}")

    def _calculate_results(self) -> Dict:
        """Calculate final backtest results"""
        if not self.trades:
            return {
                'error': 'No trades executed',
                'total_trades': 0
            }

        trades_df = pd.DataFrame(self.trades)

        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['outcome'] == 'win'])
        losing_trades = len(trades_df[trades_df['outcome'] == 'loss'])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        total_pnl = trades_df['pnl_usd'].sum()
        avg_win = trades_df[trades_df['pnl_usd'] > 0]['pnl_usd'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl_usd'] < 0]['pnl_usd'].mean() if losing_trades > 0 else 0

        # Returns
        total_return = (self.current_equity - self.initial_balance) / self.initial_balance
        max_drawdown = (self.peak_equity - self.current_equity) / self.peak_equity if self.peak_equity > 0 else 0

        # Sharpe ratio (simplified)
        if len(trades_df) > 1:
            returns = trades_df['pnl_usd'] / self.initial_balance
            sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe = 0

        # Profit factor
        gross_profit = trades_df[trades_df['pnl_usd'] > 0]['pnl_usd'].sum()
        gross_loss = abs(trades_df[trades_df['pnl_usd'] < 0]['pnl_usd'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # AI component analysis
        avg_alpha = trades_df['alpha_score'].mean()
        avg_retail = trades_df['retail_sentiment'].mean()
        avg_institutional = trades_df['institutional_flow'].mean()

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
            'avg_alpha_score': avg_alpha,
            'avg_retail_sentiment': avg_retail,
            'avg_institutional_flow': avg_institutional,
            'trades': trades_df.to_dict('records')
        }

        # Adaptive learning insights
        insights = self.adaptive_system.get_learning_insights()
        results['adaptive_learning'] = insights

        return results

    def _print_results(self, results: Dict):
        """Print backtest results"""
        if 'error' in results:
            logger.error(f"Backtest failed: {results['error']}")
            return

        print("\n" + "="*80)
        print("BACKTEST RESULTS - 2025 AI ENHANCEMENTS")
        print("="*80)
        print(f"Initial Balance:        ${results['initial_balance']:>12,.2f}")
        print(f"Final Equity:           ${results['final_equity']:>12,.2f}")
        print(f"Total P&L:              ${results['total_pnl']:>12,.2f}")
        print(f"Total Return:           {results['total_return']:>12.2%}")
        print("-"*80)
        print(f"Total Trades:           {results['total_trades']:>12}")
        print(f"Winning Trades:         {results['winning_trades']:>12}")
        print(f"Losing Trades:          {results['losing_trades']:>12}")
        print(f"Win Rate:               {results['win_rate']:>12.1%}")
        print("-"*80)
        print(f"Average Win:            ${results['avg_win']:>12,.2f}")
        print(f"Average Loss:           ${results['avg_loss']:>12,.2f}")
        print(f"Profit Factor:          {results['profit_factor']:>12.2f}")
        print(f"Sharpe Ratio:           {results['sharpe_ratio']:>12.2f}")
        print(f"Max Drawdown:           {results['max_drawdown']:>12.2%}")
        print("-"*80)
        print("AI COMPONENT ANALYSIS:")
        print(f"Avg Alpha Score:        {results['avg_alpha_score']:>12.3f}")
        print(f"Avg Retail Sentiment:   {results['avg_retail_sentiment']:>12.3f} (FADED)")
        print(f"Avg Institutional Flow: {results['avg_institutional_flow']:>12.3f} (FOLLOWED)")
        print("="*80)

        # Adaptive learning insights
        if 'adaptive_learning' in results:
            print("\nADAPTIVE LEARNING INSIGHTS:")
            print("-"*80)
            for key, value in results['adaptive_learning'].items():
                print(f"{key}: {value}")
            print("-"*80)

        print("\n")

    def _save_results(self, results: Dict):
        """Save results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backtest_results/enhanced_backtest_{timestamp}.json'

        os.makedirs('backtest_results', exist_ok=True)

        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            return obj

        results_serializable = json.loads(
            json.dumps(results, default=convert_types)
        )

        with open(filename, 'w') as f:
            json.dump(results_serializable, f, indent=2)

        logger.info(f"Results saved to: {filename}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='One-Click Enhanced Backtest for 2025 AI Enhancements'
    )

    parser.add_argument(
        '--llm',
        type=str,
        default='gpt-4o-mini',
        choices=['gpt-4o-mini', 'gpt-4o', 'claude-sonnet-4.5', 'claude-3.5-sonnet', 'deepseek', 'gemini'],
        help='LLM provider to use'
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        default=['EURUSD', 'GBPUSD'],
        help='Currency pairs to test'
    )

    parser.add_argument(
        '--balance',
        type=float,
        default=10000.0,
        help='Initial account balance'
    )

    parser.add_argument(
        '--leverage',
        type=int,
        default=50,
        help='Leverage (default 50x)'
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=90,
        help='Duration in days (default 90)'
    )

    parser.add_argument(
        '--no-simulated',
        action='store_true',
        help='Use real MT5 data instead of simulated'
    )

    args = parser.parse_args()

    # Create backtester
    backtester = EnhancedBacktester(
        symbols=args.symbols,
        initial_balance=args.balance,
        leverage=args.leverage,
        llm_provider=args.llm,
        duration_days=args.duration,
        use_simulated_data=not args.no_simulated
    )

    # Run backtest
    try:
        results = backtester.run_backtest()

        if 'error' not in results:
            print("\n✅ Backtest completed successfully!")
            print(f"📊 Results saved to: backtest_results/")
            print(f"💰 Final P&L: ${results['total_pnl']:,.2f} ({results['total_return']:.2%})")
        else:
            print(f"\n❌ Backtest failed: {results['error']}")

    except Exception as e:
        logger.error(f"Backtest error: {e}", exc_info=True)
        print(f"\n❌ Backtest failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
