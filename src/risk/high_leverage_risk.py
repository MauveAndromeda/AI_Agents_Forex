"""
High-Leverage Risk Management (50x-500x)
Specialized controls for forex trading with high leverage
Designed for Forex.com MT5 with 50x leverage on major pairs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeverageLevel(Enum):
    """Supported leverage levels"""
    LEV_50X = 50
    LEV_100X = 100
    LEV_200X = 200
    LEV_500X = 500


@dataclass
class HighLeveragePosition:
    """High-leverage position with enhanced tracking"""
    symbol: str
    direction: int  # 1 long, -1 short
    entry_price: float
    lot_size: float
    leverage: int
    stop_loss: float
    take_profit: float
    entry_time: pd.Timestamp
    max_loss_usd: float  # Maximum loss in USD
    margin_used: float
    liquidation_price: float  # Price at which position is liquidated


class HighLeverageRiskManager:
    """
    Ultra-conservative risk management for high-leverage trading

    Key principles with 50x leverage:
    1. Never risk more than 0.5% per trade (vs 2% at lower leverage)
    2. Tight stops (10-15 pips maximum)
    3. Maximum 2 concurrent positions (vs 5 at lower leverage)
    4. Strict margin monitoring
    5. Automatic deleveraging in drawdown
    6. Correlation limits are critical
    """

    def __init__(self,
                 account_balance: float,
                 leverage: int = 50,
                 max_risk_per_trade: float = 0.005,  # 0.5%
                 max_positions: int = 2,
                 max_daily_loss: float = 0.02,  # 2%
                 max_drawdown: float = 0.05,  # 5%
                 margin_call_buffer: float = 0.3):  # 30% buffer before margin call
        """
        Initialize high-leverage risk manager

        Args:
            account_balance: Trading account balance
            leverage: Leverage level (50x default)
            max_risk_per_trade: Maximum risk per trade (0.5% default)
            max_positions: Maximum concurrent positions (2 default)
            max_daily_loss: Maximum daily loss (2% default)
            max_drawdown: Maximum drawdown (5% default)
            margin_call_buffer: Buffer before margin call (30% default)
        """
        self.account_balance = account_balance
        self.initial_balance = account_balance
        self.leverage = leverage
        self.max_risk_per_trade = max_risk_per_trade
        self.max_positions = max_positions
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.margin_call_buffer = margin_call_buffer

        self.positions: List[HighLeveragePosition] = []
        self.trade_history: List[Dict] = []
        self.daily_pnl: List[float] = []

        logger.info(f"High-leverage risk manager initialized: {leverage}x leverage, "
                   f"{max_risk_per_trade*100:.1f}% risk per trade")

    def calculate_position_size(self,
                               symbol: str,
                               entry_price: float,
                               stop_loss_price: float,
                               leverage: Optional[int] = None) -> Tuple[float, Dict]:
        """
        Calculate position size for high-leverage trading

        Returns:
            Tuple of (lot_size, risk_metrics_dict)
        """
        if leverage is None:
            leverage = self.leverage

        # Input validation
        if entry_price <= 0 or stop_loss_price <= 0:
            logger.error(f"Invalid prices: entry={entry_price}, sl={stop_loss_price}")
            return 0.0, {}

        # Calculate maximum loss in USD
        max_loss_usd = self.account_balance * self.max_risk_per_trade

        # Adjust for current drawdown (reduce risk in drawdown)
        current_dd = self.get_current_drawdown()
        if current_dd > 0.02:  # 2% drawdown
            max_loss_usd *= (1 - current_dd)  # Linear reduction
            logger.warning(f"Drawdown {current_dd:.2%}, reducing position size")

        # Calculate stop loss in pips
        pip_size = 0.01 if 'JPY' in symbol.upper() else 0.0001
        stop_loss_pips = abs(entry_price - stop_loss_price) / pip_size

        # HIGH LEVERAGE CHECK: Enforce maximum stop loss
        MAX_STOP_PIPS = 15  # Maximum 15 pips for 50x leverage
        if stop_loss_pips > MAX_STOP_PIPS:
            logger.warning(f"Stop loss too wide: {stop_loss_pips:.1f} pips "
                          f"(max {MAX_STOP_PIPS} for {leverage}x leverage)")
            # Adjust stop loss to maximum
            stop_loss_pips = MAX_STOP_PIPS
            if entry_price > stop_loss_price:  # Long position
                stop_loss_price = entry_price - (MAX_STOP_PIPS * pip_size)
            else:  # Short position
                stop_loss_price = entry_price + (MAX_STOP_PIPS * pip_size)

        # Minimum stop loss check
        MIN_STOP_PIPS = 5  # Minimum 5 pips to avoid noise
        if stop_loss_pips < MIN_STOP_PIPS:
            logger.warning(f"Stop loss too tight: {stop_loss_pips:.1f} pips")
            return 0.0, {}

        # Calculate lot size
        # For EURUSD: 1 standard lot = 100,000 units, 1 pip = $10
        pip_value = 10  # USD per pip for 1 standard lot
        lot_size = max_loss_usd / (stop_loss_pips * pip_value)

        # Calculate margin required
        # Margin = (lot_size * contract_size * price) / leverage
        contract_size = 100000  # Standard lot
        margin_required = (lot_size * contract_size * entry_price) / leverage

        # Check if we have enough free margin
        used_margin = sum(pos.margin_used for pos in self.positions)
        free_margin = self.account_balance - used_margin
        margin_level = (self.account_balance / used_margin * 100) if used_margin > 0 else 1000

        # Ensure we maintain margin call buffer
        required_free_margin = margin_required * (1 + self.margin_call_buffer)

        if required_free_margin > free_margin:
            logger.warning(f"Insufficient margin: need ${required_free_margin:.2f}, "
                          f"have ${free_margin:.2f}")
            # Scale down lot size
            lot_size = (free_margin / (1 + self.margin_call_buffer)) / (contract_size * entry_price / leverage)

        # Round to lot step (0.01 for most brokers)
        lot_size = round(lot_size, 2)

        # Enforce minimum and maximum
        lot_size = max(0.01, min(lot_size, 10.0))  # Min 0.01, max 10 lots

        # Calculate liquidation price
        liquidation_price = self._calculate_liquidation_price(
            entry_price,
            lot_size,
            leverage,
            1 if entry_price > stop_loss_price else -1
        )

        # Risk metrics
        risk_metrics = {
            'lot_size': lot_size,
            'stop_loss_pips': stop_loss_pips,
            'max_loss_usd': max_loss_usd,
            'margin_required': margin_required,
            'margin_level': margin_level,
            'liquidation_price': liquidation_price,
            'risk_per_trade_pct': (max_loss_usd / self.account_balance) * 100,
            'leverage_used': leverage
        }

        # Additional safety checks
        if len(self.positions) >= self.max_positions:
            logger.warning(f"Maximum positions reached ({self.max_positions})")
            return 0.0, risk_metrics

        if margin_level < 200:  # 200% margin level minimum
            logger.warning(f"Margin level too low: {margin_level:.0f}%")
            return 0.0, risk_metrics

        logger.info(f"Position size calculated: {lot_size} lots, "
                   f"risk ${max_loss_usd:.2f} ({risk_metrics['risk_per_trade_pct']:.2f}%), "
                   f"margin ${margin_required:.2f}")

        return lot_size, risk_metrics

    def _calculate_liquidation_price(self,
                                   entry_price: float,
                                   lot_size: float,
                                   leverage: int,
                                   direction: int) -> float:
        """
        Calculate price at which position would be liquidated

        Liquidation occurs when losses equal margin
        """
        # Margin = position_value / leverage
        contract_size = 100000
        position_value = lot_size * contract_size * entry_price
        margin = position_value / leverage

        # Liquidation when loss = margin
        # For long: liquidation_price = entry - (margin / (lot_size * contract_size))
        # For short: liquidation_price = entry + (margin / (lot_size * contract_size))

        price_move_to_liquidation = margin / (lot_size * contract_size)

        if direction == 1:  # Long
            liquidation_price = entry_price - price_move_to_liquidation
        else:  # Short
            liquidation_price = entry_price + price_move_to_liquidation

        return liquidation_price

    def check_margin_health(self) -> Tuple[bool, str]:
        """
        Check margin health and risk of margin call

        Returns:
            Tuple of (is_healthy, warning_message)
        """
        if not self.positions:
            return True, "No open positions"

        used_margin = sum(pos.margin_used for pos in self.positions)
        margin_level = (self.account_balance / used_margin * 100) if used_margin > 0 else 1000

        # Warning levels
        if margin_level < 150:
            return False, f"CRITICAL: Margin level {margin_level:.0f}% - Risk of margin call"
        elif margin_level < 200:
            return False, f"WARNING: Margin level {margin_level:.0f}% - Close positions"
        elif margin_level < 300:
            return True, f"CAUTION: Margin level {margin_level:.0f}% - Monitor closely"
        else:
            return True, f"Healthy margin level: {margin_level:.0f}%"

    def should_trade(self) -> Tuple[bool, str]:
        """
        Determine if trading should continue (high-leverage specific)

        More conservative than standard risk manager
        """
        # Daily loss check
        if self.daily_pnl:
            today_pnl = sum(self.daily_pnl[-1:])
            if today_pnl < -self.max_daily_loss * self.account_balance:
                return False, f"Daily loss limit reached: ${today_pnl:.2f}"

        # Drawdown check
        current_dd = self.get_current_drawdown()
        if current_dd > self.max_drawdown:
            return False, f"Maximum drawdown reached: {current_dd:.2%}"

        # Position limit check
        if len(self.positions) >= self.max_positions:
            return False, f"Maximum positions reached ({self.max_positions})"

        # Margin health check
        is_healthy, msg = self.check_margin_health()
        if not is_healthy:
            return False, msg

        # Time-based checks (avoid high-impact news)
        current_time = pd.Timestamp.now()
        # Avoid trading 5 minutes before and after major news
        # (In production, integrate with news calendar API)

        return True, "OK"

    def get_current_drawdown(self) -> float:
        """Calculate current drawdown"""
        if not self.trade_history:
            return 0.0

        peak_balance = self.initial_balance
        for trade in self.trade_history:
            balance_after_trade = self.initial_balance + sum(
                t['pnl'] for t in self.trade_history[:self.trade_history.index(trade)+1]
            )
            peak_balance = max(peak_balance, balance_after_trade)

        current_dd = (peak_balance - self.account_balance) / peak_balance
        return max(0, current_dd)

    def monitor_positions(self, current_prices: Dict[str, Tuple[float, float]]):
        """
        Monitor positions for margin call risk

        Args:
            current_prices: Dict of symbol -> (bid, ask)
        """
        for position in self.positions:
            if position.symbol not in current_prices:
                continue

            bid, ask = current_prices[position.symbol]
            current_price = bid if position.direction == 1 else ask

            # Check distance to liquidation
            if position.direction == 1:  # Long
                distance_to_liquidation = (current_price - position.liquidation_price) / position.liquidation_price
            else:  # Short
                distance_to_liquidation = (position.liquidation_price - current_price) / position.liquidation_price

            # Warning if within 50% of liquidation
            if distance_to_liquidation < 0.5:
                logger.warning(f"LIQUIDATION RISK: {position.symbol} "
                             f"{distance_to_liquidation*100:.1f}% from liquidation price")

            # Calculate unrealized P&L
            pip_size = 0.01 if 'JPY' in position.symbol.upper() else 0.0001
            pips = (current_price - position.entry_price) / pip_size * position.direction
            unrealized_pnl = pips * 10 * position.lot_size

            # Check if approaching stop loss
            if position.direction == 1:
                distance_to_stop = (current_price - position.stop_loss) / position.stop_loss
            else:
                distance_to_stop = (position.stop_loss - current_price) / position.stop_loss

            if distance_to_stop < 0.2:  # Within 20% of stop loss
                logger.info(f"{position.symbol} approaching stop loss: {distance_to_stop*100:.1f}%")

    def get_risk_summary(self) -> Dict:
        """Get comprehensive risk summary"""
        used_margin = sum(pos.margin_used for pos in self.positions)
        total_exposure = sum(
            pos.lot_size * 100000 * pos.entry_price
            for pos in self.positions
        )

        margin_level = (self.account_balance / used_margin * 100) if used_margin > 0 else 1000

        return {
            'account_balance': self.account_balance,
            'leverage': self.leverage,
            'open_positions': len(self.positions),
            'used_margin': used_margin,
            'free_margin': self.account_balance - used_margin,
            'margin_level': margin_level,
            'total_exposure': total_exposure,
            'effective_leverage': total_exposure / self.account_balance if self.account_balance > 0 else 0,
            'current_drawdown': self.get_current_drawdown(),
            'daily_pnl': sum(self.daily_pnl[-1:]) if self.daily_pnl else 0,
            'can_trade': self.should_trade()[0],
            'risk_status': self.check_margin_health()[1]
        }
