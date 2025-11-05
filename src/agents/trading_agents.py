"""
Multi-Agent Trading System for Forex
Implements specialized agents for analysis, risk assessment, and execution
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging

from ..ai.unified_llm_client import UnifiedLLMClient, LLMProvider
from ..models.forex_alpha_factors import AlphaSignal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradeDirection(Enum):
    """Trade direction"""
    LONG = 1
    SHORT = -1
    NEUTRAL = 0


@dataclass
class TradingDecision:
    """Agent trading decision"""
    symbol: str
    direction: TradeDirection
    confidence: float  # 0 to 1
    reasoning: str
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timeframe: str = "H1"


class TechnicalAnalystAgent:
    """
    Technical Analysis Agent
    Analyzes price action, patterns, and indicators
    """

    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        self.llm_client = llm_client
        self.name = "Technical Analyst"

    def analyze(self,
               symbol: str,
               data: Dict[str, pd.DataFrame],
               alpha_signals: List[AlphaSignal]) -> TradingDecision:
        """
        Perform technical analysis

        Args:
            symbol: Forex pair
            data: Multi-timeframe data
            alpha_signals: Alpha factor signals

        Returns:
            Trading decision
        """
        # Get primary timeframe data (H1 or first available)
        primary_tf = 'H1' if 'H1' in data else list(data.keys())[0]
        df = data[primary_tf]

        # Aggregate signals by category
        signals_by_category = {}
        for signal in alpha_signals:
            if signal.category not in signals_by_category:
                signals_by_category[signal.category] = []
            signals_by_category[signal.category].append(signal)

        # Calculate category scores
        category_scores = {}
        for category, signals in signals_by_category.items():
            avg_score = np.mean([s.score for s in signals])
            category_scores[category] = avg_score

        # Overall technical score
        overall_score = np.mean(list(category_scores.values()))

        # Prepare data summary for LLM
        current_price = df['Close'].iloc[-1]
        data_summary = self._prepare_data_summary(df, alpha_signals, category_scores)

        # Determine direction
        if overall_score > 0.2:
            direction = TradeDirection.LONG
        elif overall_score < -0.2:
            direction = TradeDirection.SHORT
        else:
            direction = TradeDirection.NEUTRAL

        # Get LLM reasoning if available
        if self.llm_client:
            reasoning = self._get_llm_analysis(symbol, data_summary, direction)
        else:
            reasoning = self._generate_basic_reasoning(category_scores, direction)

        return TradingDecision(
            symbol=symbol,
            direction=direction,
            confidence=min(abs(overall_score), 1.0),
            reasoning=reasoning,
            entry_price=current_price,
            timeframe=primary_tf
        )

    def _prepare_data_summary(self,
                             df: pd.DataFrame,
                             signals: List[AlphaSignal],
                             category_scores: Dict[str, float]) -> str:
        """Prepare concise data summary"""
        close = df['Close'].iloc[-1]
        high_20 = df['High'].iloc[-20:].max()
        low_20 = df['Low'].iloc[-20:].min()

        summary = f"Current Price: {close:.5f}\n"
        summary += f"20-bar Range: {low_20:.5f} - {high_20:.5f}\n\n"

        summary += "Category Scores:\n"
        for category, score in category_scores.items():
            summary += f"  {category}: {score:.2f}\n"

        summary += "\nTop Signals:\n"
        top_signals = sorted(signals, key=lambda x: abs(x.score), reverse=True)[:5]
        for signal in top_signals:
            summary += f"  {signal.name}: {signal.score:.2f} ({signal.category})\n"

        return summary

    def _get_llm_analysis(self, symbol: str, data_summary: str, direction: TradeDirection) -> str:
        """Get LLM-enhanced analysis"""
        prompt = f"""You are a professional forex technical analyst. Analyze the following data for {symbol} and provide a brief trading recommendation.

{data_summary}

Preliminary Direction: {direction.name}

Provide:
1. Key technical observations
2. Strength of the setup (1-10)
3. Potential risks
4. Brief recommendation (2-3 sentences)

Be concise and actionable."""

        try:
            response = self.llm_client.generate(prompt, temperature=0.3, max_tokens=300)
            return response if response else self._generate_basic_reasoning({}, direction)
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._generate_basic_reasoning({}, direction)

    def _generate_basic_reasoning(self, category_scores: Dict, direction: TradeDirection) -> str:
        """Generate basic reasoning without LLM"""
        reasoning = f"Technical Direction: {direction.name}\n"

        if category_scores:
            top_category = max(category_scores.items(), key=lambda x: abs(x[1]))
            reasoning += f"Primary Signal: {top_category[0]} ({top_category[1]:.2f})"

        return reasoning


class RiskManagerAgent:
    """
    Risk Management Agent
    Evaluates risk and sets stop loss / take profit
    """

    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        self.llm_client = llm_client
        self.name = "Risk Manager"

    def evaluate_risk(self,
                     decision: TradingDecision,
                     data: Dict[str, pd.DataFrame],
                     account_info: Dict,
                     current_positions: int) -> TradingDecision:
        """
        Evaluate and adjust trading decision for risk

        Args:
            decision: Initial trading decision
            data: Multi-timeframe data
            account_info: Account balance and equity info
            current_positions: Number of current open positions

        Returns:
            Adjusted trading decision with stop loss and take profit
        """
        if decision.direction == TradeDirection.NEUTRAL:
            return decision

        # Get data for stop loss calculation
        primary_tf = decision.timeframe
        df = data.get(primary_tf, list(data.values())[0])

        # Calculate ATR
        import talib
        atr = talib.ATR(
            df['High'].values,
            df['Low'].values,
            df['Close'].values,
            timeperiod=14
        )[-1]

        # Calculate stop loss
        atr_multiplier = 2.0

        if decision.direction == TradeDirection.LONG:
            stop_loss = decision.entry_price - (atr * atr_multiplier)
            # Find recent support
            support = df['Low'].iloc[-20:].min()
            stop_loss = max(stop_loss, support * 0.999)  # Just below support
        else:  # SHORT
            stop_loss = decision.entry_price + (atr * atr_multiplier)
            # Find recent resistance
            resistance = df['High'].iloc[-20:].max()
            stop_loss = min(stop_loss, resistance * 1.001)  # Just above resistance

        # Calculate take profit (2:1 reward-risk ratio minimum)
        risk = abs(decision.entry_price - stop_loss)
        reward = risk * 2.5  # Aim for 2.5:1

        if decision.direction == TradeDirection.LONG:
            take_profit = decision.entry_price + reward
        else:
            take_profit = decision.entry_price - reward

        # Adjust confidence based on risk factors
        risk_factors = self._assess_risk_factors(
            decision,
            account_info,
            current_positions,
            atr / decision.entry_price
        )

        adjusted_confidence = decision.confidence * risk_factors['multiplier']

        # Get LLM risk assessment if available
        if self.llm_client and adjusted_confidence > 0.3:
            risk_reasoning = self._get_llm_risk_assessment(
                decision,
                risk_factors,
                stop_loss,
                take_profit
            )
            decision.reasoning += f"\n\nRisk Assessment:\n{risk_reasoning}"

        # Update decision
        decision.stop_loss = stop_loss
        decision.take_profit = take_profit
        decision.confidence = min(adjusted_confidence, 1.0)

        return decision

    def _assess_risk_factors(self,
                           decision: TradingDecision,
                           account_info: Dict,
                           current_positions: int,
                           volatility: float) -> Dict:
        """Assess various risk factors"""
        risk_multiplier = 1.0
        factors = []

        # Position count risk
        if current_positions >= 4:
            risk_multiplier *= 0.7
            factors.append("High position count")

        # Volatility risk
        if volatility > 0.015:  # 1.5% daily volatility
            risk_multiplier *= 0.8
            factors.append("High volatility")

        # Account equity risk
        equity = account_info.get('equity', 10000)
        balance = account_info.get('balance', 10000)

        if equity < balance * 0.95:  # In drawdown
            risk_multiplier *= 0.6
            factors.append("Account in drawdown")

        return {
            'multiplier': risk_multiplier,
            'factors': factors
        }

    def _get_llm_risk_assessment(self,
                                decision: TradingDecision,
                                risk_factors: Dict,
                                stop_loss: float,
                                take_profit: float) -> str:
        """Get LLM risk assessment"""
        risk_reward = abs(take_profit - decision.entry_price) / abs(decision.entry_price - stop_loss)

        prompt = f"""As a risk manager, evaluate this forex trade:

Symbol: {decision.symbol}
Direction: {decision.direction.name}
Entry: {decision.entry_price:.5f}
Stop Loss: {stop_loss:.5f}
Take Profit: {take_profit:.5f}
Risk-Reward Ratio: {risk_reward:.2f}:1

Risk Factors: {', '.join(risk_factors['factors']) if risk_factors['factors'] else 'None'}

Provide a brief risk assessment (2-3 sentences) covering:
1. Is the risk-reward acceptable?
2. Are the stop loss and take profit levels reasonable?
3. Any additional precautions?"""

        try:
            response = self.llm_client.generate(prompt, temperature=0.3, max_tokens=200)
            return response if response else "Risk parameters calculated using ATR-based methodology."
        except Exception as e:
            logger.error(f"LLM risk assessment failed: {e}")
            return "Risk parameters calculated using ATR-based methodology."


class SentimentAnalystAgent:
    """
    Market Sentiment Agent
    Analyzes market sentiment and news (placeholder for news integration)
    """

    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        self.llm_client = llm_client
        self.name = "Sentiment Analyst"

    def analyze_sentiment(self,
                         symbol: str,
                         decision: TradingDecision,
                         news: Optional[List[str]] = None) -> float:
        """
        Analyze market sentiment

        Args:
            symbol: Forex pair
            decision: Current trading decision
            news: Optional news headlines

        Returns:
            Sentiment adjustment factor (0.5 to 1.5)
        """
        # Without news API, use basic sentiment from price action
        # In production, this would integrate news feeds

        if not self.llm_client or not news:
            return 1.0  # Neutral

        # Analyze news sentiment
        news_text = "\n".join(news[:5])  # Top 5 headlines

        prompt = f"""Analyze the market sentiment for {symbol} based on these news headlines:

{news_text}

Current technical signal: {decision.direction.name}

Rate the overall sentiment:
- Bullish (1.3-1.5): Strong positive news supporting upward movement
- Slightly Bullish (1.1-1.3): Mild positive news
- Neutral (0.9-1.1): Mixed or no significant news
- Slightly Bearish (0.7-0.9): Mild negative news
- Bearish (0.5-0.7): Strong negative news supporting downward movement

Respond with only a number between 0.5 and 1.5, followed by one sentence explanation."""

        try:
            response = self.llm_client.generate(prompt, temperature=0.3, max_tokens=100)
            # Extract number from response
            sentiment_score = float(response.split()[0])
            return max(0.5, min(1.5, sentiment_score))
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 1.0


class ExecutionAgent:
    """
    Trade Execution Agent
    Makes final decision on whether to execute trade
    """

    def __init__(self, min_confidence: float = 0.4):
        self.name = "Execution Agent"
        self.min_confidence = min_confidence

    def should_execute(self,
                      decision: TradingDecision,
                      account_can_trade: bool,
                      multi_timeframe_agreement: float) -> Tuple[bool, str]:
        """
        Determine if trade should be executed

        Args:
            decision: Trading decision
            account_can_trade: Risk manager approval
            multi_timeframe_agreement: Agreement across timeframes (-1 to 1)

        Returns:
            Tuple of (should_execute, reason)
        """
        if decision.direction == TradeDirection.NEUTRAL:
            return False, "No clear directional bias"

        if not account_can_trade:
            return False, "Risk limits reached"

        if decision.confidence < self.min_confidence:
            return False, f"Confidence too low: {decision.confidence:.2f}"

        if decision.stop_loss is None or decision.take_profit is None:
            return False, "Missing stop loss or take profit"

        # Check multi-timeframe agreement
        if abs(multi_timeframe_agreement) < 0.3:
            return False, "Weak multi-timeframe agreement"

        # Check if stop loss is too tight
        risk_pct = abs(decision.entry_price - decision.stop_loss) / decision.entry_price
        if risk_pct < 0.001:  # Less than 0.1%
            return False, "Stop loss too tight"

        # Check if risk-reward is acceptable
        risk = abs(decision.entry_price - decision.stop_loss)
        reward = abs(decision.take_profit - decision.entry_price)
        risk_reward = reward / risk if risk > 0 else 0

        if risk_reward < 1.5:
            return False, f"Poor risk-reward ratio: {risk_reward:.2f}"

        return True, "All criteria met - execute trade"


class MultiAgentTradingSystem:
    """
    Coordinates multiple agents for trading decisions
    """

    def __init__(self,
                 llm_client: Optional[UnifiedLLMClient] = None,
                 min_confidence: float = 0.4):
        """
        Initialize multi-agent system

        Args:
            llm_client: LLM client for AI enhancement
            min_confidence: Minimum confidence threshold
        """
        self.technical_agent = TechnicalAnalystAgent(llm_client)
        self.risk_agent = RiskManagerAgent(llm_client)
        self.sentiment_agent = SentimentAnalystAgent(llm_client)
        self.execution_agent = ExecutionAgent(min_confidence)

    def analyze_and_decide(self,
                          symbol: str,
                          data: Dict[str, pd.DataFrame],
                          alpha_signals: List[AlphaSignal],
                          account_info: Dict,
                          current_positions: int,
                          account_can_trade: bool,
                          news: Optional[List[str]] = None) -> Optional[TradingDecision]:
        """
        Run multi-agent analysis and make trading decision

        Args:
            symbol: Forex pair
            data: Multi-timeframe data
            alpha_signals: Alpha factor signals
            account_info: Account information
            current_positions: Current open positions
            account_can_trade: Whether account can trade
            news: Optional news headlines

        Returns:
            Trading decision if should execute, None otherwise
        """
        logger.info(f"Multi-agent analysis for {symbol}")

        # Step 1: Technical analysis
        decision = self.technical_agent.analyze(symbol, data, alpha_signals)
        logger.info(f"Technical Agent: {decision.direction.name} (confidence: {decision.confidence:.2f})")

        if decision.direction == TradeDirection.NEUTRAL:
            logger.info("No trade signal - neutral")
            return None

        # Step 2: Risk management
        decision = self.risk_agent.evaluate_risk(
            decision,
            data,
            account_info,
            current_positions
        )
        logger.info(f"Risk Agent: Adjusted confidence to {decision.confidence:.2f}")

        # Step 3: Sentiment analysis
        if news:
            sentiment_factor = self.sentiment_agent.analyze_sentiment(symbol, decision, news)
            decision.confidence *= sentiment_factor
            logger.info(f"Sentiment Agent: Applied factor {sentiment_factor:.2f}")

        # Step 4: Calculate multi-timeframe agreement
        mtf_agreement = self._calculate_mtf_agreement(data, decision.direction)

        # Step 5: Execution decision
        should_execute, reason = self.execution_agent.should_execute(
            decision,
            account_can_trade,
            mtf_agreement
        )

        logger.info(f"Execution Agent: {should_execute} - {reason}")

        if should_execute:
            return decision
        else:
            return None

    def _calculate_mtf_agreement(self,
                                data: Dict[str, pd.DataFrame],
                                direction: TradeDirection) -> float:
        """Calculate agreement across timeframes"""
        if len(data) < 2:
            return 0.5

        import talib

        agreements = []
        for tf_name, df in data.items():
            if len(df) < 50:
                continue

            close = df['Close'].values
            ma_20 = talib.SMA(close, 20)[-1]
            ma_50 = talib.SMA(close, 50)[-1] if len(close) >= 50 else ma_20

            tf_bullish = close[-1] > ma_20 and ma_20 > ma_50
            tf_bearish = close[-1] < ma_20 and ma_20 < ma_50

            if direction == TradeDirection.LONG and tf_bullish:
                agreements.append(1)
            elif direction == TradeDirection.SHORT and tf_bearish:
                agreements.append(1)
            elif direction == TradeDirection.LONG and tf_bearish:
                agreements.append(-1)
            elif direction == TradeDirection.SHORT and tf_bullish:
                agreements.append(-1)
            else:
                agreements.append(0)

        return np.mean(agreements) if agreements else 0.0
