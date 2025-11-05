"""
Enhanced Forex Strategy with 2025 AI Enhancements
Production-grade strategy integrating:
- Market microstructure analysis (retail vs institutional flow)
- High-leverage risk management (50x specific)
- Reinforcement learning for timing
- Advanced LLM reasoning
- Adaptive learning from outcomes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import time

from ..data.mt5_connector import MT5Connector
from ..models.forex_alpha_factors_optimized import ForexAlphaFactorsOptimized
from ..agents.market_microstructure import MarketMicrostructureAnalyzer, SentimentAgent
from ..agents.ai_enhancements_2025 import (
    ReinforcementLearningAgent,
    AdvancedLLMAgent,
    AdaptiveLearningSystem,
    TradeExperience
)
from ..risk.high_leverage_risk import HighLeverageRiskManager
from ..execution.mt5_executor import MT5Executor
from ..ai.unified_llm_client import UnifiedLLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedSignal:
    """Enhanced trading signal with all AI components"""
    symbol: str
    direction: str  # 'BUY', 'SELL', 'HOLD'
    conviction: float  # 0.0 to 1.0

    # Alpha factors
    alpha_score: float

    # Market microstructure
    retail_sentiment: float
    institutional_flow: float
    smart_money_direction: int

    # RL agent
    rl_action: int
    rl_confidence: float

    # LLM reasoning
    llm_decision: Dict
    llm_reasoning: str

    # Risk parameters
    position_size: float
    stop_loss_pips: float
    take_profit_pips: float
    liquidation_price: float

    # Metadata
    timestamp: datetime
    timeframe: str


class EnhancedForexStrategy:
    """
    Production-grade Forex strategy with 2025 AI enhancements

    Strategy Logic:
    1. Detect retail vs institutional flow
    2. Fade retail sentiment (contrarian)
    3. Follow institutional flow (smart money)
    4. Use RL agent for optimal timing
    5. LLM for multi-step reasoning and validation
    6. Ultra-conservative risk for 50x leverage
    7. Adaptive learning from outcomes
    """

    def __init__(self,
                 symbols: List[str],
                 timeframes: List[str],
                 account_balance: float,
                 leverage: int = 50,
                 use_llm: bool = True,
                 enable_rl: bool = True,
                 enable_adaptive_learning: bool = True,
                 dry_run: bool = False):
        """
        Initialize enhanced strategy

        Args:
            symbols: List of forex pairs (e.g., ['EURUSD', 'GBPUSD'])
            timeframes: List of timeframes (e.g., ['H1', 'M15'])
            account_balance: Account balance in USD
            leverage: Leverage (default 50x for Forex.com)
            use_llm: Enable LLM reasoning
            enable_rl: Enable RL agent
            enable_adaptive_learning: Enable adaptive learning
            dry_run: Paper trading mode
        """
        self.symbols = symbols
        self.timeframes = timeframes
        self.account_balance = account_balance
        self.leverage = leverage
        self.use_llm = use_llm
        self.enable_rl = enable_rl
        self.enable_adaptive_learning = enable_adaptive_learning
        self.dry_run = dry_run

        # Initialize components
        logger.info("Initializing Enhanced Forex Strategy...")

        # Data and execution
        self.mt5 = MT5Connector()
        self.executor = MT5Executor(dry_run=dry_run)

        # Alpha factors (optimized with caching)
        self.alpha_factors = ForexAlphaFactorsOptimized(
            enable_cache=True,
            cache_ttl=60
        )

        # Market microstructure
        self.microstructure = MarketMicrostructureAnalyzer()

        # Risk management (50x specific)
        self.risk_manager = HighLeverageRiskManager(
            account_balance=account_balance,
            leverage=leverage,
            max_risk_per_trade=0.005,  # 0.5%
            max_positions=2,
            max_daily_loss=0.02,
            max_drawdown=0.05
        )

        # AI components
        if self.use_llm:
            llm_client = UnifiedLLMClient()
            self.sentiment_agent = SentimentAgent(llm_client)
            self.llm_agent = AdvancedLLMAgent(llm_client)
            logger.info("✓ LLM agents initialized")
        else:
            self.sentiment_agent = None
            self.llm_agent = None

        if self.enable_rl:
            self.rl_agent = ReinforcementLearningAgent(
                state_dim=50,
                action_space=3,
                learning_rate=0.001,
                gamma=0.95,
                epsilon=0.1
            )
            logger.info("✓ RL agent initialized")
        else:
            self.rl_agent = None

        if self.enable_adaptive_learning:
            self.adaptive_system = AdaptiveLearningSystem()
            logger.info("✓ Adaptive learning system initialized")
        else:
            self.adaptive_system = None

        # State tracking
        self.active_positions = {}
        self.current_equity = account_balance
        self.daily_pnl = 0.0
        self.peak_equity = account_balance
        self.last_trade_time = {}

        # Performance tracking
        self.trade_history = []
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'sharpe_ratio': 0.0
        }

        logger.info(f"Strategy initialized: {len(symbols)} symbols, {len(timeframes)} timeframes")
        logger.info(f"Leverage: {leverage}x | Risk per trade: 0.5% | Max positions: 2")
        logger.info(f"Mode: {'DRY RUN (Paper Trading)' if dry_run else 'LIVE TRADING'}")

    def generate_signal(self, symbol: str) -> Optional[EnhancedSignal]:
        """
        Generate enhanced trading signal for a symbol

        Returns:
            EnhancedSignal or None if no valid signal
        """
        try:
            # 1. Get market data
            data = self._get_market_data(symbol)
            if not data:
                return None

            # 2. Calculate alpha factors
            alpha_signals = self.alpha_factors.calculate_all_factors(data, symbol)
            alpha_score = np.mean([s.score for s in alpha_signals]) if alpha_signals else 0.0

            # 3. Market microstructure analysis
            primary_df = data.get('H1') or data.get('M15')
            if primary_df is None:
                return None

            order_flow = self.microstructure.analyze_order_flow(
                primary_df,
                symbol=symbol,
                timeframe='H1'
            )

            # 4. RL agent decision
            rl_action = 0
            rl_confidence = 0.5
            if self.enable_rl and order_flow:
                state = self.rl_agent.extract_state_features(
                    data,
                    alpha_signals,
                    order_flow
                )
                if state:
                    rl_action = self.rl_agent.select_action(state, training=True)
                    # Confidence based on Q-values
                    state_key = self.rl_agent.get_state_key(state)
                    if state_key in self.rl_agent.q_table:
                        q_values = self.rl_agent.q_table[state_key]
                        rl_confidence = float(np.max(q_values)) / (np.sum(np.abs(q_values)) + 1e-6)

            # 5. Adaptive learning check
            should_trade = True
            adaptive_confidence = 0.5
            if self.enable_adaptive_learning and order_flow:
                conditions = self._extract_conditions(data, order_flow, alpha_score)
                should_trade, adaptive_confidence = self.adaptive_system.should_trade_in_conditions(
                    conditions
                )

            if not should_trade:
                logger.info(f"{symbol}: Adaptive learning says avoid these conditions")
                return None

            # 6. LLM reasoning (final validation)
            llm_decision = None
            llm_reasoning = ""
            if self.use_llm and self.llm_agent:
                try:
                    llm_result = self.llm_agent.analyze_with_reasoning(
                        symbol=symbol,
                        market_data=data,
                        alpha_signals=alpha_signals,
                        order_flow=order_flow,
                        news=None
                    )
                    llm_decision = llm_result['decision']
                    llm_reasoning = llm_result['full_reasoning']
                except Exception as e:
                    logger.warning(f"LLM reasoning failed: {e}")
                    llm_decision = {
                        "action": "HOLD",
                        "conviction": 0.0,
                        "reasoning": "LLM error",
                        "stop_loss_pips": 15,
                        "take_profit_pips": 30
                    }

            # 7. Combine signals (weighted vote)
            direction, conviction = self._combine_signals(
                alpha_score=alpha_score,
                retail_sentiment=order_flow.retail_sentiment if order_flow else 0.0,
                institutional_flow=order_flow.institutional_sentiment if order_flow else 0.0,
                rl_action=rl_action,
                rl_confidence=rl_confidence,
                llm_decision=llm_decision,
                adaptive_confidence=adaptive_confidence
            )

            if direction == 'HOLD' or conviction < 0.4:
                logger.info(f"{symbol}: No strong signal (conviction: {conviction:.2f})")
                return None

            # 8. Calculate position size and risk parameters
            current_price = float(primary_df['Close'].iloc[-1])

            # Get stop loss from LLM or use default
            stop_loss_pips = 15  # Max for 50x
            take_profit_pips = 30
            if llm_decision:
                stop_loss_pips = min(llm_decision.get('stop_loss_pips', 15), 15)
                take_profit_pips = llm_decision.get('take_profit_pips', 30)

            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                symbol=symbol,
                entry_price=current_price,
                stop_loss_pips=stop_loss_pips,
                direction=direction
            )

            if position_size == 0:
                logger.warning(f"{symbol}: Position size is 0 (risk limit reached)")
                return None

            # Calculate stop loss and take profit prices
            pip_size = 0.01 if 'JPY' in symbol.upper() else 0.0001
            if direction == 'BUY':
                stop_loss_price = current_price - (stop_loss_pips * pip_size)
                take_profit_price = current_price + (take_profit_pips * pip_size)
            else:
                stop_loss_price = current_price + (stop_loss_pips * pip_size)
                take_profit_price = current_price - (take_profit_pips * pip_size)

            # Calculate liquidation price
            liquidation_price = self.risk_manager._calculate_liquidation_price(
                entry_price=current_price,
                lot_size=position_size,
                leverage=self.leverage,
                direction=direction
            )

            # 9. Create enhanced signal
            signal = EnhancedSignal(
                symbol=symbol,
                direction=direction,
                conviction=conviction,
                alpha_score=alpha_score,
                retail_sentiment=order_flow.retail_sentiment if order_flow else 0.0,
                institutional_flow=order_flow.institutional_sentiment if order_flow else 0.0,
                smart_money_direction=order_flow.smart_money_direction if order_flow else 0,
                rl_action=rl_action,
                rl_confidence=rl_confidence,
                llm_decision=llm_decision or {},
                llm_reasoning=llm_reasoning,
                position_size=position_size,
                stop_loss_pips=stop_loss_pips,
                take_profit_pips=take_profit_pips,
                liquidation_price=liquidation_price,
                timestamp=datetime.now(),
                timeframe='H1'
            )

            logger.info(f"\n{'='*60}")
            logger.info(f"SIGNAL GENERATED: {symbol}")
            logger.info(f"{'='*60}")
            logger.info(f"Direction: {direction} | Conviction: {conviction:.2%}")
            logger.info(f"Alpha Score: {alpha_score:.3f}")
            logger.info(f"Retail Sentiment: {signal.retail_sentiment:.2f} (FADE)")
            logger.info(f"Institutional Flow: {signal.institutional_flow:.2f} (FOLLOW)")
            logger.info(f"RL Action: {rl_action} | RL Confidence: {rl_confidence:.2%}")
            logger.info(f"Position Size: {position_size:.2f} lots")
            logger.info(f"Stop Loss: {stop_loss_pips} pips | Take Profit: {take_profit_pips} pips")
            logger.info(f"Liquidation Price: {liquidation_price:.5f}")
            if llm_reasoning:
                logger.info(f"LLM Reasoning:\n{llm_reasoning[:200]}...")
            logger.info(f"{'='*60}\n")

            return signal

        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None

    def execute_signal(self, signal: EnhancedSignal) -> bool:
        """
        Execute trading signal

        Returns:
            True if executed successfully
        """
        try:
            # Check if we can open new position
            if not self.risk_manager.can_open_position(len(self.active_positions)):
                logger.warning(f"Cannot open position: max positions reached")
                return False

            # Check margin health
            if not self.risk_manager.check_margin_health(self.current_equity):
                logger.error(f"MARGIN HEALTH CHECK FAILED - Cannot open new positions")
                return False

            # Check minimum time between trades (prevent overtrading)
            last_trade = self.last_trade_time.get(signal.symbol, datetime.min)
            if (signal.timestamp - last_trade).seconds < 300:  # 5 minutes
                logger.info(f"{signal.symbol}: Too soon since last trade")
                return False

            # Calculate stop loss and take profit prices
            current_price = self.mt5.get_current_price(signal.symbol)
            if not current_price:
                logger.error(f"Cannot get current price for {signal.symbol}")
                return False

            pip_size = 0.01 if 'JPY' in signal.symbol.upper() else 0.0001
            if signal.direction == 'BUY':
                stop_loss = current_price - (signal.stop_loss_pips * pip_size)
                take_profit = current_price + (signal.take_profit_pips * pip_size)
            else:
                stop_loss = current_price + (signal.stop_loss_pips * pip_size)
                take_profit = current_price - (signal.take_profit_pips * pip_size)

            # Execute order
            logger.info(f"Executing {signal.direction} order for {signal.symbol}...")
            result = self.executor.execute_market_order(
                symbol=signal.symbol,
                order_type=signal.direction,
                volume=signal.position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment=f"Enhanced Strategy - Conviction: {signal.conviction:.2%}"
            )

            if result['success']:
                # Track position
                self.active_positions[signal.symbol] = {
                    'signal': signal,
                    'order_id': result.get('order_id'),
                    'entry_price': current_price,
                    'entry_time': signal.timestamp,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }

                self.last_trade_time[signal.symbol] = signal.timestamp

                logger.info(f"✓ Position opened: {signal.symbol} {signal.direction} "
                          f"{signal.position_size} lots @ {current_price:.5f}")
                return True
            else:
                logger.error(f"✗ Order execution failed: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return False

    def update_positions(self):
        """Update active positions and record outcomes for learning"""
        closed_positions = []

        for symbol, position_info in list(self.active_positions.items()):
            # Check if position is still open
            current_price = self.mt5.get_current_price(symbol)
            if not current_price:
                continue

            signal = position_info['signal']
            entry_price = position_info['entry_price']

            # Calculate current P&L
            if signal.direction == 'BUY':
                pnl_pips = (current_price - entry_price) / (0.01 if 'JPY' in symbol else 0.0001)
            else:
                pnl_pips = (entry_price - current_price) / (0.01 if 'JPY' in symbol else 0.0001)

            pnl_usd = pnl_pips * signal.position_size * 10  # $10 per pip per lot

            # Check if position hit stop or target (in dry run, simulate this)
            if self.dry_run:
                hit_stop = (signal.direction == 'BUY' and pnl_pips <= -signal.stop_loss_pips) or \
                          (signal.direction == 'SELL' and pnl_pips <= -signal.stop_loss_pips)
                hit_target = (signal.direction == 'BUY' and pnl_pips >= signal.take_profit_pips) or \
                            (signal.direction == 'SELL' and pnl_pips >= signal.take_profit_pips)

                if hit_stop or hit_target:
                    # Position closed
                    closed_positions.append((symbol, pnl_usd, signal))
                    del self.active_positions[symbol]

                    # Update equity
                    self.current_equity += pnl_usd
                    self.daily_pnl += pnl_usd

                    # Track performance
                    self.performance_metrics['total_trades'] += 1
                    if pnl_usd > 0:
                        self.performance_metrics['winning_trades'] += 1
                    else:
                        self.performance_metrics['losing_trades'] += 1
                    self.performance_metrics['total_pnl'] += pnl_usd

                    logger.info(f"Position closed: {symbol} | P&L: ${pnl_usd:.2f} | "
                              f"Reason: {'Take Profit' if hit_target else 'Stop Loss'}")

        # Record outcomes for learning systems
        for symbol, pnl, signal in closed_positions:
            # Adaptive learning
            if self.enable_adaptive_learning:
                conditions = {
                    'alpha_score': signal.alpha_score,
                    'retail_sentiment': signal.retail_sentiment,
                    'institutional_flow': signal.institutional_flow,
                    'conviction': signal.conviction
                }
                self.adaptive_system.record_trade_outcome(
                    conditions=conditions,
                    outcome=pnl,
                    metadata={'symbol': symbol, 'direction': signal.direction}
                )

            # RL agent learning
            if self.enable_rl:
                # Would need to implement full state tracking for RL
                # For now, just store experience
                pass

        # Update peak equity for drawdown calculation
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity

    def _get_market_data(self, symbol: str) -> Optional[Dict[str, pd.DataFrame]]:
        """Get market data for all timeframes"""
        data = {}
        for tf in self.timeframes:
            df = self.mt5.get_data(symbol, tf, bars=500)
            if df is not None and len(df) > 0:
                data[tf] = df
        return data if data else None

    def _combine_signals(self,
                        alpha_score: float,
                        retail_sentiment: float,
                        institutional_flow: float,
                        rl_action: int,
                        rl_confidence: float,
                        llm_decision: Optional[Dict],
                        adaptive_confidence: float) -> Tuple[str, float]:
        """
        Combine all signals into final decision

        Strategy:
        - Fade retail sentiment (contrarian)
        - Follow institutional flow (smart money)
        - Weight by confidence levels

        Returns:
            Tuple of (direction, conviction)
        """
        votes = []
        weights = []

        # 1. Alpha factors (30% weight)
        if alpha_score > 0.2:
            votes.append(1)  # Buy
            weights.append(0.30 * abs(alpha_score))
        elif alpha_score < -0.2:
            votes.append(-1)  # Sell
            weights.append(0.30 * abs(alpha_score))

        # 2. Retail sentiment - FADE (20% weight)
        if retail_sentiment > 0.3:
            votes.append(-1)  # Fade bullish retail
            weights.append(0.20 * abs(retail_sentiment))
        elif retail_sentiment < -0.3:
            votes.append(1)  # Fade bearish retail
            weights.append(0.20 * abs(retail_sentiment))

        # 3. Institutional flow - FOLLOW (25% weight)
        if institutional_flow > 0.3:
            votes.append(1)  # Follow institutions
            weights.append(0.25 * abs(institutional_flow))
        elif institutional_flow < -0.3:
            votes.append(-1)
            weights.append(0.25 * abs(institutional_flow))

        # 4. RL agent (10% weight)
        if rl_action != 0:
            votes.append(rl_action)
            weights.append(0.10 * rl_confidence)

        # 5. LLM decision (15% weight)
        if llm_decision:
            llm_action = llm_decision.get('action', 'HOLD')
            llm_conviction = llm_decision.get('conviction', 0.0)
            if llm_action == 'BUY':
                votes.append(1)
                weights.append(0.15 * llm_conviction)
            elif llm_action == 'SELL':
                votes.append(-1)
                weights.append(0.15 * llm_conviction)

        # No votes = HOLD
        if not votes:
            return 'HOLD', 0.0

        # Weighted average
        total_weight = sum(weights)
        if total_weight == 0:
            return 'HOLD', 0.0

        weighted_vote = sum(v * w for v, w in zip(votes, weights)) / total_weight

        # Apply adaptive learning confidence
        conviction = abs(weighted_vote) * adaptive_confidence

        # Minimum conviction threshold
        if conviction < 0.4:
            return 'HOLD', conviction

        direction = 'BUY' if weighted_vote > 0 else 'SELL'

        return direction, conviction

    def _extract_conditions(self,
                           data: Dict[str, pd.DataFrame],
                           order_flow,
                           alpha_score: float) -> Dict[str, float]:
        """Extract market conditions for adaptive learning"""
        conditions = {
            'alpha_score': round(alpha_score, 1),
            'retail_sentiment': round(order_flow.retail_sentiment, 1) if order_flow else 0.0,
            'institutional_flow': round(order_flow.institutional_sentiment, 1) if order_flow else 0.0
        }

        # Add volatility
        primary_df = data.get('H1')
        if primary_df is not None and len(primary_df) > 20:
            returns = primary_df['Close'].pct_change()
            conditions['volatility'] = round(returns.std() * 100, 1)

        return conditions

    def run(self, duration_hours: Optional[int] = None):
        """
        Run strategy continuously

        Args:
            duration_hours: Run for specified hours (None = indefinite)
        """
        logger.info("\n" + "="*80)
        logger.info("ENHANCED FOREX STRATEGY - STARTING")
        logger.info("="*80)
        logger.info(f"Symbols: {', '.join(self.symbols)}")
        logger.info(f"Leverage: {self.leverage}x")
        logger.info(f"Initial Balance: ${self.account_balance:,.2f}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        logger.info("="*80 + "\n")

        start_time = datetime.now()
        iteration = 0

        try:
            while True:
                iteration += 1
                logger.info(f"\n--- Iteration {iteration} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

                # Update existing positions
                self.update_positions()

                # Generate and execute signals for each symbol
                for symbol in self.symbols:
                    # Skip if already have position
                    if symbol in self.active_positions:
                        logger.info(f"{symbol}: Position already open, skipping")
                        continue

                    # Generate signal
                    signal = self.generate_signal(symbol)

                    if signal and signal.direction != 'HOLD':
                        # Execute if conviction is high enough
                        if signal.conviction >= 0.5:
                            self.execute_signal(signal)
                        else:
                            logger.info(f"{symbol}: Signal too weak (conviction: {signal.conviction:.2%})")

                # Log status
                logger.info(f"\nStatus: Equity: ${self.current_equity:,.2f} | "
                          f"Daily P&L: ${self.daily_pnl:,.2f} | "
                          f"Active Positions: {len(self.active_positions)}")

                # Check duration
                if duration_hours:
                    elapsed = (datetime.now() - start_time).seconds / 3600
                    if elapsed >= duration_hours:
                        logger.info(f"\nDuration limit reached ({duration_hours} hours)")
                        break

                # Sleep between iterations (60 seconds)
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("\n\nStrategy stopped by user")
        except Exception as e:
            logger.error(f"\n\nStrategy error: {e}")
            raise
        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup and save results"""
        logger.info("\n" + "="*80)
        logger.info("ENHANCED FOREX STRATEGY - SUMMARY")
        logger.info("="*80)
        logger.info(f"Final Equity: ${self.current_equity:,.2f}")
        logger.info(f"Total P&L: ${self.performance_metrics['total_pnl']:,.2f}")
        logger.info(f"Total Trades: {self.performance_metrics['total_trades']}")

        if self.performance_metrics['total_trades'] > 0:
            win_rate = self.performance_metrics['winning_trades'] / self.performance_metrics['total_trades']
            logger.info(f"Win Rate: {win_rate:.1%}")
            logger.info(f"Avg P&L per Trade: ${self.performance_metrics['total_pnl'] / self.performance_metrics['total_trades']:.2f}")

        logger.info("="*80 + "\n")

        # Save learning data
        if self.enable_adaptive_learning:
            insights = self.adaptive_system.get_learning_insights()
            logger.info("Adaptive Learning Insights:")
            for key, value in insights.items():
                logger.info(f"  {key}: {value}")

        # Save RL model
        if self.enable_rl:
            self.rl_agent.save_model("models/rl_agent.pkl")
            logger.info("RL model saved")

        # Disconnect
        self.mt5.disconnect()
        logger.info("Disconnected from MT5")


def main():
    """Main function for running enhanced strategy"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced Forex Trading Strategy')
    parser.add_argument('--symbols', nargs='+', default=['EURUSD', 'GBPUSD'],
                       help='Forex symbols to trade')
    parser.add_argument('--balance', type=float, default=10000.0,
                       help='Account balance')
    parser.add_argument('--leverage', type=int, default=50,
                       help='Leverage (default 50x)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Duration in hours (None = indefinite)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Paper trading mode')
    parser.add_argument('--no-llm', action='store_true',
                       help='Disable LLM reasoning')
    parser.add_argument('--no-rl', action='store_true',
                       help='Disable RL agent')

    args = parser.parse_args()

    # Initialize strategy
    strategy = EnhancedForexStrategy(
        symbols=args.symbols,
        timeframes=['H1', 'M15'],
        account_balance=args.balance,
        leverage=args.leverage,
        use_llm=not args.no_llm,
        enable_rl=not args.no_rl,
        enable_adaptive_learning=True,
        dry_run=args.dry_run
    )

    # Run
    strategy.run(duration_hours=args.duration)


if __name__ == "__main__":
    main()
