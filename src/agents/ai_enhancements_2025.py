"""
2025 AI Enhancements for Forex Trading
- Reinforcement Learning agents
- Advanced LLM reasoning
- Multi-agent coordination
- Adaptive learning from trades
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
import json
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TradeExperience:
    """Experience for reinforcement learning"""
    state: Dict[str, float]
    action: int  # 1 buy, 0 hold, -1 sell
    reward: float
    next_state: Dict[str, float]
    done: bool
    metadata: Dict[str, Any]


class ReinforcementLearningAgent:
    """
    RL Agent that learns from trading experience
    Uses Q-learning/DQN approach to optimize entry/exit timing
    """

    def __init__(self,
                 state_dim: int = 50,
                 action_space: int = 3,  # buy, hold, sell
                 learning_rate: float = 0.001,
                 gamma: float = 0.95,
                 epsilon: float = 0.1):
        """
        Initialize RL agent

        Args:
            state_dim: Dimension of state space
            action_space: Number of possible actions
            learning_rate: Learning rate for Q-learning
            gamma: Discount factor
            epsilon: Exploration rate
        """
        self.state_dim = state_dim
        self.action_space = action_space
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon

        # Experience replay buffer
        self.memory = deque(maxlen=10000)

        # Q-table (simplified, in production use neural network)
        self.q_table = {}

        # Performance tracking
        self.episode_rewards = []
        self.learning_curve = []

        logger.info(f"RL Agent initialized: state_dim={state_dim}, "
                   f"action_space={action_space}, epsilon={epsilon}")

    def get_state_key(self, state: Dict[str, float]) -> str:
        """Convert state dict to hashable key"""
        # Discretize continuous values for Q-table
        discretized = {}
        for k, v in state.items():
            discretized[k] = round(v, 2)  # 2 decimal places
        return json.dumps(discretized, sort_keys=True)

    def select_action(self, state: Dict[str, float], training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy

        Returns:
            action: 1 (buy), 0 (hold), -1 (sell)
        """
        state_key = self.get_state_key(state)

        # Exploration vs exploitation
        if training and np.random.random() < self.epsilon:
            # Explore: random action
            action_idx = np.random.randint(0, self.action_space)
        else:
            # Exploit: best known action
            if state_key not in self.q_table:
                # Initialize Q-values
                self.q_table[state_key] = np.zeros(self.action_space)

            action_idx = np.argmax(self.q_table[state_key])

        # Convert action index to trade action
        # 0 -> sell (-1), 1 -> hold (0), 2 -> buy (1)
        action_map = {0: -1, 1: 0, 2: 1}
        return action_map[action_idx]

    def store_experience(self, experience: TradeExperience):
        """Store experience in replay buffer"""
        self.memory.append(experience)

    def learn(self, batch_size: int = 32):
        """
        Learn from experiences using Q-learning

        Q(s,a) <- Q(s,a) + α [r + γ max Q(s',a') - Q(s,a)]
        """
        if len(self.memory) < batch_size:
            return

        # Sample random batch
        batch = np.random.choice(self.memory, size=batch_size, replace=False)

        for exp in batch:
            state_key = self.get_state_key(exp.state)
            next_state_key = self.get_state_key(exp.next_state)

            # Initialize if needed
            if state_key not in self.q_table:
                self.q_table[state_key] = np.zeros(self.action_space)
            if next_state_key not in self.q_table:
                self.q_table[next_state_key] = np.zeros(self.action_space)

            # Convert action back to index
            action_map = {-1: 0, 0: 1, 1: 2}
            action_idx = action_map[exp.action]

            # Q-learning update
            if exp.done:
                target = exp.reward
            else:
                target = exp.reward + self.gamma * np.max(self.q_table[next_state_key])

            # Update Q-value
            self.q_table[state_key][action_idx] += self.learning_rate * (
                target - self.q_table[state_key][action_idx]
            )

        # Decay epsilon (reduce exploration over time)
        self.epsilon = max(0.01, self.epsilon * 0.995)

    def extract_state_features(self,
                              data: Dict[str, pd.DataFrame],
                              alpha_signals: List,
                              order_flow: Any) -> Dict[str, float]:
        """
        Extract state features from market data

        Returns:
            Dictionary of normalized features
        """
        features = {}

        # Get primary timeframe data
        tf_hierarchy = ['H1', 'M30', 'M15']
        df = None
        for tf in tf_hierarchy:
            if tf in data:
                df = data[tf]
                break

        if df is None or len(df) < 50:
            return {}

        close = df['Close'].values

        # Technical indicators (normalized to [-1, 1])
        import talib

        # 1. Trend indicators
        sma_20 = talib.SMA(close, 20)[-1]
        sma_50 = talib.SMA(close, 50)[-1]
        features['trend'] = np.tanh((close[-1] - sma_50) / sma_50 * 100)

        # 2. Momentum
        rsi = talib.RSI(close, 14)[-1]
        features['momentum'] = (rsi - 50) / 50  # [-1, 1]

        # 3. Volatility
        atr = talib.ATR(df['High'].values, df['Low'].values, close, 14)[-1]
        features['volatility'] = np.tanh(atr / close[-1] * 1000)

        # 4. Order flow signals
        if order_flow:
            features['retail_sentiment'] = order_flow.retail_sentiment
            features['institutional_flow'] = order_flow.institutional_sentiment
            features['smart_money'] = order_flow.smart_money_direction

        # 5. Alpha signals composite
        if alpha_signals:
            features['alpha_score'] = np.mean([s.score for s in alpha_signals])

        # 6. Market regime (simplified)
        returns = pd.Series(close).pct_change()
        features['regime_volatility'] = np.tanh(returns.std() * 100)

        # 7. Time features
        hour = pd.Timestamp.now().hour
        features['hour_sin'] = np.sin(2 * np.pi * hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * hour / 24)

        return features

    def save_model(self, filepath: str):
        """Save Q-table to file"""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'epsilon': self.epsilon,
                'episode_rewards': self.episode_rewards
            }, f)
        logger.info(f"RL model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load Q-table from file"""
        import pickle
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.q_table = data['q_table']
                self.epsilon = data['epsilon']
                self.episode_rewards = data['episode_rewards']
            logger.info(f"RL model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")


class AdvancedLLMAgent:
    """
    Advanced LLM reasoning for trading decisions
    2025 enhancement: Chain-of-thought, multi-step reasoning
    """

    def __init__(self, llm_client):
        """
        Initialize advanced LLM agent

        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
        self.conversation_history = []

    def analyze_with_reasoning(self,
                               symbol: str,
                               market_data: Dict,
                               alpha_signals: List,
                               order_flow: Any,
                               news: Optional[List[str]] = None) -> Dict:
        """
        Advanced multi-step reasoning for trading decision

        Uses chain-of-thought prompting for better analysis
        """
        # Prepare context
        context = self._prepare_context(symbol, market_data, alpha_signals, order_flow, news)

        # Step 1: Situation analysis
        situation_prompt = f"""Analyze the current market situation for {symbol}:

{context}

Step 1: What is the current market structure? (trend, range, breakout, etc.)
Step 2: What are the key support/resistance levels?
Step 3: What is the institutional vs retail positioning?

Provide a structured analysis."""

        situation_analysis = self.llm_client.generate(situation_prompt, temperature=0.3, max_tokens=300)

        # Step 2: Risk assessment
        risk_prompt = f"""Based on this situation analysis:
{situation_analysis}

Market data: {context}

Step 1: What are the main risks to a long position?
Step 2: What are the main risks to a short position?
Step 3: What is the risk/reward ratio?

Provide concise risk assessment."""

        risk_assessment = self.llm_client.generate(risk_prompt, temperature=0.3, max_tokens=250)

        # Step 3: Trading decision
        decision_prompt = f"""Make a trading decision for {symbol}:

Situation: {situation_analysis}
Risk Assessment: {risk_assessment}

Based on:
- Fade retail sentiment (retail is usually wrong)
- Follow institutional flow
- Prioritize capital preservation

Decision (respond in JSON format):
{{
  "action": "BUY" or "SELL" or "HOLD",
  "conviction": 0.0 to 1.0,
  "reasoning": "brief explanation",
  "stop_loss_pips": number,
  "take_profit_pips": number
}}"""

        decision_json = self.llm_client.generate(decision_prompt, temperature=0.2, max_tokens=200)

        try:
            decision = json.loads(decision_json)
        except:
            # Fallback if JSON parsing fails
            decision = {
                "action": "HOLD",
                "conviction": 0.0,
                "reasoning": "Failed to parse LLM response",
                "stop_loss_pips": 10,
                "take_profit_pips": 20
            }

        return {
            'situation': situation_analysis,
            'risk': risk_assessment,
            'decision': decision,
            'full_reasoning': f"{situation_analysis}\n\n{risk_assessment}"
        }

    def _prepare_context(self,
                        symbol: str,
                        market_data: Dict,
                        alpha_signals: List,
                        order_flow: Any,
                        news: Optional[List[str]] = None) -> str:
        """Prepare context for LLM"""
        context_parts = []

        # Price action
        if market_data and 'H1' in market_data:
            df = market_data['H1']
            context_parts.append(f"Current price: {df['Close'].iloc[-1]:.5f}")
            context_parts.append(f"24h change: {((df['Close'].iloc[-1] / df['Close'].iloc[-24]) - 1) * 100:.2f}%")

        # Alpha signals summary
        if alpha_signals:
            avg_score = np.mean([s.score for s in alpha_signals])
            context_parts.append(f"Alpha signals: {avg_score:.2f} "
                               f"({'bullish' if avg_score > 0 else 'bearish'})")

        # Order flow
        if order_flow:
            context_parts.append(f"Retail sentiment: {order_flow.retail_sentiment:.2f}")
            context_parts.append(f"Institutional flow: {order_flow.institutional_sentiment:.2f}")
            context_parts.append(f"Smart money: {order_flow.smart_money_direction}")

        # News
        if news:
            context_parts.append(f"Recent news: {' | '.join(news[:3])}")

        return "\n".join(context_parts)


class AdaptiveLearningSystem:
    """
    System that adapts strategy based on performance
    Learns which conditions lead to profitable trades
    """

    def __init__(self):
        """Initialize adaptive learning system"""
        self.performance_by_condition = {}
        self.trade_outcomes = []

    def record_trade_outcome(self,
                            conditions: Dict[str, float],
                            outcome: float,  # P&L
                            metadata: Dict):
        """
        Record trade outcome for learning

        Args:
            conditions: Market conditions at trade entry
            outcome: Trade P&L
            metadata: Additional info (symbol, timeframe, etc.)
        """
        self.trade_outcomes.append({
            'conditions': conditions,
            'outcome': outcome,
            'metadata': metadata,
            'timestamp': pd.Timestamp.now()
        })

        # Update performance stats by condition
        condition_key = self._discretize_conditions(conditions)
        if condition_key not in self.performance_by_condition:
            self.performance_by_condition[condition_key] = {
                'trades': 0,
                'wins': 0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0
            }

        stats = self.performance_by_condition[condition_key]
        stats['trades'] += 1
        stats['wins'] += 1 if outcome > 0 else 0
        stats['total_pnl'] += outcome
        stats['avg_pnl'] = stats['total_pnl'] / stats['trades']

    def should_trade_in_conditions(self, conditions: Dict[str, float]) -> Tuple[bool, float]:
        """
        Determine if we should trade given current conditions

        Returns:
            Tuple of (should_trade, confidence)
        """
        condition_key = self._discretize_conditions(conditions)

        if condition_key not in self.performance_by_condition:
            # No data, default to medium confidence
            return True, 0.5

        stats = self.performance_by_condition[condition_key]

        # Require minimum sample size
        if stats['trades'] < 10:
            return True, 0.5

        # Calculate win rate and profitability
        win_rate = stats['wins'] / stats['trades']
        avg_pnl = stats['avg_pnl']

        # Decision logic
        if win_rate > 0.55 and avg_pnl > 0:
            # Good conditions
            confidence = min(win_rate, 0.9)
            return True, confidence
        elif win_rate < 0.45 or avg_pnl < 0:
            # Bad conditions, avoid
            return False, 0.0
        else:
            # Neutral conditions
            return True, 0.5

    def _discretize_conditions(self, conditions: Dict[str, float]) -> str:
        """Convert continuous conditions to discrete bins"""
        discretized = {}
        for k, v in conditions.items():
            # Round to 1 decimal place for binning
            discretized[k] = round(v, 1)
        return json.dumps(discretized, sort_keys=True)

    def get_learning_insights(self) -> Dict:
        """Get insights from learning"""
        if not self.trade_outcomes:
            return {"message": "No trades recorded yet"}

        total_trades = len(self.trade_outcomes)
        winning_trades = sum(1 for t in self.trade_outcomes if t['outcome'] > 0)
        total_pnl = sum(t['outcome'] for t in self.trade_outcomes)

        # Find best and worst conditions
        best_conditions = max(
            self.performance_by_condition.items(),
            key=lambda x: x[1]['avg_pnl'] if x[1]['trades'] >= 10 else -float('inf'),
            default=(None, None)
        )

        worst_conditions = min(
            self.performance_by_condition.items(),
            key=lambda x: x[1]['avg_pnl'] if x[1]['trades'] >= 10 else float('inf'),
            default=(None, None)
        )

        return {
            'total_trades': total_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'avg_pnl_per_trade': total_pnl / total_trades if total_trades > 0 else 0,
            'best_conditions': best_conditions[0] if best_conditions[0] else "N/A",
            'best_performance': best_conditions[1] if best_conditions[1] else "N/A",
            'worst_conditions': worst_conditions[0] if worst_conditions[0] else "N/A",
            'worst_performance': worst_conditions[1] if worst_conditions[1] else "N/A"
        }
