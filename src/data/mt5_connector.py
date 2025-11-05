"""
MT5 Data Connector for Forex Trading System
Handles connection, data retrieval, and real-time streaming from MetaTrader 5
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Timeframe(Enum):
    """MT5 Timeframe mappings"""
    M1 = mt5.TIMEFRAME_M1
    M5 = mt5.TIMEFRAME_M5
    M15 = mt5.TIMEFRAME_M15
    M30 = mt5.TIMEFRAME_M30
    H1 = mt5.TIMEFRAME_H1
    H4 = mt5.TIMEFRAME_H4
    D1 = mt5.TIMEFRAME_D1
    W1 = mt5.TIMEFRAME_W1
    MN1 = mt5.TIMEFRAME_MN1


@dataclass
class ForexSymbol:
    """Forex symbol configuration"""
    symbol: str
    description: str
    digits: int
    point: float
    min_lot: float
    max_lot: float
    lot_step: float
    contract_size: float


class MT5Connector:
    """
    MT5 Connection and Data Management
    Supports multiple timeframes and forex pairs
    """

    def __init__(self, account: int = None, password: str = None, server: str = None):
        """
        Initialize MT5 connection

        Args:
            account: MT5 account number
            password: MT5 password
            server: MT5 server name
        """
        self.account = account
        self.password = password
        self.server = server
        self.connected = False
        self.symbols_info = {}

    def connect(self) -> bool:
        """Establish connection to MT5"""
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False

            if self.account and self.password and self.server:
                authorized = mt5.login(self.account, password=self.password, server=self.server)
                if not authorized:
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    return False

            self.connected = True
            logger.info("MT5 connection established")
            return True

        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Close MT5 connection"""
        mt5.shutdown()
        self.connected = False
        logger.info("MT5 connection closed")

    def get_forex_pairs(self, include_majors: bool = True,
                       include_minors: bool = True,
                       include_exotics: bool = False) -> List[str]:
        """
        Get available forex pairs

        Returns:
            List of forex pair symbols
        """
        majors = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
            "AUDUSD", "USDCAD", "NZDUSD"
        ]

        minors = [
            "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
            "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD",
            "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
            "CADJPY", "CHFJPY", "NZDJPY", "NZDCHF", "NZDCAD"
        ]

        exotics = [
            "USDZAR", "USDTRY", "USDMXN", "USDSEK", "USDNOK",
            "EURPLN", "EURHUF", "EURTRY", "GBPTRY", "GBPZAR"
        ]

        pairs = []
        if include_majors:
            pairs.extend(majors)
        if include_minors:
            pairs.extend(minors)
        if include_exotics:
            pairs.extend(exotics)

        # Verify symbols exist in MT5
        available_pairs = []
        for symbol in pairs:
            if mt5.symbol_info(symbol) is not None:
                available_pairs.append(symbol)
            else:
                # Try with suffix (e.g., EURUSD.raw, EURUSD.pro)
                for suffix in ["", ".raw", ".pro", ".ecn", ".m"]:
                    test_symbol = f"{symbol}{suffix}"
                    if mt5.symbol_info(test_symbol) is not None:
                        available_pairs.append(test_symbol)
                        break

        logger.info(f"Found {len(available_pairs)} available forex pairs")
        return available_pairs

    def get_symbol_info(self, symbol: str) -> Optional[ForexSymbol]:
        """Get detailed symbol information"""
        if symbol in self.symbols_info:
            return self.symbols_info[symbol]

        info = mt5.symbol_info(symbol)
        if info is None:
            logger.warning(f"Symbol {symbol} not found")
            return None

        forex_symbol = ForexSymbol(
            symbol=symbol,
            description=info.description,
            digits=info.digits,
            point=info.point,
            min_lot=info.volume_min,
            max_lot=info.volume_max,
            lot_step=info.volume_step,
            contract_size=info.trade_contract_size
        )

        self.symbols_info[symbol] = forex_symbol
        return forex_symbol

    def get_rates(self, symbol: str, timeframe: Timeframe,
                 start: datetime, end: datetime) -> Optional[pd.DataFrame]:
        """
        Get historical rate data

        Args:
            symbol: Forex pair symbol
            timeframe: Timeframe enum
            start: Start datetime
            end: End datetime

        Returns:
            DataFrame with OHLCV data
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return None

        rates = mt5.copy_rates_range(symbol, timeframe.value, start, end)

        if rates is None or len(rates) == 0:
            logger.warning(f"No data for {symbol} {timeframe.name}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        # Rename columns for consistency
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume',
            'spread': 'Spread'
        }, inplace=True)

        return df

    def get_rates_bars(self, symbol: str, timeframe: Timeframe,
                      count: int = 1000) -> Optional[pd.DataFrame]:
        """
        Get last N bars

        Args:
            symbol: Forex pair symbol
            timeframe: Timeframe enum
            count: Number of bars

        Returns:
            DataFrame with OHLCV data
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return None

        rates = mt5.copy_rates_from_pos(symbol, timeframe.value, 0, count)

        if rates is None or len(rates) == 0:
            logger.warning(f"No data for {symbol} {timeframe.name}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume',
            'spread': 'Spread'
        }, inplace=True)

        return df

    def get_multi_timeframe_data(self, symbol: str,
                                timeframes: List[Timeframe],
                                count: int = 1000) -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple timeframes

        Args:
            symbol: Forex pair symbol
            timeframes: List of timeframes
            count: Number of bars per timeframe

        Returns:
            Dictionary with timeframe as key and DataFrame as value
        """
        data = {}
        for tf in timeframes:
            df = self.get_rates_bars(symbol, tf, count)
            if df is not None:
                data[tf.name] = df

        return data

    def get_current_price(self, symbol: str) -> Optional[Tuple[float, float]]:
        """
        Get current bid/ask price

        Returns:
            Tuple of (bid, ask) prices
        """
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        return (tick.bid, tick.ask)

    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        account = mt5.account_info()
        if account is None:
            return None

        return {
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'free_margin': account.margin_free,
            'margin_level': account.margin_level,
            'profit': account.profit,
            'currency': account.currency,
            'leverage': account.leverage
        }

    def calculate_lot_size(self, symbol: str, risk_amount: float,
                          stop_loss_pips: float) -> float:
        """
        Calculate position size based on risk

        Args:
            symbol: Forex pair
            risk_amount: Amount to risk in account currency
            stop_loss_pips: Stop loss in pips

        Returns:
            Lot size
        """
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            return 0.0

        # Get pip value
        pip_value = symbol_info.point * 10 * symbol_info.contract_size

        # Calculate lot size
        lot_size = risk_amount / (stop_loss_pips * pip_value)

        # Round to lot step
        lot_size = round(lot_size / symbol_info.lot_step) * symbol_info.lot_step

        # Ensure within limits
        lot_size = max(symbol_info.min_lot, min(lot_size, symbol_info.max_lot))

        return lot_size

    def get_market_hours(self, symbol: str) -> Dict:
        """Get trading session information"""
        sessions = {
            'sydney': {'open': '22:00', 'close': '07:00'},
            'tokyo': {'open': '00:00', 'close': '09:00'},
            'london': {'open': '08:00', 'close': '17:00'},
            'new_york': {'open': '13:00', 'close': '22:00'}
        }
        return sessions

    def is_market_open(self, symbol: str) -> bool:
        """Check if market is currently open for symbol"""
        # Forex is open 24/5, closed on weekends
        now = datetime.now()
        weekday = now.weekday()

        # Saturday (5) and Sunday (6) are closed
        if weekday == 5:  # Saturday
            return False
        if weekday == 6:  # Sunday before ~22:00 UTC
            return now.hour >= 22

        # Friday after ~22:00 UTC market closes
        if weekday == 4 and now.hour >= 22:
            return False

        return True


class MultiTimeframeAnalyzer:
    """
    Analyzes forex data across multiple timeframes
    Implements higher timeframe confirmation
    """

    def __init__(self, connector: MT5Connector):
        self.connector = connector

    def get_aligned_data(self, symbol: str,
                        primary_tf: Timeframe,
                        higher_tfs: List[Timeframe],
                        bars: int = 1000) -> Dict[str, pd.DataFrame]:
        """
        Get aligned multi-timeframe data
        Ensures all timeframes end at the same time
        """
        all_tfs = [primary_tf] + higher_tfs
        data = self.connector.get_multi_timeframe_data(symbol, all_tfs, bars)

        if not data:
            return {}

        # Align to primary timeframe's last bar
        primary_data = data.get(primary_tf.name)
        if primary_data is None:
            return {}

        last_time = primary_data.index[-1]

        # Filter higher timeframes to align with primary
        for tf_name, df in data.items():
            if tf_name != primary_tf.name:
                data[tf_name] = df[df.index <= last_time]

        return data

    def get_trend_agreement(self, data: Dict[str, pd.DataFrame],
                           lookback: int = 50) -> Dict[str, int]:
        """
        Check trend agreement across timeframes

        Returns:
            Dict with timeframe and trend direction (1=up, -1=down, 0=neutral)
        """
        trends = {}

        for tf_name, df in data.items():
            if len(df) < lookback:
                trends[tf_name] = 0
                continue

            # Simple trend: current price vs moving average
            ma = df['Close'].rolling(lookback).mean()
            current_price = df['Close'].iloc[-1]
            ma_value = ma.iloc[-1]

            if current_price > ma_value * 1.001:  # 0.1% threshold
                trends[tf_name] = 1
            elif current_price < ma_value * 0.999:
                trends[tf_name] = -1
            else:
                trends[tf_name] = 0

        return trends

    def get_support_resistance(self, df: pd.DataFrame,
                              window: int = 50) -> Tuple[List[float], List[float]]:
        """
        Identify support and resistance levels

        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        highs = df['High'].rolling(window).max()
        lows = df['Low'].rolling(window).min()

        # Find local peaks and troughs
        resistance = highs.drop_duplicates().sort_values(ascending=False).head(5).tolist()
        support = lows.drop_duplicates().sort_values(ascending=True).head(5).tolist()

        return support, resistance


if __name__ == "__main__":
    # Example usage
    connector = MT5Connector()

    if connector.connect():
        # Get forex pairs
        pairs = connector.get_forex_pairs()
        print(f"Available pairs: {pairs[:10]}")

        # Get multi-timeframe data
        if pairs:
            symbol = pairs[0]
            timeframes = [Timeframe.M15, Timeframe.H1, Timeframe.H4, Timeframe.D1]
            data = connector.get_multi_timeframe_data(symbol, timeframes, count=500)

            for tf, df in data.items():
                print(f"\n{symbol} {tf}: {len(df)} bars")
                print(df.tail(3))

        connector.disconnect()
