"""
Forex Trading Strategy
Combines multi-timeframe analysis, AI agents, and risk management
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..data.mt5_connector import MT5Connector, Timeframe
from ..models.forex_alpha_factors import ForexAlphaFactors
from ..agents.trading_agents import MultiAgentTradingSystem, TradingDecision, TradeDirection
from ..risk.forex_risk_manager import ForexRiskManager, Position, RiskLevel
from ..execution.mt5_executor import MT5OrderExecutor, OrderType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForexStrategy:
    """
    Main trading strategy class
    Orchestrates data fetching, analysis, decision making, and execution
    """

    def __init__(self,
                 symbols: List[str],
                 timeframes: List[Timeframe],
                 initial_balance: float,
                 risk_level: RiskLevel = RiskLevel.MODERATE,
                 use_ai: bool = True,
                 dry_run: bool = True):
        """
        Initialize strategy

        Args:
            symbols: List of forex pairs to trade
            timeframes: List of timeframes to analyze
            initial_balance: Starting account balance
            risk_level: Risk tolerance level
            use_ai: Use AI agents for decision making
            dry_run: If True, log trades but don't execute
        """
        self.symbols = symbols
        self.timeframes = timeframes
        self.dry_run = dry_run

        # Initialize components
        self.connector = MT5Connector()
        self.alpha_factors = ForexAlphaFactors()
        self.risk_manager = ForexRiskManager(
            account_balance=initial_balance,
            risk_level=risk_level
        )

        if not dry_run:
            self.executor = MT5OrderExecutor()
        else:
            self.executor = None

        # Initialize AI agents
        if use_ai:
            try:
                from ..ai.unified_llm_client import UnifiedLLMClient, LLMProvider
                llm_client = UnifiedLLMClient([LLMProvider.DEEPSEEK])
                self.agent_system = MultiAgentTradingSystem(llm_client)
            except Exception as e:
                logger.warning(f"AI initialization failed: {e}. Running without AI.")
                self.agent_system = MultiAgentTradingSystem(None)
        else:
            self.agent_system = MultiAgentTradingSystem(None)

        self.active_positions: Dict[str, Position] = {}

    def initialize(self) -> bool:
        """Initialize connections"""
        if not self.connector.connect():
            logger.error("Failed to connect to MT5")
            return False

        logger.info("Strategy initialized successfully")
        return True

    def shutdown(self):
        """Cleanup and disconnect"""
        self.connector.disconnect()
        logger.info("Strategy shutdown complete")

    def scan_for_opportunities(self) -> List[TradingDecision]:
        """
        Scan all symbols for trading opportunities

        Returns:
            List of trading decisions
        """
        decisions = []

        for symbol in self.symbols:
            # Skip if already have position
            if symbol in self.active_positions:
                continue

            # Get multi-timeframe data
            data = self.connector.get_multi_timeframe_data(
                symbol,
                self.timeframes,
                count=500
            )

            if not data:
                logger.warning(f"No data for {symbol}")
                continue

            # Calculate alpha factors
            alpha_signals = self.alpha_factors.calculate_all_factors(data, symbol)

            # Get account info
            account_info = self.connector.get_account_info()
            if not account_info:
                account_info = {
                    'balance': self.risk_manager.account_balance,
                    'equity': self.risk_manager.account_balance
                }

            # Check if can trade
            can_trade, reason = self.risk_manager.should_trade()

            # Run agent analysis
            decision = self.agent_system.analyze_and_decide(
                symbol=symbol,
                data=data,
                alpha_signals=alpha_signals,
                account_info=account_info,
                current_positions=len(self.active_positions),
                account_can_trade=can_trade,
                news=None
            )

            if decision:
                decisions.append(decision)
                logger.info(f"Trade opportunity: {symbol} {decision.direction.name} "
                          f"(confidence: {decision.confidence:.2%})")

        return decisions

    def execute_decision(self, decision: TradingDecision) -> bool:
        """
        Execute trading decision

        Args:
            decision: Trading decision from agents

        Returns:
            True if successful
        """
        if self.dry_run:
            logger.info(f"DRY RUN: Would execute {decision.symbol} "
                       f"{decision.direction.name} @ {decision.entry_price}")
            return True

        # Calculate position size
        lot_size = self.risk_manager.calculate_position_size(
            symbol=decision.symbol,
            entry_price=decision.entry_price,
            stop_loss_price=decision.stop_loss,
            point_value=10,
            lot_step=0.01,
            min_lot=0.01,
            max_lot=10.0
        )

        if lot_size == 0:
            logger.warning(f"Position size is 0 for {decision.symbol}, skipping")
            return False

        # Execute order
        order_type = OrderType.BUY if decision.direction == TradeDirection.LONG else OrderType.SELL

        result = self.executor.place_market_order(
            symbol=decision.symbol,
            order_type=order_type,
            lot_size=lot_size,
            stop_loss=decision.stop_loss,
            take_profit=decision.take_profit,
            comment=f"AI Strategy - {decision.confidence:.2%} conf"
        )

        if result.success:
            # Create position record
            position = Position(
                symbol=decision.symbol,
                direction=decision.direction.value,
                entry_price=result.price,
                lot_size=lot_size,
                stop_loss=decision.stop_loss,
                take_profit=decision.take_profit,
                entry_time=pd.Timestamp.now(),
                timeframe=decision.timeframe
            )

            self.active_positions[decision.symbol] = position
            self.risk_manager.add_position(position)

            logger.info(f"Position opened: {decision.symbol} {order_type.name} "
                       f"{lot_size} lots @ {result.price}")
            return True
        else:
            logger.error(f"Order execution failed: {result.error_message}")
            return False

    def update_positions(self):
        """Update and manage active positions"""
        if self.dry_run:
            return

        # Get current positions from MT5
        open_positions = self.executor.get_open_positions()
        open_tickets = {pos.ticket for pos in open_positions}

        # Check if any positions were closed externally
        closed_symbols = []
        for symbol, position in self.active_positions.items():
            # In real implementation, would track ticket numbers
            # For now, just check if position still exists
            if symbol not in [pos.symbol for pos in open_positions]:
                closed_symbols.append(symbol)

        # Remove closed positions
        for symbol in closed_symbols:
            position = self.active_positions[symbol]
            # Get exit price from history
            current_price = self.connector.get_current_price(symbol)
            if current_price:
                exit_price = current_price[0] if position.direction == 1 else current_price[1]
                self.risk_manager.close_position(position, exit_price, pd.Timestamp.now())

            del self.active_positions[symbol]
            logger.info(f"Position closed: {symbol}")

    def run_single_iteration(self):
        """Run one iteration of the strategy"""
        logger.info("=" * 60)
        logger.info("Running strategy iteration")

        # Update existing positions
        self.update_positions()

        # Check market regime
        # Get data for regime detection
        sample_symbol = self.symbols[0]
        sample_data = self.connector.get_multi_timeframe_data(
            sample_symbol,
            self.timeframes[-1:],  # Use highest timeframe
            count=200
        )

        if sample_data:
            regime = self.risk_manager.detect_market_regime(sample_data)
            logger.info(f"Market regime: {regime.value}")

        # Scan for opportunities
        decisions = self.scan_for_opportunities()

        logger.info(f"Found {len(decisions)} trading opportunities")

        # Execute decisions
        for decision in decisions:
            if len(self.active_positions) >= self.risk_manager.max_positions:
                logger.info("Maximum positions reached, stopping")
                break

            self.execute_decision(decision)

        # Log status
        logger.info(f"Active positions: {len(self.active_positions)}")
        logger.info(f"Account balance: ${self.risk_manager.account_balance:.2f}")

        if self.risk_manager.trade_history:
            metrics = self.risk_manager.calculate_risk_metrics()
            if metrics:
                logger.info(f"Sharpe: {metrics.sharpe_ratio:.2f}, "
                          f"Win rate: {metrics.win_rate:.2%}, "
                          f"Max DD: {metrics.max_drawdown:.2%}")

        logger.info("=" * 60)

    def run_continuous(self, interval_minutes: int = 60):
        """
        Run strategy continuously

        Args:
            interval_minutes: Minutes between iterations
        """
        import time

        logger.info(f"Starting continuous trading (interval: {interval_minutes} min)")

        try:
            while True:
                self.run_single_iteration()

                logger.info(f"Waiting {interval_minutes} minutes until next iteration...")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in continuous run: {e}", exc_info=True)
        finally:
            self.shutdown()


# Example usage
if __name__ == "__main__":
    from config import Config

    # Initialize strategy
    strategy = ForexStrategy(
        symbols=['EURUSD', 'GBPUSD', 'USDJPY'],
        timeframes=[Timeframe.H1, Timeframe.H4, Timeframe.D1],
        initial_balance=10000,
        risk_level=RiskLevel.MODERATE,
        use_ai=True,
        dry_run=True  # Set to False for live trading
    )

    if strategy.initialize():
        # Run single iteration
        strategy.run_single_iteration()

        # Or run continuously
        # strategy.run_continuous(interval_minutes=60)

        strategy.shutdown()
