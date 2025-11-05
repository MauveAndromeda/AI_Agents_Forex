"""
Forex Alpha Factors - 100+ Factors for FX Trading
Adapted for 24/5 forex markets with multi-timeframe analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import talib
from scipy import stats
from dataclasses import dataclass


@dataclass
class AlphaSignal:
    """Alpha factor signal output"""
    name: str
    value: float
    score: float  # Normalized -1 to 1
    timeframe: str
    category: str


class ForexAlphaFactors:
    """
    Comprehensive alpha factor library for forex trading
    Categories: Momentum, Reversal, Volatility, Correlation, Carry, Sentiment
    """

    def __init__(self):
        self.factors = {}

    def calculate_all_factors(self, data: Dict[str, pd.DataFrame],
                             symbol: str) -> List[AlphaSignal]:
        """
        Calculate all alpha factors across multiple timeframes

        Args:
            data: Dict of timeframe -> DataFrame
            symbol: Forex pair symbol

        Returns:
            List of alpha signals
        """
        signals = []

        for tf_name, df in data.items():
            if len(df) < 200:  # Need sufficient data
                continue

            # Momentum factors
            signals.extend(self._momentum_factors(df, tf_name))

            # Reversal factors
            signals.extend(self._reversal_factors(df, tf_name))

            # Volatility factors
            signals.extend(self._volatility_factors(df, tf_name))

            # Trend strength factors
            signals.extend(self._trend_factors(df, tf_name))

            # Pattern recognition
            signals.extend(self._pattern_factors(df, tf_name))

        # Cross-timeframe factors
        if len(data) > 1:
            signals.extend(self._multi_timeframe_factors(data))

        # Correlation factors (requires multiple symbols)
        signals.extend(self._correlation_factors(data, symbol))

        return signals

    def _momentum_factors(self, df: pd.DataFrame, tf: str) -> List[AlphaSignal]:
        """Momentum-based factors"""
        signals = []
        close = df['Close'].values

        # 1. Rate of Change (multiple periods)
        for period in [5, 10, 20, 50]:
            roc = ((close[-1] - close[-period]) / close[-period]) * 100
            score = np.tanh(roc / 2)  # Normalize
            signals.append(AlphaSignal(
                name=f"ROC_{period}",
                value=roc,
                score=score,
                timeframe=tf,
                category="Momentum"
            ))

        # 2. RSI variations
        for period in [7, 14, 21]:
            rsi = talib.RSI(close, timeperiod=period)[-1]
            # Score: overbought negative, oversold positive
            if rsi > 70:
                score = -(rsi - 70) / 30
            elif rsi < 30:
                score = (30 - rsi) / 30
            else:
                score = 0
            signals.append(AlphaSignal(
                name=f"RSI_{period}",
                value=rsi,
                score=score,
                timeframe=tf,
                category="Momentum"
            ))

        # 3. MACD
        macd, signal_line, hist = talib.MACD(close)
        macd_score = np.tanh(hist[-1] / np.std(hist[-20:]) if len(hist) > 20 else 0)
        signals.append(AlphaSignal(
            name="MACD_Histogram",
            value=hist[-1],
            score=macd_score,
            timeframe=tf,
            category="Momentum"
        ))

        # 4. Stochastic
        slowk, slowd = talib.STOCH(df['High'].values, df['Low'].values, close)
        stoch_score = 0
        if slowk[-1] > 80:
            stoch_score = -(slowk[-1] - 80) / 20
        elif slowk[-1] < 20:
            stoch_score = (20 - slowk[-1]) / 20
        signals.append(AlphaSignal(
            name="Stochastic",
            value=slowk[-1],
            score=stoch_score,
            timeframe=tf,
            category="Momentum"
        ))

        # 5. ADX (Trend Strength)
        adx = talib.ADX(df['High'].values, df['Low'].values, close, timeperiod=14)[-1]
        plus_di = talib.PLUS_DI(df['High'].values, df['Low'].values, close)[-1]
        minus_di = talib.MINUS_DI(df['High'].values, df['Low'].values, close)[-1]

        adx_score = 0
        if adx > 25:  # Strong trend
            adx_score = 1 if plus_di > minus_di else -1
        signals.append(AlphaSignal(
            name="ADX_Direction",
            value=adx,
            score=adx_score,
            timeframe=tf,
            category="Momentum"
        ))

        # 6. Momentum Oscillator
        mom = talib.MOM(close, timeperiod=10)
        mom_score = np.tanh(mom[-1] / np.std(mom[-50:]) if len(mom) > 50 else 0)
        signals.append(AlphaSignal(
            name="Momentum_10",
            value=mom[-1],
            score=mom_score,
            timeframe=tf,
            category="Momentum"
        ))

        # 7. Williams %R
        willr = talib.WILLR(df['High'].values, df['Low'].values, close)[-1]
        willr_score = 0
        if willr > -20:
            willr_score = -(willr + 20) / 20
        elif willr < -80:
            willr_score = (-80 - willr) / 20
        signals.append(AlphaSignal(
            name="Williams_R",
            value=willr,
            score=willr_score,
            timeframe=tf,
            category="Momentum"
        ))

        # 8. CCI (Commodity Channel Index)
        cci = talib.CCI(df['High'].values, df['Low'].values, close)[-1]
        cci_score = np.tanh(cci / 200)
        signals.append(AlphaSignal(
            name="CCI",
            value=cci,
            score=cci_score,
            timeframe=tf,
            category="Momentum"
        ))

        return signals

    def _reversal_factors(self, df: pd.DataFrame, tf: str) -> List[AlphaSignal]:
        """Mean reversion factors"""
        signals = []
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values

        # 1. Bollinger Band position
        for period in [20, 50]:
            upper, middle, lower = talib.BBANDS(close, timeperiod=period)
            bb_position = (close[-1] - lower[-1]) / (upper[-1] - lower[-1])
            # Reversal: extreme positions
            if bb_position > 0.9:
                bb_score = -1
            elif bb_position < 0.1:
                bb_score = 1
            else:
                bb_score = 0
            signals.append(AlphaSignal(
                name=f"BB_Reversal_{period}",
                value=bb_position,
                score=bb_score,
                timeframe=tf,
                category="Reversal"
            ))

        # 2. Deviation from moving averages
        for period in [20, 50, 100, 200]:
            if len(close) < period:
                continue
            ma = talib.SMA(close, timeperiod=period)[-1]
            deviation = ((close[-1] - ma) / ma) * 100
            # Reversal signal when too far from MA
            reversal_score = -np.tanh(deviation / 2)
            signals.append(AlphaSignal(
                name=f"MA_Deviation_{period}",
                value=deviation,
                score=reversal_score,
                timeframe=tf,
                category="Reversal"
            ))

        # 3. Short-term overbought/oversold
        returns = pd.Series(close).pct_change()
        short_return = returns.iloc[-5:].sum()
        reversal_score = -np.tanh(short_return * 100)
        signals.append(AlphaSignal(
            name="Short_Term_Reversal",
            value=short_return,
            score=reversal_score,
            timeframe=tf,
            category="Reversal"
        ))

        # 4. RSI divergence
        rsi = talib.RSI(close, timeperiod=14)
        if len(rsi) > 50:
            price_slope = (close[-1] - close[-20]) / close[-20]
            rsi_slope = (rsi[-1] - rsi[-20]) / rsi[-20]

            # Bearish divergence: price up, RSI down
            if price_slope > 0 and rsi_slope < 0:
                divergence_score = -1
            # Bullish divergence: price down, RSI up
            elif price_slope < 0 and rsi_slope > 0:
                divergence_score = 1
            else:
                divergence_score = 0

            signals.append(AlphaSignal(
                name="RSI_Divergence",
                value=rsi_slope,
                score=divergence_score,
                timeframe=tf,
                category="Reversal"
            ))

        # 5. Support/Resistance bounce
        atr = talib.ATR(high, low, close, timeperiod=14)[-1]
        swing_low = np.min(low[-20:])
        swing_high = np.max(high[-20:])

        distance_to_support = (close[-1] - swing_low) / atr
        distance_to_resistance = (swing_high - close[-1]) / atr

        if distance_to_support < 0.5:
            sr_score = 1  # Near support, expect bounce
        elif distance_to_resistance < 0.5:
            sr_score = -1  # Near resistance, expect rejection
        else:
            sr_score = 0

        signals.append(AlphaSignal(
            name="Support_Resistance",
            value=distance_to_support,
            score=sr_score,
            timeframe=tf,
            category="Reversal"
        ))

        return signals

    def _volatility_factors(self, df: pd.DataFrame, tf: str) -> List[AlphaSignal]:
        """Volatility-based factors"""
        signals = []
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values

        # 1. ATR (normalized)
        for period in [14, 20, 50]:
            atr = talib.ATR(high, low, close, timeperiod=period)
            atr_pct = (atr[-1] / close[-1]) * 100
            atr_change = (atr[-1] / atr[-period] - 1) if len(atr) > period else 0

            # High volatility expansion can signal trend continuation
            vol_score = np.tanh(atr_change * 5)
            signals.append(AlphaSignal(
                name=f"ATR_Change_{period}",
                value=atr_pct,
                score=vol_score,
                timeframe=tf,
                category="Volatility"
            ))

        # 2. Bollinger Band width
        upper, middle, lower = talib.BBANDS(close, timeperiod=20)
        bb_width = ((upper[-1] - lower[-1]) / middle[-1]) * 100
        bb_width_ma = np.mean([(upper[i] - lower[i]) / middle[i] for i in range(-50, -1)])

        # Contracting volatility (squeeze) followed by expansion
        width_ratio = bb_width / (bb_width_ma * 100)
        squeeze_score = -1 if width_ratio < 0.5 else (1 if width_ratio > 1.5 else 0)

        signals.append(AlphaSignal(
            name="BB_Squeeze",
            value=bb_width,
            score=squeeze_score,
            timeframe=tf,
            category="Volatility"
        ))

        # 3. Historical volatility
        returns = pd.Series(close).pct_change()
        for window in [10, 20, 50]:
            if len(returns) < window:
                continue
            hist_vol = returns.iloc[-window:].std() * np.sqrt(252)
            vol_rank = stats.percentileofscore(returns.rolling(window).std().dropna(), hist_vol)

            # High volatility can signal both opportunity and risk
            vol_score = (vol_rank - 50) / 50  # -1 to 1
            signals.append(AlphaSignal(
                name=f"Historical_Vol_{window}",
                value=hist_vol,
                score=vol_score,
                timeframe=tf,
                category="Volatility"
            ))

        # 4. Volatility regime
        short_vol = returns.iloc[-10:].std()
        long_vol = returns.iloc[-50:].std()
        vol_regime_score = np.tanh((short_vol - long_vol) / long_vol * 10)

        signals.append(AlphaSignal(
            name="Volatility_Regime",
            value=short_vol / long_vol,
            score=vol_regime_score,
            timeframe=tf,
            category="Volatility"
        ))

        # 5. True Range expansion
        tr = talib.TRANGE(high, low, close)
        tr_expansion = (tr[-1] / np.mean(tr[-20:-1])) - 1
        tr_score = np.tanh(tr_expansion * 2)

        signals.append(AlphaSignal(
            name="True_Range_Expansion",
            value=tr_expansion,
            score=tr_score,
            timeframe=tf,
            category="Volatility"
        ))

        return signals

    def _trend_factors(self, df: pd.DataFrame, tf: str) -> List[AlphaSignal]:
        """Trend identification and strength"""
        signals = []
        close = df['Close'].values

        # 1. Moving average crossovers
        ma_pairs = [(10, 20), (20, 50), (50, 100), (50, 200)]
        for fast, slow in ma_pairs:
            if len(close) < slow:
                continue
            ma_fast = talib.SMA(close, timeperiod=fast)
            ma_slow = talib.SMA(close, timeperiod=slow)

            crossover = (ma_fast[-1] / ma_slow[-1]) - 1
            cross_score = np.tanh(crossover * 100)

            signals.append(AlphaSignal(
                name=f"MA_Cross_{fast}_{slow}",
                value=crossover,
                score=cross_score,
                timeframe=tf,
                category="Trend"
            ))

        # 2. EMA alignment
        ema_periods = [8, 13, 21, 34, 55]
        ema_values = [talib.EMA(close, timeperiod=p)[-1] for p in ema_periods]

        # All EMAs in order = strong trend
        uptrend = all(ema_values[i] > ema_values[i+1] for i in range(len(ema_values)-1))
        downtrend = all(ema_values[i] < ema_values[i+1] for i in range(len(ema_values)-1))

        alignment_score = 1 if uptrend else (-1 if downtrend else 0)
        signals.append(AlphaSignal(
            name="EMA_Alignment",
            value=ema_values[0] / ema_values[-1],
            score=alignment_score,
            timeframe=tf,
            category="Trend"
        ))

        # 3. Linear regression slope
        for window in [20, 50, 100]:
            if len(close) < window:
                continue
            x = np.arange(window)
            y = close[-window:]
            slope, intercept = np.polyfit(x, y, 1)

            # Normalize slope
            slope_pct = (slope * window / close[-1]) * 100
            slope_score = np.tanh(slope_pct)

            signals.append(AlphaSignal(
                name=f"Linear_Regression_{window}",
                value=slope_pct,
                score=slope_score,
                timeframe=tf,
                category="Trend"
            ))

        # 4. Ichimoku Cloud
        tenkan_sen = (talib.MAX(close, 9)[-1] + talib.MIN(close, 9)[-1]) / 2
        kijun_sen = (talib.MAX(close, 26)[-1] + talib.MIN(close, 26)[-1]) / 2

        if close[-1] > max(tenkan_sen, kijun_sen):
            ichimoku_score = 1
        elif close[-1] < min(tenkan_sen, kijun_sen):
            ichimoku_score = -1
        else:
            ichimoku_score = 0

        signals.append(AlphaSignal(
            name="Ichimoku",
            value=(close[-1] - kijun_sen) / close[-1],
            score=ichimoku_score,
            timeframe=tf,
            category="Trend"
        ))

        # 5. Parabolic SAR
        sar = talib.SAR(df['High'].values, df['Low'].values)
        sar_score = 1 if close[-1] > sar[-1] else -1

        signals.append(AlphaSignal(
            name="Parabolic_SAR",
            value=(close[-1] - sar[-1]) / close[-1],
            score=sar_score,
            timeframe=tf,
            category="Trend"
        ))

        return signals

    def _pattern_factors(self, df: pd.DataFrame, tf: str) -> List[AlphaSignal]:
        """Candlestick pattern recognition"""
        signals = []
        open_price = df['Open'].values
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values

        # Major reversal patterns
        patterns = {
            'Hammer': talib.CDLHAMMER(open_price, high, low, close),
            'Shooting_Star': talib.CDLSHOOTINGSTAR(open_price, high, low, close),
            'Engulfing': talib.CDLENGULFING(open_price, high, low, close),
            'Morning_Star': talib.CDLMORNINGSTAR(open_price, high, low, close),
            'Evening_Star': talib.CDLEVENINGSTAR(open_price, high, low, close),
            'Doji': talib.CDLDOJI(open_price, high, low, close),
            'Harami': talib.CDLHARAMI(open_price, high, low, close),
        }

        for pattern_name, pattern_values in patterns.items():
            if pattern_values[-1] != 0:
                score = 1 if pattern_values[-1] > 0 else -1
                signals.append(AlphaSignal(
                    name=f"Pattern_{pattern_name}",
                    value=pattern_values[-1],
                    score=score,
                    timeframe=tf,
                    category="Pattern"
                ))

        return signals

    def _multi_timeframe_factors(self, data: Dict[str, pd.DataFrame]) -> List[AlphaSignal]:
        """Factors based on multiple timeframe analysis"""
        signals = []

        # Get trend direction for each timeframe
        tf_trends = {}
        for tf_name, df in data.items():
            close = df['Close'].values
            if len(close) < 50:
                continue

            ma_50 = talib.SMA(close, timeperiod=50)[-1]
            tf_trends[tf_name] = 1 if close[-1] > ma_50 else -1

        # Trend alignment across timeframes
        if len(tf_trends) > 1:
            all_bullish = all(trend == 1 for trend in tf_trends.values())
            all_bearish = all(trend == -1 for trend in tf_trends.values())

            alignment_score = 1 if all_bullish else (-1 if all_bearish else 0)
            signals.append(AlphaSignal(
                name="Multi_TF_Alignment",
                value=sum(tf_trends.values()) / len(tf_trends),
                score=alignment_score,
                timeframe="Multi",
                category="Multi-TF"
            ))

        # Higher timeframe confirmation
        timeframe_hierarchy = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1']
        available_tfs = sorted([tf for tf in tf_trends.keys() if tf in timeframe_hierarchy],
                              key=lambda x: timeframe_hierarchy.index(x))

        if len(available_tfs) >= 2:
            # Lower TF should follow higher TF
            lower_tf = available_tfs[0]
            higher_tf = available_tfs[-1]

            confirmation_score = 1 if tf_trends[lower_tf] == tf_trends[higher_tf] else 0
            signals.append(AlphaSignal(
                name="HTF_Confirmation",
                value=confirmation_score,
                score=confirmation_score,
                timeframe=f"{lower_tf}_vs_{higher_tf}",
                category="Multi-TF"
            ))

        return signals

    def _correlation_factors(self, data: Dict[str, pd.DataFrame], symbol: str) -> List[AlphaSignal]:
        """Currency correlation and carry trade factors"""
        signals = []

        # This would require multiple symbol data
        # Placeholder for forex-specific factors

        # 1. Carry trade potential (would need interest rate data)
        # 2. Currency strength index
        # 3. Risk-on/risk-off signals

        return signals

    def get_composite_score(self, signals: List[AlphaSignal],
                           weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate weighted composite score

        Args:
            signals: List of alpha signals
            weights: Category weights (default equal)

        Returns:
            Composite score -1 to 1
        """
        if not signals:
            return 0.0

        if weights is None:
            weights = {
                'Momentum': 1.0,
                'Reversal': 0.8,
                'Volatility': 0.6,
                'Trend': 1.2,
                'Pattern': 0.7,
                'Multi-TF': 1.5
            }

        weighted_sum = 0.0
        total_weight = 0.0

        for signal in signals:
            weight = weights.get(signal.category, 1.0)
            weighted_sum += signal.score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0
