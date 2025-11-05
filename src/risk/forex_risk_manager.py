"""
Forex Risk Management System
Handles position sizing, stop loss, take profit, and risk controls
Adapted for high leverage and 24/5 forex markets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = 0.01  # 1% per trade
    MODERATE = 0.02      # 2% per trade
    AGGRESSIVE = 0.03    # 3% per trade


class MarketRegime(Enum):
    """Market regime classification"""
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    RANGING_LOW_VOL = "ranging_low_vol"
    RANGING_HIGH_VOL = "ranging_high_vol"
    VOLATILE_CRASH = "volatile_crash"
    VOLATILE_RECOVERY = "volatile_recovery"


@dataclass
class Position:
    """Trading position"""
    symbol: str
    direction: int  # 1 for long, -1 for short
    entry_price: float
    lot_size: float
    stop_loss: float
    take_profit: float
    entry_time: pd.Timestamp
    timeframe: str
    unrealized_pnl: float = 0.0
    risk_amount: float = 0.0


@dataclass
class RiskMetrics:
    """Risk assessment metrics"""
    var_95: float  # Value at Risk (95%)
    var_99: float  # Value at Risk (99%)
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    current_drawdown: float
    win_rate: float
    profit_factor: float
    risk_reward_ratio: float


class ForexRiskManager:
    """
    Comprehensive risk management for forex trading
    Handles position sizing, regime detection, and portfolio risk
    """

    def __init__(self,
                 account_balance: float,
                 risk_level: RiskLevel = RiskLevel.MODERATE,
                 max_positions: int = 5,
                 max_correlated_positions: int = 3,
                 max_daily_loss: float = 0.05,  # 5%
                 max_drawdown: float = 0.15):   # 15%
        """
        Initialize risk manager

        Args:
            account_balance: Trading account balance
            risk_level: Risk tolerance level
            max_positions: Maximum concurrent positions
            max_correlated_positions: Max positions in correlated pairs
            max_daily_loss: Maximum daily loss (as fraction)
            max_drawdown: Maximum allowed drawdown (as fraction)
        """
        self.account_balance = account_balance
        self.initial_balance = account_balance
        self.risk_level = risk_level
        self.max_positions = max_positions
        self.max_correlated_positions = max_correlated_positions
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown

        self.positions: List[Position] = []
        self.trade_history: List[Dict] = []
        self.daily_pnl: List[float] = []
        self.current_regime = MarketRegime.RANGING_LOW_VOL

        # Forex-specific correlations
        self.correlation_groups = self._init_correlation_groups()

    def _init_correlation_groups(self) -> Dict[str, List[str]]:
        """Initialize currency correlation groups"""
        return {
            'USD_strength': ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY'],
            'EUR_strength': ['EURUSD', 'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD'],
            'GBP_strength': ['GBPUSD', 'EURGBP', 'GBPJPY', 'GBPCHF', 'GBPAUD'],
            'JPY_strength': ['USDJPY', 'EURJPY', 'GBPJPY', 'AUDJPY', 'CADJPY'],
            'Commodity': ['AUDUSD', 'NZDUSD', 'USDCAD'],  # Commodity currencies
        }

    def calculate_position_size(self,
                               symbol: str,
                               entry_price: float,
                               stop_loss_price: float,
                               point_value: float = 10,
                               lot_step: float = 0.01,
                               min_lot: float = 0.01,
                               max_lot: float = 100) -> float:
        """
        Calculate position size based on risk

        Args:
            symbol: Forex pair
            entry_price: Entry price
            stop_loss_price: Stop loss price
            point_value: Value per pip per lot
            lot_step: Lot size increment
            min_lot: Minimum lot size
            max_lot: Maximum lot size

        Returns:
            Lot size
        """
        # Input validation
        if entry_price <= 0 or stop_loss_price <= 0:
            logger.warning(f"Invalid prices for {symbol}: entry={entry_price}, sl={stop_loss_price}")
            return 0.0

        if abs(entry_price - stop_loss_price) < 0.00001:
            logger.warning(f"Stop loss too close to entry for {symbol}")
            return 0.0

        # Risk amount for this trade
        risk_amount = self.account_balance * self.risk_level.value

        # Adjust risk based on regime
        risk_amount *= self._get_regime_risk_multiplier()

        # Adjust risk based on current drawdown
        current_dd = self.get_current_drawdown()
        if current_dd > 0.05:  # If in 5%+ drawdown
            risk_amount *= 0.5  # Reduce risk by half
            logger.info(f"Drawdown {current_dd:.2%}, reducing position size")

        # Calculate stop loss in pips (handle JPY pairs differently)
        pip_size = 0.01 if 'JPY' in symbol.upper() else 0.0001
        stop_loss_pips = abs(entry_price - stop_loss_price) / pip_size

        # Avoid division by zero or too tight stops
        if stop_loss_pips < 1:
            logger.warning(f"Stop loss too tight for {symbol}: {stop_loss_pips:.1f} pips")
            return min_lot

        # Calculate lot size
        lot_size = risk_amount / (stop_loss_pips * point_value)

        # Round to lot step
        lot_size = round(lot_size / lot_step) * lot_step

        # Ensure within limits
        lot_size = max(min_lot, min(lot_size, max_lot))

        # Check if we're at position limit
        if len(self.positions) >= self.max_positions:
            return 0.0

        # Check correlation limits
        if not self._check_correlation_limit(symbol):
            logger.warning(f"Correlation limit reached for {symbol}")
            return 0.0

        return lot_size

    def calculate_stop_loss(self,
                           entry_price: float,
                           direction: int,
                           atr: float,
                           support_resistance: Optional[float] = None,
                           atr_multiplier: float = 2.0) -> float:
        """
        Calculate stop loss price

        Args:
            entry_price: Entry price
            direction: 1 for long, -1 for short
            atr: Average True Range
            support_resistance: Support/resistance level
            atr_multiplier: ATR multiplier for stop distance

        Returns:
            Stop loss price
        """
        # ATR-based stop
        atr_stop = entry_price - (direction * atr * atr_multiplier)

        # If support/resistance provided, use the better one
        if support_resistance is not None:
            if direction == 1:  # Long
                # Use whichever is higher (closer to entry)
                return max(atr_stop, support_resistance)
            else:  # Short
                # Use whichever is lower (closer to entry)
                return min(atr_stop, support_resistance)

        return atr_stop

    def calculate_take_profit(self,
                             entry_price: float,
                             stop_loss: float,
                             direction: int,
                             risk_reward_ratio: float = 2.0) -> float:
        """
        Calculate take profit based on risk-reward ratio

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            direction: 1 for long, -1 for short
            risk_reward_ratio: Desired risk-reward ratio

        Returns:
            Take profit price
        """
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio

        return entry_price + (direction * reward)

    def detect_market_regime(self, data: Dict[str, pd.DataFrame]) -> MarketRegime:
        """
        Detect current market regime

        Args:
            data: Multi-timeframe data

        Returns:
            Detected market regime
        """
        # Use highest timeframe available
        tf_hierarchy = ['D1', 'H4', 'H1', 'M30', 'M15']
        df = None

        for tf in tf_hierarchy:
            if tf in data:
                df = data[tf]
                break

        if df is None or len(df) < 100:
            return MarketRegime.RANGING_LOW_VOL

        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values

        # Calculate indicators
        returns = pd.Series(close).pct_change()
        volatility = returns.std() * np.sqrt(252)

        ma_50 = np.mean(close[-50:])
        ma_20 = np.mean(close[-20:])

        # ADX for trend strength
        import talib
        adx = talib.ADX(high, low, close, timeperiod=14)[-1]

        # Regime detection logic
        is_trending = adx > 25
        is_bullish = close[-1] > ma_50 and ma_20 > ma_50
        is_bearish = close[-1] < ma_50 and ma_20 < ma_50
        is_high_vol = volatility > returns.rolling(50).std().mean() * np.sqrt(252)

        # Recent sharp moves (crash/recovery)
        recent_move = (close[-1] / close[-5]) - 1

        if recent_move < -0.02:  # 2% drop in 5 bars
            regime = MarketRegime.VOLATILE_CRASH
        elif recent_move > 0.02:  # 2% rise in 5 bars
            regime = MarketRegime.VOLATILE_RECOVERY
        elif is_trending and is_bullish:
            regime = MarketRegime.TRENDING_BULL
        elif is_trending and is_bearish:
            regime = MarketRegime.TRENDING_BEAR
        elif is_high_vol:
            regime = MarketRegime.RANGING_HIGH_VOL
        else:
            regime = MarketRegime.RANGING_LOW_VOL

        self.current_regime = regime
        logger.info(f"Market regime detected: {regime.value}")
        return regime

    def _get_regime_risk_multiplier(self) -> float:
        """Get risk adjustment multiplier based on regime"""
        multipliers = {
            MarketRegime.TRENDING_BULL: 1.2,
            MarketRegime.TRENDING_BEAR: 1.2,
            MarketRegime.RANGING_LOW_VOL: 0.8,
            MarketRegime.RANGING_HIGH_VOL: 0.6,
            MarketRegime.VOLATILE_CRASH: 0.3,
            MarketRegime.VOLATILE_RECOVERY: 0.5,
        }
        return multipliers.get(self.current_regime, 1.0)

    def _check_correlation_limit(self, symbol: str) -> bool:
        """Check if adding position violates correlation limits"""
        if not self.positions:
            return True

        # Count positions in same correlation group
        for group_name, group_symbols in self.correlation_groups.items():
            if symbol not in group_symbols:
                continue

            # Count existing positions in this group
            group_position_count = sum(
                1 for pos in self.positions
                if any(pos.symbol.startswith(s[:6]) for s in group_symbols)
            )

            if group_position_count >= self.max_correlated_positions:
                return False

        return True

    def add_position(self, position: Position):
        """Add a new position"""
        self.positions.append(position)
        logger.info(f"Position opened: {position.symbol} {position.direction} "
                   f"{position.lot_size} lots @ {position.entry_price}")

    def close_position(self, position: Position, exit_price: float, exit_time: pd.Timestamp):
        """Close a position and record trade"""
        pnl = (exit_price - position.entry_price) * position.direction * position.lot_size * 10

        trade_record = {
            'symbol': position.symbol,
            'direction': position.direction,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'lot_size': position.lot_size,
            'entry_time': position.entry_time,
            'exit_time': exit_time,
            'pnl': pnl,
            'return': pnl / self.account_balance,
            'regime': self.current_regime.value
        }

        self.trade_history.append(trade_record)
        self.account_balance += pnl
        self.positions.remove(position)

        logger.info(f"Position closed: {position.symbol} PnL: ${pnl:.2f}")

    def update_positions(self, current_prices: Dict[str, Tuple[float, float]]):
        """
        Update all positions with current prices

        Args:
            current_prices: Dict of symbol -> (bid, ask) prices
        """
        for position in self.positions:
            if position.symbol not in current_prices:
                continue

            bid, ask = current_prices[position.symbol]
            exit_price = bid if position.direction == 1 else ask

            position.unrealized_pnl = (
                (exit_price - position.entry_price) *
                position.direction *
                position.lot_size * 10
            )

    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit is reached"""
        if not self.daily_pnl:
            return False

        today_pnl = sum(self.daily_pnl[-1:])
        loss_pct = abs(today_pnl) / self.initial_balance

        if today_pnl < 0 and loss_pct > self.max_daily_loss:
            logger.warning(f"Daily loss limit reached: {loss_pct:.2%}")
            return True

        return False

    def check_max_drawdown(self) -> bool:
        """Check if maximum drawdown is reached"""
        current_dd = self.get_current_drawdown()

        if current_dd > self.max_drawdown:
            logger.warning(f"Maximum drawdown reached: {current_dd:.2%}")
            return True

        return False

    def get_current_drawdown(self) -> float:
        """Calculate current drawdown"""
        peak_balance = self.initial_balance

        for trade in self.trade_history:
            balance_at_trade = self.initial_balance + sum(
                t['pnl'] for t in self.trade_history[:self.trade_history.index(trade)+1]
            )
            peak_balance = max(peak_balance, balance_at_trade)

        current_dd = (peak_balance - self.account_balance) / peak_balance
        return max(0, current_dd)

    def calculate_var(self, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk

        Args:
            confidence: Confidence level (0.95 or 0.99)

        Returns:
            VaR in currency units
        """
        if len(self.trade_history) < 30:
            return 0.0

        returns = [trade['return'] for trade in self.trade_history]
        var = np.percentile(returns, (1 - confidence) * 100)

        return abs(var * self.account_balance)

    def calculate_risk_metrics(self) -> Optional[RiskMetrics]:
        """Calculate comprehensive risk metrics"""
        if len(self.trade_history) < 10:
            return None

        returns = pd.Series([t['return'] for t in self.trade_history])
        pnls = pd.Series([t['pnl'] for t in self.trade_history])

        # Sharpe ratio
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        sortino = (returns.mean() / downside_returns.std() * np.sqrt(252)
                  if len(downside_returns) > 0 and downside_returns.std() > 0 else 0)

        # Max drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_dd = abs(drawdown.min())

        # Win rate
        wins = len(pnls[pnls > 0])
        total = len(pnls)
        win_rate = wins / total if total > 0 else 0

        # Profit factor
        gross_profit = pnls[pnls > 0].sum()
        gross_loss = abs(pnls[pnls < 0].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Average risk-reward
        avg_win = pnls[pnls > 0].mean() if len(pnls[pnls > 0]) > 0 else 0
        avg_loss = abs(pnls[pnls < 0].mean()) if len(pnls[pnls < 0]) > 0 else 1
        risk_reward = avg_win / avg_loss if avg_loss > 0 else 0

        return RiskMetrics(
            var_95=self.calculate_var(0.95),
            var_99=self.calculate_var(0.99),
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            current_drawdown=self.get_current_drawdown(),
            win_rate=win_rate,
            profit_factor=profit_factor,
            risk_reward_ratio=risk_reward
        )

    def should_trade(self) -> Tuple[bool, str]:
        """
        Determine if trading should continue

        Returns:
            Tuple of (can_trade, reason)
        """
        if self.check_daily_loss_limit():
            return False, "Daily loss limit reached"

        if self.check_max_drawdown():
            return False, "Maximum drawdown reached"

        if len(self.positions) >= self.max_positions:
            return False, "Maximum positions reached"

        # Volatility circuit breaker
        if self.current_regime == MarketRegime.VOLATILE_CRASH:
            return False, "Market in crash mode - trading halted"

        return True, "OK"

    def get_position_summary(self) -> Dict:
        """Get summary of current positions"""
        if not self.positions:
            return {'count': 0, 'total_exposure': 0, 'total_pnl': 0}

        total_pnl = sum(pos.unrealized_pnl for pos in self.positions)
        total_exposure = sum(
            pos.entry_price * pos.lot_size * 100000  # Standard lot
            for pos in self.positions
        )

        return {
            'count': len(self.positions),
            'total_exposure': total_exposure,
            'total_pnl': total_pnl,
            'positions': [
                {
                    'symbol': pos.symbol,
                    'direction': 'LONG' if pos.direction == 1 else 'SHORT',
                    'lot_size': pos.lot_size,
                    'entry_price': pos.entry_price,
                    'unrealized_pnl': pos.unrealized_pnl
                }
                for pos in self.positions
            ]
        }
