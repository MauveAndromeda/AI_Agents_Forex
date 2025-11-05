"""
Forex Backtesting Engine
Multi-timeframe backtesting with realistic execution modeling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict

from ..data.mt5_connector import MT5Connector, Timeframe
from ..models.forex_alpha_factors import ForexAlphaFactors, AlphaSignal
from ..agents.trading_agents import MultiAgentTradingSystem, TradingDecision, TradeDirection
from ..risk.forex_risk_manager import ForexRiskManager, Position, RiskLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Backtest configuration"""
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    initial_balance: float
    risk_level: RiskLevel
    timeframes: List[Timeframe]
    primary_timeframe: Timeframe
    spread_pips: float = 2.0  # Average spread
    slippage_pips: float = 0.5  # Average slippage
    commission_per_lot: float = 7.0  # Round-trip commission


@dataclass
class BacktestResults:
    """Backtest results"""
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_trade_duration: timedelta
    final_balance: float
    trades: List[Dict]
    equity_curve: pd.Series


class ForexBacktester:
    """
    Comprehensive forex backtesting system
    Supports multi-timeframe analysis and realistic execution
    """

    def __init__(self,
                 config: BacktestConfig,
                 mt5_connector: MT5Connector,
                 use_ai: bool = True):
        """
        Initialize backtester

        Args:
            config: Backtest configuration
            mt5_connector: MT5 data connector
            use_ai: Use AI agents (requires API keys)
        """
        self.config = config
        self.connector = mt5_connector
        self.use_ai = use_ai

        # Initialize components
        self.alpha_factors = ForexAlphaFactors()
        self.risk_manager = ForexRiskManager(
            account_balance=config.initial_balance,
            risk_level=config.risk_level
        )

        if use_ai:
            try:
                from ..ai.unified_llm_client import UnifiedLLMClient, LLMProvider
                llm_client = UnifiedLLMClient([LLMProvider.DEEPSEEK])
                self.agent_system = MultiAgentTradingSystem(llm_client)
            except Exception as e:
                logger.warning(f"AI initialization failed: {e}. Running without AI.")
                self.agent_system = MultiAgentTradingSystem(None)
                self.use_ai = False
        else:
            self.agent_system = MultiAgentTradingSystem(None)

        # Backtest state
        self.current_positions: Dict[str, Position] = {}
        self.closed_trades: List[Dict] = []
        self.equity_curve: List[Tuple[datetime, float]] = []

    def run(self) -> BacktestResults:
        """
        Run backtest

        Returns:
            Backtest results
        """
        logger.info(f"Starting backtest: {self.config.start_date} to {self.config.end_date}")
        logger.info(f"Symbols: {self.config.symbols}")
        logger.info(f"Timeframes: {[tf.name for tf in self.config.timeframes]}")

        # Generate date range (daily steps)
        date_range = pd.date_range(
            start=self.config.start_date,
            end=self.config.end_date,
            freq='D'
        )

        for current_date in date_range:
            if current_date.weekday() >= 5:  # Skip weekends
                continue

            self._process_day(current_date)

        # Close all remaining positions
        self._close_all_positions(self.config.end_date)

        # Calculate results
        results = self._calculate_results()

        logger.info(f"Backtest complete. Final balance: ${results.final_balance:.2f}")
        logger.info(f"Total return: {results.total_return:.2%}")
        logger.info(f"Sharpe ratio: {results.sharpe_ratio:.2f}")
        logger.info(f"Max drawdown: {results.max_drawdown:.2%}")
        logger.info(f"Win rate: {results.win_rate:.2%}")

        return results

    def _process_day(self, current_date: datetime):
        """Process one day of trading"""
        logger.info(f"Processing {current_date.date()}")

        # Update existing positions and check stops
        self._update_positions(current_date)

        # Check if we can trade
        can_trade, reason = self.risk_manager.should_trade()
        if not can_trade:
            logger.info(f"Trading halted: {reason}")
            return

        # Scan symbols for opportunities
        for symbol in self.config.symbols:
            # Skip if already have position
            if symbol in self.current_positions:
                continue

            # Get multi-timeframe data
            data = self._get_multi_timeframe_data(symbol, current_date)
            if not data:
                continue

            # Calculate alpha factors
            alpha_signals = self.alpha_factors.calculate_all_factors(data, symbol)

            # Run agent analysis
            account_info = {
                'balance': self.risk_manager.account_balance,
                'equity': self.risk_manager.account_balance,
                'free_margin': self.risk_manager.account_balance * 0.5
            }

            decision = self.agent_system.analyze_and_decide(
                symbol=symbol,
                data=data,
                alpha_signals=alpha_signals,
                account_info=account_info,
                current_positions=len(self.current_positions),
                account_can_trade=can_trade,
                news=None  # Could add news data here
            )

            if decision:
                self._execute_trade(decision, current_date, data)

        # Record equity
        self.equity_curve.append((current_date, self.risk_manager.account_balance))

    def _get_multi_timeframe_data(self,
                                  symbol: str,
                                  current_date: datetime) -> Optional[Dict[str, pd.DataFrame]]:
        """Get multi-timeframe data up to current date"""
        data = {}

        end_date = current_date
        start_date = current_date - timedelta(days=365)  # 1 year of history

        for timeframe in self.config.timeframes:
            df = self.connector.get_rates(symbol, timeframe, start_date, end_date)
            if df is not None and len(df) > 100:
                # Only use data up to current date
                df = df[df.index <= current_date]
                data[timeframe.name] = df

        return data if data else None

    def _execute_trade(self,
                      decision: TradingDecision,
                      current_date: datetime,
                      data: Dict[str, pd.DataFrame]):
        """Execute a trade based on decision"""
        # Apply spread and slippage
        entry_price = decision.entry_price
        if decision.direction == TradeDirection.LONG:
            entry_price += (self.config.spread_pips + self.config.slippage_pips) * 0.0001
        else:
            entry_price -= (self.config.spread_pips + self.config.slippage_pips) * 0.0001

        # Calculate position size
        lot_size = self.risk_manager.calculate_position_size(
            symbol=decision.symbol,
            entry_price=entry_price,
            stop_loss_price=decision.stop_loss,
            point_value=10,
            lot_step=0.01,
            min_lot=0.01,
            max_lot=10.0
        )

        if lot_size == 0:
            logger.info(f"Position size = 0, skipping trade for {decision.symbol}")
            return

        # Apply commission
        commission = lot_size * self.config.commission_per_lot
        self.risk_manager.account_balance -= commission

        # Create position
        position = Position(
            symbol=decision.symbol,
            direction=decision.direction.value,
            entry_price=entry_price,
            lot_size=lot_size,
            stop_loss=decision.stop_loss,
            take_profit=decision.take_profit,
            entry_time=pd.Timestamp(current_date),
            timeframe=decision.timeframe,
            risk_amount=abs(entry_price - decision.stop_loss) * lot_size * 10
        )

        self.current_positions[decision.symbol] = position
        self.risk_manager.add_position(position)

        logger.info(f"Trade executed: {decision.symbol} {decision.direction.name} "
                   f"{lot_size} lots @ {entry_price:.5f} "
                   f"SL: {decision.stop_loss:.5f} TP: {decision.take_profit:.5f}")

    def _update_positions(self, current_date: datetime):
        """Update positions and check stop loss / take profit"""
        symbols_to_close = []

        for symbol, position in self.current_positions.items():
            # Get current price
            data = self._get_multi_timeframe_data(symbol, current_date)
            if not data:
                continue

            primary_df = data[self.config.primary_timeframe.name]
            if len(primary_df) == 0:
                continue

            current_bar = primary_df.iloc[-1]
            current_high = current_bar['High']
            current_low = current_bar['Low']
            current_close = current_bar['Close']

            # Check stop loss
            if position.direction == 1:  # Long
                if current_low <= position.stop_loss:
                    # Stop loss hit
                    exit_price = position.stop_loss
                    self._close_position(position, exit_price, current_date, "Stop Loss")
                    symbols_to_close.append(symbol)
                    continue
                # Check take profit
                elif current_high >= position.take_profit:
                    # Take profit hit
                    exit_price = position.take_profit
                    self._close_position(position, exit_price, current_date, "Take Profit")
                    symbols_to_close.append(symbol)
                    continue

            else:  # Short
                if current_high >= position.stop_loss:
                    # Stop loss hit
                    exit_price = position.stop_loss
                    self._close_position(position, exit_price, current_date, "Stop Loss")
                    symbols_to_close.append(symbol)
                    continue
                # Check take profit
                elif current_low <= position.take_profit:
                    # Take profit hit
                    exit_price = position.take_profit
                    self._close_position(position, exit_price, current_date, "Take Profit")
                    symbols_to_close.append(symbol)
                    continue

            # Update unrealized P&L
            position.unrealized_pnl = (
                (current_close - position.entry_price) *
                position.direction *
                position.lot_size * 100000 / 10000  # Assuming standard lot
            )

        # Remove closed positions
        for symbol in symbols_to_close:
            del self.current_positions[symbol]

    def _close_position(self,
                       position: Position,
                       exit_price: float,
                       exit_time: datetime,
                       reason: str):
        """Close a position"""
        # Calculate P&L (using standard lot calculation)
        pip_value = 10  # USD per pip for standard lot
        pips = (exit_price - position.entry_price) * 10000 * position.direction
        pnl = pips * pip_value * position.lot_size

        # Apply commission
        commission = position.lot_size * self.config.commission_per_lot
        pnl -= commission

        # Update balance
        self.risk_manager.account_balance += pnl

        # Record trade
        trade_record = {
            'symbol': position.symbol,
            'direction': 'LONG' if position.direction == 1 else 'SHORT',
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'lot_size': position.lot_size,
            'entry_time': position.entry_time,
            'exit_time': pd.Timestamp(exit_time),
            'pnl': pnl,
            'pips': pips,
            'return_pct': (pnl / self.config.initial_balance) * 100,
            'exit_reason': reason,
            'duration': pd.Timestamp(exit_time) - position.entry_time
        }

        self.closed_trades.append(trade_record)
        self.risk_manager.close_position(position, exit_price, pd.Timestamp(exit_time))

        logger.info(f"Position closed: {position.symbol} {reason} "
                   f"P&L: ${pnl:.2f} ({pips:.1f} pips)")

    def _close_all_positions(self, exit_time: datetime):
        """Close all remaining positions at end of backtest"""
        for symbol, position in list(self.current_positions.items()):
            data = self._get_multi_timeframe_data(symbol, exit_time)
            if data:
                primary_df = data[self.config.primary_timeframe.name]
                exit_price = primary_df.iloc[-1]['Close']
                self._close_position(position, exit_price, exit_time, "End of Backtest")

        self.current_positions.clear()

    def _calculate_results(self) -> BacktestResults:
        """Calculate backtest performance metrics"""
        if not self.closed_trades:
            return BacktestResults(
                total_return=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                avg_win=0.0,
                avg_loss=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                avg_trade_duration=timedelta(0),
                final_balance=self.config.initial_balance,
                trades=[],
                equity_curve=pd.Series()
            )

        trades_df = pd.DataFrame(self.closed_trades)

        # Basic metrics
        total_return = (self.risk_manager.account_balance - self.config.initial_balance) / self.config.initial_balance
        final_balance = self.risk_manager.account_balance

        # Win/Loss metrics
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        win_rate = len(winning_trades) / len(trades_df)
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        largest_win = winning_trades['pnl'].max() if len(winning_trades) > 0 else 0
        largest_loss = losing_trades['pnl'].min() if len(losing_trades) > 0 else 0

        # Profit factor
        gross_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Risk metrics
        returns = trades_df['return_pct'] / 100
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        downside_returns = returns[returns < 0]
        sortino_ratio = (returns.mean() / downside_returns.std() * np.sqrt(252)
                        if len(downside_returns) > 0 and downside_returns.std() > 0 else 0)

        # Drawdown
        equity_series = pd.Series([eq[1] for eq in self.equity_curve],
                                 index=[eq[0] for eq in self.equity_curve])
        cumulative = equity_series / self.config.initial_balance
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())

        # Trade duration
        avg_duration = trades_df['duration'].mean()

        return BacktestResults(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(trades_df),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            avg_trade_duration=avg_duration,
            final_balance=final_balance,
            trades=self.closed_trades,
            equity_curve=equity_series
        )

    def save_results(self, results: BacktestResults, output_dir: str = "backtest_results"):
        """Save backtest results to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Save trades CSV
        trades_df = pd.DataFrame(results.trades)
        trades_df.to_csv(f"{output_dir}/trades.csv", index=False)

        # Save equity curve
        results.equity_curve.to_csv(f"{output_dir}/equity_curve.csv")

        # Save summary
        summary = {
            'Total Return': f"{results.total_return:.2%}",
            'Sharpe Ratio': f"{results.sharpe_ratio:.2f}",
            'Sortino Ratio': f"{results.sortino_ratio:.2f}",
            'Max Drawdown': f"{results.max_drawdown:.2%}",
            'Win Rate': f"{results.win_rate:.2%}",
            'Profit Factor': f"{results.profit_factor:.2f}",
            'Total Trades': results.total_trades,
            'Winning Trades': results.winning_trades,
            'Losing Trades': results.losing_trades,
            'Average Win': f"${results.avg_win:.2f}",
            'Average Loss': f"${results.avg_loss:.2f}",
            'Largest Win': f"${results.largest_win:.2f}",
            'Largest Loss': f"${results.largest_loss:.2f}",
            'Final Balance': f"${results.final_balance:.2f}"
        }

        summary_df = pd.DataFrame(list(summary.items()), columns=['Metric', 'Value'])
        summary_df.to_csv(f"{output_dir}/summary.csv", index=False)

        logger.info(f"Results saved to {output_dir}/")
