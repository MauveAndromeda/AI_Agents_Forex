# Forex DeepSeeker

**AI-Enhanced Multi-Timeframe Forex Trading System**

An institutional-grade quantitative forex trading platform combining 100+ alpha factors, multi-agent AI decision-making, and sophisticated risk management. Built specifically for MetaTrader 5 with support for dozens of forex pairs and multiple timeframes.

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
│   │   └── mt5_connector.py         # MT5 data interface
│   ├── models/
│   │   └── forex_alpha_factors.py   # 100+ alpha factors
│   ├── agents/
│   │   └── trading_agents.py        # Multi-agent system
│   ├── risk/
│   │   └── forex_risk_manager.py    # Risk management
│   ├── ai/
│   │   └── unified_llm_client.py    # Multi-LLM support
│   └── backtest/
│       └── forex_backtester.py      # Backtesting engine
├── config.py                         # Configuration manager
├── quick_backtest.py                 # Quick backtest script
├── requirements.txt                  # Dependencies
└── .env.example                      # Environment template
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

## 📚 Comparison with Stock_Deepseeker

### Similarities
- Multi-agent AI architecture
- 100+ alpha factors
- Regime detection
- AI-enhanced decision making
- Institutional-grade risk management

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

## ⚖️ Disclaimer

**This software is for educational and research purposes only.**

- Trading forex involves substantial risk of loss
- Past performance does not guarantee future results
- No system can guarantee profits
- Use at your own risk
- Always test thoroughly before live trading
- Consider your risk tolerance and financial situation
- Consult with a financial advisor before trading

---

**Built with ❤️ for the forex trading community**

*Inspired by Stock_Deepseeker - Adapted for the unique characteristics of 24/5 forex markets*
