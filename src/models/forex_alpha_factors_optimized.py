"""
Optimized Forex Alpha Factors with Caching
Performance improvements for repeated calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import talib
from scipy import stats
from dataclasses import dataclass
import time
import hashlib


@dataclass
class AlphaSignal:
    """Alpha factor signal output"""
    name: str
    value: float
    score: float  # Normalized -1 to 1
    timeframe: str
    category: str


class ForexAlphaFactorsOptimized:
    """
    Optimized alpha factor library with caching and performance improvements
    """

    def __init__(self, enable_cache: bool = True, cache_ttl: int = 60):
        """
        Initialize alpha factors calculator

        Args:
            enable_cache: Enable caching of calculations
            cache_ttl: Cache time-to-live in seconds
        """
        self.factors = {}
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self._cache = {} if enable_cache else None
        self._cache_timestamps = {} if enable_cache else None
        self._indicator_cache = {}  # Cache for computed indicators

    def _get_cache_key(self, symbol: str, data: Dict[str, pd.DataFrame]) -> str:
        """Generate cache key for data"""
        # Use hash of last timestamp from each timeframe
        timestamps = []
        for tf, df in data.items():
            if len(df) > 0:
                timestamps.append(f"{tf}:{df.index[-1]}")
        key_str = f"{symbol}:{'|'.join(timestamps)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def calculate_all_factors(self, data: Dict[str, pd.DataFrame],
                             symbol: str) -> List[AlphaSignal]:
        """
        Calculate all alpha factors with caching

        Args:
            data: Dict of timeframe -> DataFrame
            symbol: Forex pair symbol

        Returns:
            List of alpha signals
        """
        # Check cache
        if self.enable_cache:
            cache_key = self._get_cache_key(symbol, data)
            if cache_key in self._cache:
                cached_time = self._cache_timestamps.get(cache_key, 0)
                if time.time() - cached_time < self.cache_ttl:
                    return self._cache[cache_key]

        signals = []

        # Import original calculate methods
        from .forex_alpha_factors import ForexAlphaFactors
        original = ForexAlphaFactors()

        # Use original implementations
        for tf_name, df in data.items():
            if len(df) < 200:
                continue

            signals.extend(original._momentum_factors(df, tf_name))
            signals.extend(original._reversal_factors(df, tf_name))
            signals.extend(original._volatility_factors(df, tf_name))
            signals.extend(original._trend_factors(df, tf_name))
            signals.extend(original._pattern_factors(df, tf_name))

        if len(data) > 1:
            signals.extend(original._multi_timeframe_factors(data))

        signals.extend(original._correlation_factors(data, symbol))

        # Update cache
        if self.enable_cache:
            self._cache[cache_key] = signals
            self._cache_timestamps[cache_key] = time.time()

            # Clean old cache entries
            self._clean_cache()

        return signals

    def _clean_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if current_time - timestamp > self.cache_ttl * 2  # Keep 2x TTL
        ]
        for key in expired_keys:
            del self._cache[key]
            del self._cache_timestamps[key]

    def clear_cache(self):
        """Clear all cache"""
        if self.enable_cache:
            self._cache.clear()
            self._cache_timestamps.clear()
            self._indicator_cache.clear()
