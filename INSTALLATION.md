# Installation Guide - Forex DeepSeeker

## Step-by-Step Installation

### 1. System Requirements

**Operating System:**
- Windows 10/11 (recommended for MT5)
- Linux (Ubuntu 20.04+) with Wine for MT5
- macOS (with Wine for MT5)

**Hardware:**
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 5GB free space

**Software:**
- Python 3.8 or higher
- MetaTrader 5 Terminal
- Git (optional)

### 2. Install MetaTrader 5

**Windows:**
1. Download from: https://www.metatrader5.com/en/download
2. Run installer
3. Complete setup wizard
4. Open a demo account with any broker that supports MT5

**Linux (Ubuntu/Debian):**
```bash
# Install Wine
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine64 wine32

# Download and install MT5
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
wine mt5setup.exe
```

**macOS:**
```bash
# Install Wine via Homebrew
brew install --cask wine-stable

# Download and install MT5
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
wine mt5setup.exe
```

### 3. Install Python Dependencies

**Option A: Using pip (recommended)**
```bash
cd AI_Agents_Forex
pip install -r requirements.txt
```

**Option B: Using conda**
```bash
conda create -n forex-trading python=3.10
conda activate forex-trading
pip install -r requirements.txt
```

### 4. Install TA-Lib

TA-Lib requires special installation:

**Windows:**
1. Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Install: `pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl`

Or use conda:
```bash
conda install -c conda-forge ta-lib
```

**Linux:**
```bash
# Install TA-Lib C library
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Install Python wrapper
pip install TA-Lib
```

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

### 5. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Minimum Configuration:**
```ini
# MT5 Account (get from your MT5 terminal)
MT5_ACCOUNT=12345678
MT5_PASSWORD=YourPassword
MT5_SERVER=BrokerName-Demo

# AI API Key (at least one required)
DEEPSEEK_API_KEY=sk-xxxxx
```

### 6. Verify Installation

Run verification script:
```bash
python -c "import MetaTrader5 as mt5; import talib; import pandas; print('All dependencies OK')"
```

Expected output: `All dependencies OK`

### 7. Test MT5 Connection

```python
python
>>> import MetaTrader5 as mt5
>>> mt5.initialize()
True
>>> mt5.terminal_info()
# Should show terminal information
>>> mt5.shutdown()
```

### 8. Get API Keys

**DeepSeek (Recommended - Most Affordable):**
1. Visit: https://platform.deepseek.com/
2. Sign up for account
3. Navigate to API Keys
4. Create new key
5. Copy to `.env` file

**OpenAI (Optional):**
1. Visit: https://platform.openai.com/
2. Create API key
3. Add to `.env` file

**Anthropic Claude (Optional):**
1. Visit: https://console.anthropic.com/
2. Create API key
3. Add to `.env` file

### 9. Run Quick Test

```bash
# Syntax check
python -m py_compile quick_backtest.py

# Test configuration
python config.py

# Run quick backtest (requires MT5 running)
python quick_backtest.py
```

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'MetaTrader5'"

**Solution:**
```bash
pip install MetaTrader5
```

### Issue: "ImportError: dlopen failed: ta-lib not found"

**Solution (Linux):**
```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

**Solution (macOS):**
```bash
export LIBRARY_PATH=/opt/homebrew/lib:$LIBRARY_PATH
```

### Issue: "MT5 initialization failed"

**Solutions:**
1. Ensure MT5 terminal is running
2. Check that "Algo Trading" button is enabled in MT5
3. Verify MT5 credentials in `.env` file
4. Try without login first: `MT5_ACCOUNT=` (leave empty)

### Issue: "No forex pairs available"

**Solutions:**
1. Open MT5 terminal
2. Go to "View" -> "Symbols"
3. Enable forex pairs you want to trade
4. Restart the script

### Issue: "API key invalid"

**Solutions:**
1. Double-check API key in `.env` file
2. Ensure no extra spaces or quotes
3. Verify key is active on provider's website
4. Try with different provider (e.g., switch from OpenAI to DeepSeek)

## Virtual Environment Setup (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

## Docker Installation (Advanced)

```bash
# Build image
docker build -t forex-deepseeker .

# Run container
docker run -it --rm \
  -v $(pwd):/app \
  -v ~/.wine:/root/.wine \
  -e MT5_ACCOUNT=$MT5_ACCOUNT \
  -e MT5_PASSWORD=$MT5_PASSWORD \
  -e DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY \
  forex-deepseeker python quick_backtest.py
```

## Next Steps

After successful installation:

1. **Review Configuration**: Edit `.env` for your preferences
2. **Run Backtest**: Test the system with historical data
3. **Analyze Results**: Review generated reports
4. **Paper Trade**: Run with `dry_run=True` for 1-2 weeks
5. **Go Live**: Start with small positions

## Support

- GitHub Issues: https://github.com/MauveAndromeda/AI_Agents_Forex/issues
- Documentation: See README.md
- MT5 Help: https://www.mql5.com/en/docs

## Security Reminder

🚨 **NEVER commit `.env` file or share API keys publicly!**

The `.gitignore` file is configured to prevent this, but always double-check before pushing to GitHub.
