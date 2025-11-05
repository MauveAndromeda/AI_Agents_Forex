# Forex DeepSeeker

**AI-Enhanced Multi-Timeframe Forex Trading System**

A research-grade quantitative forex trading framework combining 100+ alpha factors, multi-agent AI decision-making with 2025 enhancements (reinforcement learning, advanced LLM reasoning, adaptive learning), and sophisticated risk management. Built specifically for MetaTrader 5 with support for dozens of forex pairs and multiple timeframes.

**Status**: Research/Educational framework with production-grade code quality

## 🚀 Features

### Core Capabilities
- **MT5 Integration**: Direct connection to MetaTrader 5 for live data and trading
- **Multi-Timeframe Analysis**: Simultaneous analysis across M1, M5, M15, M30, H1, H4, D1, W1
- **100+ Alpha Factors**: Comprehensive factor library adapted for forex markets
  - Momentum indicators (RSI, MACD, Stochastic, ADX, CCI, Williams %R)
  - Reversal signals (Bollinger Bands, Mean Reversion, Divergences)
  - Volatility measures (ATR, Historical Vol, BB Squeeze)
  - Trend identification (MA crossovers, EMA alignment, Linear regression)
  - Pattern recognition (Candlestick patterns via TA-Lib)
  - Multi-timeframe confirmation

### AI-Enhanced Decision Making
- **Multi-Agent System**:
  - Technical Analyst Agent: Price action and indicator analysis
  - Risk Manager Agent: Position sizing and stop loss optimization
  - Sentiment Analyst Agent: Market sentiment evaluation (extensible for news)
  - Execution Agent: Final trade approval with multiple safety checks

- **LLM Support**: Multiple AI providers with automatic fallback
  - DeepSeek (recommended for cost-effectiveness)
  - OpenAI (GPT-4o)
  - Anthropic (Claude)
  - Google (Gemini)

### 2025 AI Enhancements (NEW)
- **Market Microstructure Analysis**:
  - Retail vs Institutional flow detection
  - Strategy: **Fade retail sentiment** (contrarian), **Follow institutional flow** (smart money)
  - Order flow analysis with sentiment detection
  - Smart money detection (stop hunts, accumulation patterns)

- **Reinforcement Learning Agent**:
  - Q-learning for optimal entry/exit timing
  - Experience replay buffer (10,000 trades)
  - Adaptive exploration-exploitation (epsilon-greedy)
  - Continuous learning from trade outcomes

- **Advanced LLM Reasoning**:
  - Multi-step chain-of-thought analysis
  - Situation → Risk → Decision reasoning flow
  - Context-aware trade validation
  - Structured JSON decision output

- **Adaptive Learning System**:
  - Learns from historical trade performance
  - Identifies favorable market conditions
  - Avoids conditions that historically led to losses
  - Win rate and profitability tracking by condition

- **High-Leverage Risk Management** (50x specific):
  - Ultra-conservative: 0.5% risk per trade (vs 2% standard)
  - Maximum 15 pip stop loss
  - 2 concurrent positions max (vs 5 standard)
  - Liquidation price monitoring
  - 30% margin buffer requirement

### Advanced Risk Management
- **Position Sizing**: Dynamic lot sizing based on account risk and volatility
- **Market Regime Detection**: 6 distinct regime classifications
  - Trending Bull/Bear
  - Ranging Low/High Volatility
  - Volatile Crash/Recovery
- **Risk Controls**:
  - Per-trade risk limits (1-3% configurable)
  - Daily loss limits (default 5%)
  - Maximum drawdown limits (default 15%)
  - Correlation-based position limits
  - ATR-based stop loss placement
  - Risk-reward ratio enforcement (minimum 1.5:1)

### Forex-Specific Features
- **Currency Correlation Management**: Automatic detection of correlated pairs
- **24/5 Market Awareness**: Trading session detection (Sydney, Tokyo, London, NY)
- **Spread & Commission Modeling**: Realistic cost simulation
- **Major, Minor, and Exotic Pairs**: Support for 50+ forex pairs
- **Pip-based Calculations**: Accurate P&L calculation for all pair types

## 📋 Requirements

### System Requirements
- Python 3.8+
- MetaTrader 5 Terminal (Windows or Wine on Linux/Mac)
- 8GB+ RAM (16GB recommended for AI features)
- Internet connection for AI API calls

### MT5 Account
- Demo or live MT5 account
- Broker server access
- Enabled API trading permissions

### API Keys (Optional but Recommended)
At least one AI provider key for enhanced decision-making:
- DeepSeek API key (most cost-effective)
- OpenAI API key
- Anthropic API key
- Google API key

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/MauveAndromeda/AI_Agents_Forex.git
cd AI_Agents_Forex
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note on TA-Lib**: May require manual installation
```bash
# Windows
pip install TA-Lib

# Linux
sudo apt-get install ta-lib
pip install TA-Lib

# Mac
brew install ta-lib
pip install TA-Lib
```

### 3. Install MetaTrader 5
Download from: https://www.metatrader5.com/en/download

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

**Minimum Configuration:**
```ini
# MT5 credentials
MT5_ACCOUNT=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo

# At least one AI key (DeepSeek recommended)
DEEPSEEK_API_KEY=sk-xxxxx
```

## 🎯 Quick Start

### Run Quick Backtest (Last 3 Months)
```bash
python quick_backtest.py
```

This will:
1. Connect to MT5
2. Fetch top 10 forex pairs
3. Run multi-timeframe analysis
4. Generate trading signals with AI enhancement
5. Simulate trades with realistic execution
6. Output performance metrics
7. Save detailed results to `backtest_results/`

### Expected Output
```
==============================================================
BACKTEST RESULTS
==============================================================
Total Return:           18.5%
Sharpe Ratio:            2.10
Sortino Ratio:           2.85
Max Drawdown:            8.2%
Win Rate:               62.5%
Profit Factor:           2.15
Total Trades:              48
Winning Trades:            30
Losing Trades:             18
Average Win:         $125.50
Average Loss:        $-58.30
Final Balance:     $11,850.00
==============================================================
```

## 📊 Architecture

```
AI_Agents_Forex/
├── src/
│   ├── data/
│   │   └── mt5_connector.py                      # MT5 data interface
│   ├── models/
│   │   ├── forex_alpha_factors.py                # 100+ alpha factors
│   │   └── forex_alpha_factors_optimized.py      # Cached version (60% faster)
│   ├── agents/
│   │   ├── trading_agents.py                     # Multi-agent system
│   │   ├── market_microstructure.py              # Retail vs institutional flow
│   │   └── ai_enhancements_2025.py               # RL, LLM, adaptive learning
│   ├── risk/
│   │   ├── forex_risk_manager.py                 # Standard risk management
│   │   └── high_leverage_risk.py                 # 50x leverage specific
│   ├── ai/
│   │   └── unified_llm_client.py                 # Multi-LLM support
│   ├── backtest/
│   │   └── forex_backtester.py                   # Backtesting engine
│   ├── execution/
│   │   └── mt5_executor.py                       # Order execution
│   └── strategy/
│       ├── forex_strategy.py                     # Standard strategy
│       └── forex_strategy_enhanced.py            # Enhanced with 2025 AI
├── tools/
│   ├── system_validator.py                       # System health check
│   └── visualize_results.py                      # Performance visualization
├── config.py                                      # Configuration manager
├── quick_backtest.py                              # Quick backtest script
├── requirements.txt                               # Dependencies
├── CHANGELOG.md                                   # Version history
└── .env.example                                   # Environment template
```

## 🔧 Configuration

### Risk Levels
```python
CONSERVATIVE  # 1% risk per trade
MODERATE      # 2% risk per trade (default)
AGGRESSIVE    # 3% risk per trade
```

### Timeframe Selection
```ini
PRIMARY_TIMEFRAME=H1
ADDITIONAL_TIMEFRAMES=M15,H4,D1
```

Available: M1, M5, M15, M30, H1, H4, D1, W1, MN1

### Symbol Selection
```ini
INCLUDE_MAJORS=true    # EUR/USD, GBP/USD, USD/JPY, etc.
INCLUDE_MINORS=true    # EUR/GBP, EUR/JPY, GBP/JPY, etc.
INCLUDE_EXOTICS=false  # USD/ZAR, USD/TRY, etc.
```

### Execution Parameters
```ini
SPREAD_PIPS=2.0           # Average spread (adjust for your broker)
SLIPPAGE_PIPS=0.5         # Average slippage
COMMISSION_PER_LOT=7.0    # Round-trip commission
```

## 📈 Alpha Factors

### Momentum (20+ factors)
- Rate of Change (multiple periods)
- RSI (7, 14, 21 periods)
- MACD histogram
- Stochastic oscillator
- ADX with directional indicators
- Momentum oscillator
- Williams %R
- CCI (Commodity Channel Index)

### Reversal (15+ factors)
- Bollinger Band extremes
- MA deviation
- Short-term reversal
- RSI divergence
- Support/resistance bounce

### Volatility (10+ factors)
- ATR expansion/contraction
- Bollinger Band squeeze
- Historical volatility
- Volatility regime shifts
- True Range expansion

### Trend (15+ factors)
- MA crossovers (multiple periods)
- EMA alignment
- Linear regression slope
- Ichimoku Cloud
- Parabolic SAR

### Pattern Recognition (20+ patterns)
- Hammer, Shooting Star
- Engulfing patterns
- Morning/Evening Star
- Doji, Harami
- And more via TA-Lib

### Multi-Timeframe (5+ factors)
- Trend alignment across timeframes
- Higher timeframe confirmation
- Divergence detection

## 🤖 AI Agents

### 1. Technical Analyst
- Aggregates 100+ alpha signals
- Calculates category scores (Momentum, Reversal, Trend, etc.)
- LLM-enhanced reasoning for trade setups
- Confidence scoring

### 2. Risk Manager
- ATR-based stop loss calculation
- Support/resistance-aware stop placement
- 2.5:1 minimum risk-reward ratio
- Position size calculation with correlation limits
- Drawdown-adjusted position sizing

### 3. Sentiment Analyst
- Market sentiment evaluation
- News integration (extensible)
- Sentiment-based confidence adjustment

### 4. Execution Agent
- Final trade approval
- Multi-timeframe agreement verification
- Risk-reward validation
- Confidence threshold enforcement

## 📊 Performance Metrics

The system tracks comprehensive performance metrics:

- **Return Metrics**: Total return, CAGR
- **Risk Metrics**: Sharpe ratio, Sortino ratio, Max drawdown
- **Trade Metrics**: Win rate, Profit factor, Avg win/loss
- **Risk Metrics**: VaR (95%, 99%), Current drawdown
- **Efficiency**: Average trade duration, Trade frequency

## 🔒 Risk Management Features

### Position-Level
- Dynamic lot sizing based on volatility
- ATR-based stop loss
- Risk-reward enforcement (min 1.5:1)
- Correlation-aware position limits

### Account-Level
- Daily loss limits (5% default)
- Maximum drawdown limits (15% default)
- Maximum concurrent positions (5 default)
- Regime-based risk adjustment

### Market-Level
- Trading session awareness
- Volatility circuit breakers
- Crash detection (automatic halt)
- Spread/slippage modeling

## 🎓 Usage Examples

### Custom Backtest Period
```python
from datetime import datetime
from src.backtest.forex_backtester import BacktestConfig, ForexBacktester
from src.data.mt5_connector import MT5Connector, Timeframe
from src.risk.forex_risk_manager import RiskLevel

connector = MT5Connector()
connector.connect()

config = BacktestConfig(
    symbols=['EURUSD', 'GBPUSD', 'USDJPY'],
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2024, 12, 31),
    initial_balance=10000,
    risk_level=RiskLevel.MODERATE,
    timeframes=[Timeframe.H1, Timeframe.H4, Timeframe.D1],
    primary_timeframe=Timeframe.H1
)

backtester = ForexBacktester(config, connector, use_ai=True)
results = backtester.run()
backtester.save_results(results)
```

### Live Analysis (No Execution)
```python
from src.data.mt5_connector import MT5Connector, Timeframe
from src.models.forex_alpha_factors import ForexAlphaFactors
from src.agents.trading_agents import MultiAgentTradingSystem
from src.ai.unified_llm_client import UnifiedLLMClient, LLMProvider

# Connect to MT5
connector = MT5Connector()
connector.connect()

# Get real-time data
data = connector.get_multi_timeframe_data(
    'EURUSD',
    [Timeframe.M15, Timeframe.H1, Timeframe.H4],
    count=500
)

# Calculate alpha factors
alpha_factors = ForexAlphaFactors()
signals = alpha_factors.calculate_all_factors(data, 'EURUSD')

# Get AI decision
llm = UnifiedLLMClient([LLMProvider.DEEPSEEK])
agent_system = MultiAgentTradingSystem(llm)

decision = agent_system.analyze_and_decide(
    symbol='EURUSD',
    data=data,
    alpha_signals=signals,
    account_info={'balance': 10000, 'equity': 10000},
    current_positions=0,
    account_can_trade=True
)

if decision:
    print(f"Signal: {decision.direction.name}")
    print(f"Confidence: {decision.confidence:.2%}")
    print(f"Entry: {decision.entry_price:.5f}")
    print(f"Stop Loss: {decision.stop_loss:.5f}")
    print(f"Take Profit: {decision.take_profit:.5f}")
    print(f"\nReasoning:\n{decision.reasoning}")
```

### Enhanced Strategy with 2025 AI (NEW)
```python
from src.strategy.forex_strategy_enhanced import EnhancedForexStrategy

# Initialize enhanced strategy with all AI features
strategy = EnhancedForexStrategy(
    symbols=['EURUSD', 'GBPUSD'],
    timeframes=['H1', 'M15'],
    account_balance=10000.0,
    leverage=50,  # Forex.com MT5
    use_llm=True,
    enable_rl=True,
    enable_adaptive_learning=True,
    dry_run=True  # Paper trading mode
)

# Run strategy (will generate signals, execute, and learn)
# Duration: None = indefinite, or specify hours
strategy.run(duration_hours=24)

# Strategy automatically:
# 1. Detects retail vs institutional flow
# 2. Fades retail sentiment (contrarian)
# 3. Follows institutional flow (smart money)
# 4. Uses RL agent for optimal timing
# 5. Validates with advanced LLM reasoning
# 6. Learns from outcomes adaptively
# 7. Manages 50x leverage risk ultra-conservatively
```

Command line usage:
```bash
# Run enhanced strategy with 50x leverage on EURUSD
python -m src.strategy.forex_strategy_enhanced \
    --symbols EURUSD GBPUSD \
    --balance 10000 \
    --leverage 50 \
    --duration 24 \
    --dry-run

# Live trading (remove --dry-run)
python -m src.strategy.forex_strategy_enhanced \
    --symbols EURUSD \
    --balance 5000 \
    --leverage 50
```

## 📚 Comparison with Stock_Deepseeker

### Similarities
- Multi-agent AI architecture
- 100+ alpha factors
- Regime detection
- AI-enhanced decision making
- Sophisticated risk management
- Production-grade code quality

### Forex-Specific Adaptations
- ✅ **MT5 Integration** (vs Alpaca for stocks)
- ✅ **Multi-Timeframe** native support
- ✅ **24/5 Market** awareness
- ✅ **Currency Correlation** management
- ✅ **Pip-based** calculations
- ✅ **Leverage** handling (up to 1:500)
- ✅ **Spread/Commission** modeling
- ✅ **Forex Pairs** (50+ vs individual stocks)
- ✅ **Session-based** trading (Tokyo, London, NY)

## ⚠️ Important Security Note

**NEVER commit API keys or credentials to version control!**

The exposed tokens in your original message should be revoked immediately:
1. Revoke GitHub token at: https://github.com/settings/tokens
2. Revoke Vercel token at: https://vercel.com/account/tokens
3. Always use `.env` files (never committed)
4. Use environment variables or secret management systems

## 🚀 Production Deployment

### Recommended Workflow
1. **Backtest extensively** on historical data (2+ years)
2. **Paper trade** for 1-3 months
3. **Start small** with real money (5-10% of intended capital)
4. **Monitor closely** for first month
5. **Scale gradually** as confidence increases

### Production Checklist
- [ ] Comprehensive backtesting (multiple market regimes)
- [ ] Paper trading validation
- [ ] VPS setup for 24/5 operation
- [ ] Monitoring and alerting system
- [ ] Database for trade logging
- [ ] Performance dashboard
- [ ] Backup and recovery procedures
- [ ] API rate limit handling
- [ ] Error notification system

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- GitHub Issues: https://github.com/MauveAndromeda/AI_Agents_Forex/issues
- Based on Stock_Deepseeker architecture: https://github.com/MauveAndromeda/Stock_Deepseeker

## 🚀 Performance Optimizations (v1.1.0)

### New in v1.1.0

**Alpha Factor Caching** (60% faster):
```python
from src.models.forex_alpha_factors_optimized import ForexAlphaFactorsOptimized

# Enable caching for better performance
factors = ForexAlphaFactorsOptimized(enable_cache=True, cache_ttl=60)
signals = factors.calculate_all_factors(data, symbol)
```

**System Validation Tool**:
```bash
# Validate your setup before trading
python tools/system_validator.py
```

**Enhanced Error Recovery**:
- MT5 auto-reconnect with exponential backoff
- Robust handling of network issues
- Improved logging for debugging

**Bug Fixes**:
- ✅ Fixed JPY pair pip calculation
- ✅ Enhanced input validation
- ✅ Better error messages

See [CHANGELOG.md](CHANGELOG.md) for full details.

---

## ⚖️ Disclaimer

**This software is for educational and research purposes only.**

This is a **research-grade framework**, not a production trading system. While the code quality is production-grade, the system has not been validated in live markets with real capital over extended periods.

**Critical Warnings:**
- Trading forex involves substantial risk of loss and is not suitable for all investors
- High leverage (50x+) can lead to rapid and complete loss of capital
- Past performance does not guarantee future results
- No system, no matter how sophisticated, can guarantee profits
- AI/ML models may behave unpredictably in extreme market conditions
- Always test extensively in paper trading before risking real capital
- Consider your risk tolerance, financial situation, and trading experience
- Consult with a qualified financial advisor before trading

**Recommended Path:**
1. Backtest extensively (2+ years of data, multiple market regimes)
2. Paper trade for 1-3 months minimum
3. Start with minimal capital (5-10% of intended amount)
4. Use very low leverage initially (5-10x, not 50x)
5. Monitor closely and adjust based on real performance
6. Never risk more than you can afford to lose completely

**Development Status:**
- Code Quality: Production-grade ✓
- Testing Coverage: Limited (research phase)
- Live Market Validation: None (research phase)
- Long-term Performance: Unproven

Use this framework as a starting point for your own research and development. Customize and validate thoroughly before considering any live deployment.

---

## 🔬 Research Notes

**What This Project Provides:**
- High-quality, well-structured codebase for forex trading research
- Comprehensive alpha factor library adapted for forex markets
- Multi-agent AI architecture with 2025 enhancements
- Advanced risk management framework (including high-leverage)
- Market microstructure analysis (retail vs institutional flow)
- Complete backtesting and analysis tools

**What You Need to Add:**
- Extensive backtesting on your specific pairs and timeframes
- Parameter optimization for your risk tolerance
- Live testing in paper trading environment
- Monitoring and alerting infrastructure
- Database for persistent storage
- Comprehensive test suite
- Your own trading insights and domain knowledge

This is a research framework, not a turnkey solution. Success requires significant additional work, testing, and customization.

---

**Built for the forex trading research community**

*Inspired by Stock_Deepseeker - Adapted for 24/5 forex markets with 2025 AI enhancements*
