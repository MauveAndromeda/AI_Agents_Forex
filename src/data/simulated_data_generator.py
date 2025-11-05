"""
Simulated Market Data Generator for Backtesting
Generates realistic forex market data for testing without MT5 connection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimulatedDataGenerator:
    """
    Generate realistic forex market data for backtesting
    Includes trends, reversals, volatility changes, and realistic patterns
    """

    def __init__(self, seed: Optional[int] = 42):
        """
        Initialize simulated data generator

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)

    def generate_forex_data(self,
                           symbol: str,
                           timeframe: str,
                           bars: int,
                           start_date: Optional[datetime] = None,
                           regime: str = 'mixed') -> pd.DataFrame:
        """
        Generate simulated forex data

        Args:
            symbol: Currency pair (e.g., 'EURUSD')
            timeframe: Timeframe (e.g., 'H1', 'M15')
            bars: Number of bars to generate
            start_date: Starting date (default: 3 months ago)
            regime: Market regime ('trending', 'ranging', 'volatile', 'mixed')

        Returns:
            DataFrame with OHLCV data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=90)

        # Generate timestamps based on timeframe
        timestamps = self._generate_timestamps(start_date, timeframe, bars)

        # Base price for the symbol
        base_prices = {
            'EURUSD': 1.0850,
            'GBPUSD': 1.2650,
            'USDJPY': 148.50,
            'AUDUSD': 0.6550,
            'USDCAD': 1.3550,
            'NZDUSD': 0.6050,
            'USDCHF': 0.8750,
            'EURJPY': 161.20,
            'GBPJPY': 187.80,
            'EURGBP': 0.8575,
        }

        base_price = base_prices.get(symbol, 1.0000)

        # Generate price series based on regime
        if regime == 'trending':
            prices = self._generate_trending_prices(base_price, bars)
        elif regime == 'ranging':
            prices = self._generate_ranging_prices(base_price, bars)
        elif regime == 'volatile':
            prices = self._generate_volatile_prices(base_price, bars)
        else:  # mixed
            prices = self._generate_mixed_prices(base_price, bars)

        # Generate OHLCV
        df = self._generate_ohlcv(timestamps, prices, symbol)

        logger.info(f"Generated {bars} bars of {symbol} {timeframe} data ({regime} regime)")

        return df

    def generate_multi_timeframe_data(self,
                                     symbol: str,
                                     timeframes: List[str],
                                     bars: int = 500,
                                     regime: str = 'mixed') -> Dict[str, pd.DataFrame]:
        """
        Generate data for multiple timeframes

        Args:
            symbol: Currency pair
            timeframes: List of timeframes
            bars: Number of bars per timeframe
            regime: Market regime

        Returns:
            Dictionary of {timeframe: DataFrame}
        """
        data = {}
        for tf in timeframes:
            data[tf] = self.generate_forex_data(symbol, tf, bars, regime=regime)

        return data

    def _generate_timestamps(self,
                           start_date: datetime,
                           timeframe: str,
                           bars: int) -> pd.DatetimeIndex:
        """Generate timestamps for given timeframe"""
        # Map timeframes to minutes
        tf_minutes = {
            'M1': 1,
            'M5': 5,
            'M15': 15,
            'M30': 30,
            'H1': 60,
            'H4': 240,
            'D1': 1440,
            'W1': 10080,
            'MN1': 43200
        }

        minutes = tf_minutes.get(timeframe, 60)
        timestamps = pd.date_range(
            start=start_date,
            periods=bars,
            freq=f'{minutes}min'
        )

        return timestamps

    def _generate_trending_prices(self, base_price: float, bars: int) -> np.ndarray:
        """Generate trending price series"""
        # Strong trend with some pullbacks
        trend = np.linspace(0, 0.02, bars)  # 2% overall trend
        noise = np.random.randn(bars) * 0.001  # Small noise

        # Add occasional pullbacks
        pullbacks = np.zeros(bars)
        for i in range(bars // 50):
            start = np.random.randint(0, bars - 20)
            pullbacks[start:start+10] = -0.003

        returns = trend + noise + pullbacks
        prices = base_price * (1 + np.cumsum(returns))

        return prices

    def _generate_ranging_prices(self, base_price: float, bars: int) -> np.ndarray:
        """Generate ranging (sideways) price series"""
        # Mean reversion around base price
        prices = np.zeros(bars)
        prices[0] = base_price

        mean_reversion_speed = 0.1
        volatility = 0.0005

        for i in range(1, bars):
            # Mean reversion
            deviation = (prices[i-1] - base_price) / base_price
            drift = -mean_reversion_speed * deviation

            # Random walk
            shock = np.random.randn() * volatility

            prices[i] = prices[i-1] * (1 + drift + shock)

        return prices

    def _generate_volatile_prices(self, base_price: float, bars: int) -> np.ndarray:
        """Generate volatile price series with large swings"""
        # High volatility with momentum
        volatility = 0.002  # 2x normal volatility
        momentum = 0.3

        returns = np.zeros(bars)
        returns[0] = np.random.randn() * volatility

        for i in range(1, bars):
            # Momentum effect
            prev_return = returns[i-1]
            drift = momentum * prev_return

            # Random shock
            shock = np.random.randn() * volatility

            returns[i] = drift + shock

        prices = base_price * (1 + np.cumsum(returns))

        return prices

    def _generate_mixed_prices(self, base_price: float, bars: int) -> np.ndarray:
        """Generate mixed regime price series"""
        # Combine different regimes
        prices = np.zeros(bars)
        prices[0] = base_price

        # Divide into segments
        segment_size = bars // 4

        # Segment 1: Trending up
        seg1 = self._generate_trending_prices(base_price, segment_size)

        # Segment 2: Ranging
        seg2 = self._generate_ranging_prices(seg1[-1], segment_size)

        # Segment 3: Volatile crash
        seg3 = self._generate_volatile_prices(seg2[-1], segment_size)

        # Segment 4: Recovery trend
        seg4 = self._generate_trending_prices(seg3[-1] * 0.98, bars - 3 * segment_size)

        prices = np.concatenate([seg1, seg2, seg3, seg4])[:bars]

        return prices

    def _generate_ohlcv(self,
                       timestamps: pd.DatetimeIndex,
                       close_prices: np.ndarray,
                       symbol: str) -> pd.DataFrame:
        """Generate OHLC from close prices"""
        bars = len(close_prices)

        # Generate realistic OHLC based on close
        # Typical intrabar range: 0.02% - 0.1% of price
        pip_size = 0.01 if 'JPY' in symbol else 0.0001

        high_offset = np.random.uniform(0, 5, bars) * pip_size
        low_offset = np.random.uniform(0, 5, bars) * pip_size

        # Open is close of previous bar (with small gap)
        open_prices = np.roll(close_prices, 1)
        open_prices[0] = close_prices[0] * (1 - 0.0001)

        # High is max of open/close + offset
        high_prices = np.maximum(open_prices, close_prices) + high_offset

        # Low is min of open/close - offset
        low_prices = np.minimum(open_prices, close_prices) - low_offset

        # Volume (realistic distribution)
        base_volume = 1000
        volume = np.random.lognormal(np.log(base_volume), 0.5, bars).astype(int)

        # Tick volume (for MT5)
        tick_volume = np.random.randint(50, 500, bars)

        # Spread (realistic for symbol)
        if 'JPY' in symbol:
            spread = 2  # 2 pips for JPY pairs
        else:
            spread = 1  # 1 pip for major pairs

        df = pd.DataFrame({
            'Time': timestamps,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volume,
            'TickVolume': tick_volume,
            'Spread': spread
        })

        df.set_index('Time', inplace=True)

        return df

    def add_realistic_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add realistic trading patterns to data
        (Stop hunts, fake breakouts, etc.)
        """
        df = df.copy()

        # Add occasional stop hunts (wicks that reverse quickly)
        hunt_indices = np.random.choice(len(df), size=len(df) // 50, replace=False)

        for idx in hunt_indices:
            if idx > 0 and idx < len(df) - 1:
                # Create a wick that hunts stops
                if np.random.rand() > 0.5:
                    # Hunt long stops (lower low then reverse)
                    df.iloc[idx]['Low'] = df.iloc[idx]['Low'] * 0.9998
                else:
                    # Hunt short stops (higher high then reverse)
                    df.iloc[idx]['High'] = df.iloc[idx]['High'] * 1.0002

        return df


class SimulatedMT5Connector:
    """
    Simulated MT5 connector for backtesting without real MT5
    Mimics the interface of MT5Connector but uses simulated data
    """

    def __init__(self, seed: Optional[int] = 42):
        """Initialize simulated connector"""
        self.generator = SimulatedDataGenerator(seed=seed)
        self.is_connected = False
        self.symbols = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD',
            'NZDUSD', 'USDCHF', 'EURJPY', 'GBPJPY', 'EURGBP'
        ]

    def connect(self) -> bool:
        """Simulate connection"""
        logger.info("Simulated MT5 connection established")
        self.is_connected = True
        return True

    def disconnect(self):
        """Simulate disconnection"""
        logger.info("Simulated MT5 connection closed")
        self.is_connected = False

    def get_data(self,
                symbol: str,
                timeframe: str,
                bars: int = 500,
                start_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get simulated data"""
        if not self.is_connected:
            self.connect()

        return self.generator.generate_forex_data(
            symbol=symbol,
            timeframe=timeframe,
            bars=bars,
            start_date=start_date,
            regime='mixed'
        )

    def get_multi_timeframe_data(self,
                                symbol: str,
                                timeframes: List[str],
                                count: int = 500) -> Dict[str, pd.DataFrame]:
        """Get simulated multi-timeframe data"""
        if not self.is_connected:
            self.connect()

        return self.generator.generate_multi_timeframe_data(
            symbol=symbol,
            timeframes=timeframes,
            bars=count,
            regime='mixed'
        )

    def get_current_price(self, symbol: str) -> float:
        """Get simulated current price"""
        # Get latest price from recent data
        df = self.get_data(symbol, 'M1', bars=1)
        return float(df['Close'].iloc[-1])

    def get_symbols(self) -> List[str]:
        """Get available symbols"""
        return self.symbols
