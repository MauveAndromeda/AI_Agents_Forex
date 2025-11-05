"""
Market Microstructure Analysis
Detects retail vs institutional order flow and positioning
Strategy: Fade retail sentiment, follow institutional smart money
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParticipantType(Enum):
    """Market participant classification"""
    RETAIL = "retail"
    INSTITUTIONAL = "institutional"
    SMART_MONEY = "smart_money"
    UNKNOWN = "unknown"


@dataclass
class OrderFlowSignal:
    """Order flow analysis signal"""
    symbol: str
    retail_sentiment: float  # -1 (bearish) to 1 (bullish)
    institutional_sentiment: float
    smart_money_direction: int  # 1 (long), -1 (short), 0 (neutral)
    conviction: float  # 0 to 1
    reasoning: str
    timestamp: pd.Timestamp


class MarketMicrostructureAnalyzer:
    """
    Analyzes market microstructure to detect retail vs institutional flow

    Key Insights:
    - Retail traders are typically on the wrong side
    - Institutional flow leads price movement
    - Extreme retail sentiment is a contrarian indicator
    """

    def __init__(self, fade_retail: bool = True, follow_institutions: bool = True):
        """
        Initialize microstructure analyzer

        Args:
            fade_retail: Trade against retail sentiment
            follow_institutions: Trade with institutional flow
        """
        self.fade_retail = fade_retail
        self.follow_institutions = follow_institutions
        self.retail_indicators = []
        self.institutional_indicators = []

    def analyze_order_flow(self,
                          data: Dict[str, pd.DataFrame],
                          volume_profile: Optional[pd.DataFrame] = None) -> OrderFlowSignal:
        """
        Analyze order flow to detect participant behavior

        Args:
            data: Multi-timeframe OHLCV data
            volume_profile: Optional volume profile data

        Returns:
            OrderFlowSignal with participant analysis
        """
        # Get highest timeframe for analysis
        tf_hierarchy = ['D1', 'H4', 'H1', 'M30', 'M15']
        df = None
        symbol = "UNKNOWN"

        for tf in tf_hierarchy:
            if tf in data:
                df = data[tf]
                break

        if df is None or len(df) < 100:
            return self._neutral_signal(symbol)

        # Extract retail sentiment indicators
        retail_sentiment = self._detect_retail_sentiment(df)

        # Extract institutional flow
        institutional_sentiment = self._detect_institutional_flow(df)

        # Detect smart money positioning
        smart_money_direction = self._detect_smart_money(df)

        # Calculate conviction based on divergence
        conviction = self._calculate_conviction(retail_sentiment, institutional_sentiment)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            retail_sentiment,
            institutional_sentiment,
            smart_money_direction,
            conviction
        )

        return OrderFlowSignal(
            symbol=symbol,
            retail_sentiment=retail_sentiment,
            institutional_sentiment=institutional_sentiment,
            smart_money_direction=smart_money_direction,
            conviction=conviction,
            reasoning=reasoning,
            timestamp=pd.Timestamp.now()
        )

    def _detect_retail_sentiment(self, df: pd.DataFrame) -> float:
        """
        Detect retail trader sentiment using heuristics

        Retail characteristics:
        - Chase momentum (buy high, sell low)
        - Over-leverage at extremes
        - Poor timing (late entries)
        - Stop losses at obvious levels
        """
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values if 'Volume' in df else np.ones(len(close))

        # 1. Momentum chasing indicator
        # Retail tends to buy after big moves up
        returns = pd.Series(close).pct_change()
        big_moves = returns > returns.std() * 2

        if len(big_moves) > 0:
            recent_big_moves = big_moves.iloc[-10:].sum()
            momentum_chase = np.tanh(recent_big_moves / 3)  # Normalize
        else:
            momentum_chase = 0

        # 2. Breakout trading (retail loves breakouts)
        swing_high = np.max(high[-20:])
        swing_low = np.min(low[-20:])
        current_price = close[-1]

        if current_price > swing_high * 0.999:
            breakout_bias = 1  # Retail likely long
        elif current_price < swing_low * 1.001:
            breakout_bias = -1  # Retail likely short
        else:
            breakout_bias = 0

        # 3. Volume spike at extremes (retail FOMO)
        avg_volume = np.mean(volume[-20:])
        recent_volume = volume[-1]
        volume_spike = (recent_volume / avg_volume) - 1

        if volume_spike > 0.5 and returns.iloc[-1] > 0:
            fomo_indicator = 1  # Retail buying spike
        elif volume_spike > 0.5 and returns.iloc[-1] < 0:
            fomo_indicator = -1  # Retail selling spike
        else:
            fomo_indicator = 0

        # 4. RSI extremes (retail overcommits at extremes)
        import talib
        rsi = talib.RSI(close, timeperiod=14)[-1]

        if rsi > 70:
            rsi_bias = 1  # Retail likely overbought
        elif rsi < 30:
            rsi_bias = -1  # Retail likely oversold
        else:
            rsi_bias = 0

        # Combine indicators
        retail_sentiment = np.mean([
            momentum_chase * 0.3,
            breakout_bias * 0.25,
            fomo_indicator * 0.25,
            rsi_bias * 0.2
        ])

        return np.clip(retail_sentiment, -1, 1)

    def _detect_institutional_flow(self, df: pd.DataFrame) -> float:
        """
        Detect institutional trading patterns

        Institutional characteristics:
        - Trade against extremes (buy dips, sell rallies)
        - Large hidden orders (absorption)
        - Better timing (early entries)
        - Accumulate/distribute gradually
        """
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values if 'Volume' in df else np.ones(len(close))

        # 1. Price rejection at levels (institutional defense)
        # Long wicks = institutional absorption
        upper_wick = (high - np.maximum(close, df['Open'].values)) / (high - low + 1e-10)
        lower_wick = (np.minimum(close, df['Open'].values) - low) / (high - low + 1e-10)

        recent_upper_wicks = np.mean(upper_wick[-5:])
        recent_lower_wicks = np.mean(lower_wick[-5:])

        if recent_lower_wicks > 0.4:  # Strong lower wicks = buying pressure
            wick_signal = 1
        elif recent_upper_wicks > 0.4:  # Strong upper wicks = selling pressure
            wick_signal = -1
        else:
            wick_signal = 0

        # 2. Volume profile analysis (institutional accumulation)
        # Low volume rallies = weak, high volume dips = accumulation
        returns = pd.Series(close).pct_change()
        vol_price_corr = np.corrcoef(returns.iloc[-20:],
                                      pd.Series(volume[-20:]).pct_change().fillna(0))[0, 1]

        if not np.isnan(vol_price_corr):
            # Negative correlation = accumulation on dips (bullish)
            accumulation_signal = -vol_price_corr
        else:
            accumulation_signal = 0

        # 3. Order flow imbalance detection
        # Price movement vs volume (large orders move price less)
        price_efficiency = abs(returns.iloc[-5:].sum()) / (np.mean(volume[-5:]) / np.mean(volume) + 1e-10)

        if price_efficiency < 0.5:  # Price not moving much despite volume = absorption
            if returns.iloc[-1] > 0:
                absorption_signal = 1  # Institutional buying
            else:
                absorption_signal = -1  # Institutional selling
        else:
            absorption_signal = 0

        # 4. Smart money divergence
        # Price makes new low but not confirmed by momentum
        import talib
        macd, signal, hist = talib.MACD(close)

        price_low = close[-1] < np.min(close[-20:-1])
        macd_low = hist[-1] < np.min(hist[-20:-1])

        if price_low and not macd_low:
            divergence_signal = 1  # Bullish divergence
        elif not price_low and macd_low:
            divergence_signal = -1  # Bearish divergence
        else:
            divergence_signal = 0

        # Combine institutional indicators
        institutional_flow = np.mean([
            wick_signal * 0.3,
            accumulation_signal * 0.3,
            absorption_signal * 0.2,
            divergence_signal * 0.2
        ])

        return np.clip(institutional_flow, -1, 1)

    def _detect_smart_money(self, df: pd.DataFrame) -> int:
        """
        Detect smart money positioning using advanced heuristics

        Smart money:
        - Enters before major moves
        - Uses hidden liquidity
        - Creates false breakouts (stop hunts)
        """
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values

        # 1. Stop hunt detection (smart money accumulation)
        swing_low = np.min(low[-20:])
        swing_high = np.max(high[-20:])

        # Price briefly breaks level then reverses = stop hunt
        recent_low = np.min(low[-3:])
        recent_high = np.max(high[-3:])

        if recent_low < swing_low * 0.999 and close[-1] > swing_low * 1.001:
            # Stop hunt low, now reversing up
            return 1
        elif recent_high > swing_high * 1.001 and close[-1] < swing_high * 0.999:
            # Stop hunt high, now reversing down
            return -1

        # 2. Institutional positioning via COT-like analysis
        # (In real implementation, would use actual COT data)
        # Here we use price structure as proxy

        sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]
        sma_200 = pd.Series(close).rolling(200).mean().iloc[-1] if len(close) > 200 else sma_50

        if close[-1] > sma_50 > sma_200:
            return 1  # Strong uptrend
        elif close[-1] < sma_50 < sma_200:
            return -1  # Strong downtrend
        else:
            return 0

    def _calculate_conviction(self, retail: float, institutional: float) -> float:
        """
        Calculate conviction based on divergence between retail and institutions

        High conviction when:
        - Retail and institutions are on opposite sides
        - Extreme retail sentiment (they're usually wrong)
        """
        # Divergence between retail and institutional
        divergence = abs(retail - institutional)

        # Extreme retail sentiment
        retail_extreme = abs(retail)

        # High conviction = large divergence + extreme retail
        conviction = (divergence * 0.6 + retail_extreme * 0.4)

        return np.clip(conviction, 0, 1)

    def _generate_reasoning(self,
                           retail: float,
                           institutional: float,
                           smart_money: int,
                           conviction: float) -> str:
        """Generate human-readable reasoning"""

        reasoning = []

        # Retail sentiment
        if retail > 0.5:
            reasoning.append(f"Strong retail bullish sentiment ({retail:.2f}) - CONTRARIAN BEARISH")
        elif retail < -0.5:
            reasoning.append(f"Strong retail bearish sentiment ({retail:.2f}) - CONTRARIAN BULLISH")
        else:
            reasoning.append(f"Neutral retail sentiment ({retail:.2f})")

        # Institutional flow
        if institutional > 0.3:
            reasoning.append(f"Institutional buying detected ({institutional:.2f})")
        elif institutional < -0.3:
            reasoning.append(f"Institutional selling detected ({institutional:.2f})")

        # Smart money
        if smart_money == 1:
            reasoning.append("Smart money positioned LONG")
        elif smart_money == -1:
            reasoning.append("Smart money positioned SHORT")

        # Conviction
        if conviction > 0.7:
            reasoning.append(f"HIGH CONVICTION ({conviction:.2f})")
        elif conviction > 0.4:
            reasoning.append(f"Medium conviction ({conviction:.2f})")
        else:
            reasoning.append(f"Low conviction ({conviction:.2f})")

        return " | ".join(reasoning)

    def _neutral_signal(self, symbol: str) -> OrderFlowSignal:
        """Return neutral signal when insufficient data"""
        return OrderFlowSignal(
            symbol=symbol,
            retail_sentiment=0.0,
            institutional_sentiment=0.0,
            smart_money_direction=0,
            conviction=0.0,
            reasoning="Insufficient data for order flow analysis",
            timestamp=pd.Timestamp.now()
        )

    def get_trading_signal(self, order_flow: OrderFlowSignal) -> Tuple[int, float]:
        """
        Convert order flow analysis to trading signal

        Strategy:
        - Fade retail when conviction is high
        - Follow institutions
        - Align with smart money

        Returns:
            Tuple of (direction, confidence)
            direction: 1 (long), -1 (short), 0 (neutral)
            confidence: 0 to 1
        """
        signals = []
        weights = []

        # 1. Fade retail (contrarian)
        if self.fade_retail and abs(order_flow.retail_sentiment) > 0.3:
            # Trade opposite of retail
            signals.append(-np.sign(order_flow.retail_sentiment))
            weights.append(order_flow.conviction * 0.4)

        # 2. Follow institutions
        if self.follow_institutions and abs(order_flow.institutional_sentiment) > 0.2:
            signals.append(np.sign(order_flow.institutional_sentiment))
            weights.append(0.35)

        # 3. Align with smart money
        if order_flow.smart_money_direction != 0:
            signals.append(order_flow.smart_money_direction)
            weights.append(0.25)

        if not signals:
            return 0, 0.0

        # Weighted average direction
        total_weight = sum(weights)
        if total_weight == 0:
            return 0, 0.0

        direction_score = sum(s * w for s, w in zip(signals, weights)) / total_weight

        # Determine direction and confidence
        if direction_score > 0.3:
            direction = 1
            confidence = min(abs(direction_score), 1.0)
        elif direction_score < -0.3:
            direction = -1
            confidence = min(abs(direction_score), 1.0)
        else:
            direction = 0
            confidence = 0.0

        return direction, confidence


class SentimentAgent:
    """
    AI Agent that analyzes market sentiment from multiple sources
    2025 Enhancement: Uses advanced NLP and social media analysis
    """

    def __init__(self, llm_client=None):
        """
        Initialize sentiment agent

        Args:
            llm_client: Optional LLM client for enhanced analysis
        """
        self.llm_client = llm_client
        self.microstructure = MarketMicrostructureAnalyzer()

    def analyze_sentiment(self,
                         data: Dict[str, pd.DataFrame],
                         symbol: str,
                         news: Optional[List[str]] = None,
                         social_data: Optional[Dict] = None) -> Dict:
        """
        Comprehensive sentiment analysis

        Returns:
            Dictionary with sentiment metrics and trading recommendation
        """
        # Market microstructure analysis
        order_flow = self.microstructure.analyze_order_flow(data)

        # Get trading signal
        direction, confidence = self.microstructure.get_trading_signal(order_flow)

        # Enhance with LLM if available
        if self.llm_client and news:
            llm_analysis = self._llm_enhanced_analysis(symbol, news, order_flow)
        else:
            llm_analysis = None

        return {
            'order_flow': order_flow,
            'direction': direction,
            'confidence': confidence,
            'llm_analysis': llm_analysis,
            'recommendation': self._generate_recommendation(direction, confidence, order_flow)
        }

    def _llm_enhanced_analysis(self, symbol: str, news: List[str], order_flow: OrderFlowSignal) -> str:
        """Use LLM to enhance sentiment analysis"""
        if not self.llm_client:
            return None

        prompt = f"""Analyze market sentiment for {symbol}:

Order Flow Analysis:
- Retail sentiment: {order_flow.retail_sentiment:.2f}
- Institutional flow: {order_flow.institutional_sentiment:.2f}
- Smart money: {order_flow.smart_money_direction}
- Conviction: {order_flow.conviction:.2f}

Recent News:
{chr(10).join(news[:5])}

Provide:
1. Is retail sentiment a contrarian indicator here?
2. Are institutions accumulating or distributing?
3. What's the likely next move?
4. Risk factors

Keep response under 150 words."""

        try:
            return self.llm_client.generate(prompt, temperature=0.3, max_tokens=200)
        except:
            return None

    def _generate_recommendation(self, direction: int, confidence: float, order_flow: OrderFlowSignal) -> str:
        """Generate actionable trading recommendation"""
        if direction == 0 or confidence < 0.3:
            return "NO TRADE - Insufficient conviction"

        action = "LONG" if direction == 1 else "SHORT"
        strength = "STRONG" if confidence > 0.7 else ("MODERATE" if confidence > 0.5 else "WEAK")

        return f"{strength} {action} - {order_flow.reasoning}"
