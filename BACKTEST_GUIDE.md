# One-Click Backtest Guide for vast.ai

## Quick Start

### 1. In vast.ai PyTorch Jupyter Terminal

```bash
# Navigate to project directory
cd /workspace/AI_Agents_Forex  # or wherever you cloned the repo

# Run backtest with GPT-5-nano (default, fastest, cheapest)
python run_backtest.py

# Or explicitly specify
python run_backtest.py --llm gpt-5-nano

# Or with Claude Sonnet 4.5 (highest quality)
python run_backtest.py --llm claude-sonnet-4.5

# Or with GPT-4o (balanced)
python run_backtest.py --llm gpt-4o
```

### 2. Set API Keys (Required for LLM features)

```bash
# In Jupyter terminal, set your API key
export OPENAI_API_KEY='sk-your-key-here'
# or
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

Or create a `.env` file:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

## Command Options

### Basic Usage

```bash
# Default: GPT-4o-mini, EURUSD+GBPUSD, 90 days, $10k balance
python run_backtest.py
```

### Custom Options

```bash
# Choose different LLM
python run_backtest.py --llm claude-sonnet-4.5

# Test more symbols
python run_backtest.py --symbols EURUSD GBPUSD USDJPY AUDUSD

# Longer duration
python run_backtest.py --duration 180

# Different starting balance
python run_backtest.py --balance 50000

# Different leverage
python run_backtest.py --leverage 100
```

### All Options Combined

```bash
python run_backtest.py \
    --llm gpt-4o \
    --symbols EURUSD GBPUSD USDJPY \
    --balance 25000 \
    --leverage 50 \
    --duration 120
```

## Available LLM Models

| Model | Provider | Speed | Cost | Quality | Notes |
|-------|----------|-------|------|---------|-------|
| `gpt-5-nano` | OpenAI | Very Fast | Very Low | Good | ⭐ **Default** |
| `gpt-4o-mini` | OpenAI | Fast | Low | Good | |
| `gpt-4o` | OpenAI | Medium | Medium | Excellent | |
| `claude-sonnet-4.5` | Anthropic | Medium | Medium | Excellent | |
| `claude-3.5-sonnet` | Anthropic | Medium | Medium | Very Good | |
| `deepseek` | DeepSeek | Fast | Very Low | Good | |
| `gemini` | Google | Fast | Low | Good | |

**Recommendation**: Default `gpt-5-nano` is perfect for quick tests. Use `claude-sonnet-4.5` or `gpt-4o` for final validation.

## What Gets Tested

The backtest comprehensively tests **ALL AI AGENTS** - both original and 2025 enhancements:

### Original Multi-Agent System (4 Agents) ✓

1. **TechnicalAnalystAgent** ✓
   - Analyzes 100+ alpha factors
   - Aggregates signals by category (Momentum, Reversal, Trend, etc.)
   - Calculates overall technical score
   - Uses LLM for enhanced reasoning

2. **RiskManagerAgent** ✓
   - ATR-based stop loss calculation
   - Support/resistance-aware stop placement
   - Position size validation
   - Risk-reward ratio enforcement (min 1.5:1)
   - Drawdown-adjusted sizing

3. **SentimentAnalystAgent** ✓
   - Market sentiment evaluation
   - News integration (when available)
   - Sentiment-based confidence adjustment

4. **ExecutionAgent** ✓
   - Final trade approval
   - Multi-timeframe agreement verification
   - Risk-reward validation
   - Confidence threshold enforcement

### 2025 AI Enhancements (4 New Components) ✓

1. **Market Microstructure Analysis** ✓
- Retail vs institutional flow detection
- **Fade retail sentiment** (contrarian strategy)
- **Follow institutional flow** (smart money)
- Stop hunt detection
- Volume imbalance analysis

### 2. Reinforcement Learning Agent ✓
- Q-learning for optimal timing
- Experience replay buffer
- Adaptive exploration-exploitation
- Continuous learning from outcomes

### 3. Advanced LLM Reasoning ✓
- Multi-step chain-of-thought analysis
- Three-stage reasoning: Situation → Risk → Decision
- Context-aware validation
- Structured decision output

### 4. Adaptive Learning System ✓
- Learns from trade performance
- Win rate tracking by market conditions
- Condition-based trade filtering
- Best/worst condition identification

### 5. High-Leverage Risk Management ✓
- Ultra-conservative for 50x leverage
- 0.5% risk per trade
- Maximum 15 pip stop loss
- 2 concurrent positions max
- Liquidation price monitoring
- 30% margin buffer

### 6. Alpha Factors (100+) ✓
- Momentum indicators
- Reversal signals
- Volatility measures
- Trend identification
- Pattern recognition
- Multi-timeframe confirmation

## Output

### Console Output
The script prints:
- Initialization status for all components
- Trade-by-trade execution log
- Comprehensive results table
- AI component analysis
- Adaptive learning insights

### Results File
Saved to `backtest_results/enhanced_backtest_YYYYMMDD_HHMMSS.json`

Contains:
- All performance metrics
- Individual trade details
- AI component scores
- Adaptive learning data

## Example Output

```
================================================================================
ENHANCED FOREX BACKTEST - 2025 AI ENHANCEMENTS
================================================================================
Symbols: EURUSD, GBPUSD
Initial Balance: $10,000.00
Leverage: 50x
LLM Provider: gpt-5-nano
Duration: 90 days
Data Source: Simulated
================================================================================

✓ Simulated data generator initialized
✓ Alpha factors initialized (100+ factors, cached)
✓ LLM client initialized (gpt-5-nano)
✓ Multi-Agent System initialized (4 agents: Technical, Risk, Sentiment, Execution)
✓ Market microstructure analyzer initialized (retail vs institutional)
✓ RL agent initialized (Q-learning)
✓ Advanced LLM agent initialized (chain-of-thought reasoning)
✓ Adaptive learning system initialized
✓ High-leverage risk manager initialized (50x specific)

All systems initialized. Starting backtest...

SYSTEM ARCHITECTURE:
- Original Multi-Agent System (4 agents) -> Base trading decision
- 2025 AI Enhancements (4 components) -> Enhance and validate decision
- Total: 8 AI components working together

============================================================
TESTING SYMBOL: EURUSD
============================================================

Loading historical data for EURUSD...
✓ Loaded 500 H1 bars
  Trade: BUY EURUSD @ 1.08523 | Result: WIN | P&L: +$45.20 | Equity: $10,045.20
  Trade: SELL EURUSD @ 1.08456 | Result: LOSS | P&L: -$22.50 | Equity: $10,022.70
  ...

================================================================================
BACKTEST RESULTS - 2025 AI ENHANCEMENTS
================================================================================
Initial Balance:        $   10,000.00
Final Equity:           $   11,850.00
Total P&L:              $    1,850.00
Total Return:                  18.50%
--------------------------------------------------------------------------------
Total Trades:                      48
Winning Trades:                    30
Losing Trades:                     18
Win Rate:                       62.5%
--------------------------------------------------------------------------------
Average Win:            $      125.50
Average Loss:           $      -58.30
Profit Factor:                   2.15
Sharpe Ratio:                    2.10
Max Drawdown:                    8.2%
--------------------------------------------------------------------------------
AI COMPONENT ANALYSIS:
Avg Alpha Score:                0.156
Avg Retail Sentiment:          -0.045 (FADED)
Avg Institutional Flow:         0.234 (FOLLOWED)
================================================================================

ADAPTIVE LEARNING INSIGHTS:
--------------------------------------------------------------------------------
total_trades: 48
avg_win_rate: 0.625
best_conditions: {'alpha_score': 0.2, 'institutional_flow': 0.4}
worst_conditions: {'alpha_score': -0.1, 'retail_sentiment': 0.6}
--------------------------------------------------------------------------------

✅ Backtest completed successfully!
📊 Results saved to: backtest_results/
💰 Final P&L: $1,850.00 (18.50%)
```

## Tips for vast.ai

### 1. Install Dependencies First
```bash
pip install -r requirements.txt
```

### 2. Check GPU (Optional, not required for backtest)
```bash
nvidia-smi
```

### 3. Run in Background (for long tests)
```bash
nohup python run_backtest.py --duration 180 > backtest.log 2>&1 &
```

### 4. Monitor Progress
```bash
tail -f backtest.log
```

### 5. Download Results
After backtest completes, download the results file:
```bash
# In Jupyter, navigate to backtest_results/ folder
# Download the JSON file for detailed analysis
```

## Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Make sure you're in the project root directory
```bash
cd /workspace/AI_Agents_Forex
python run_backtest.py
```

### Issue: "API key not found"
**Solution**: Set your API key
```bash
export OPENAI_API_KEY='your-key-here'
```
Or the script will run without LLM features (reduced functionality)

### Issue: "ImportError: ta-lib"
**Solution**: Install TA-Lib
```bash
# On vast.ai Ubuntu
sudo apt-get update
sudo apt-get install -y ta-lib
pip install TA-Lib
```

### Issue: Backtest too slow
**Solution**:
- Use fewer symbols: `--symbols EURUSD`
- Shorter duration: `--duration 30`
- Already using fastest: `--llm gpt-5-nano` (default)

## Performance Expectations

| Duration | Symbols | Expected Time |
|----------|---------|---------------|
| 30 days  | 1       | 1-2 minutes   |
| 90 days  | 2       | 3-5 minutes   |
| 180 days | 3       | 8-12 minutes  |

*Times vary based on LLM API response speed*

## Next Steps After Backtest

1. **Analyze Results**: Review the JSON file for detailed trade data
2. **Adjust Parameters**: Modify risk settings, test different conditions
3. **Compare LLMs**: Test different LLM models to see which performs best
4. **Longer Tests**: Run with `--duration 365` for full year backtest
5. **Paper Trading**: Move to paper trading with `forex_strategy_enhanced.py --dry-run`

## Support

If you encounter issues:
1. Check the log output for specific error messages
2. Verify API keys are set correctly
3. Ensure all dependencies are installed
4. Check `backtest.log` if running in background

---

**Ready to backtest? Just run:**
```bash
python run_backtest.py
```
*(Uses gpt-5-nano by default - no need to specify!)*

🚀 Happy backtesting!
