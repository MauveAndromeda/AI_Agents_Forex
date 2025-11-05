"""
Configuration management for Forex Trading System
Loads settings from environment variables
"""

import os
from typing import List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration"""

    # MT5 Configuration
    MT5_ACCOUNT = int(os.getenv('MT5_ACCOUNT', '0'))
    MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
    MT5_SERVER = os.getenv('MT5_SERVER', '')

    # AI API Keys
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

    # Backtest Configuration
    BACKTEST_START_DATE = datetime.strptime(
        os.getenv('BACKTEST_START_DATE', '2023-01-01'),
        '%Y-%m-%d'
    )
    BACKTEST_END_DATE = datetime.strptime(
        os.getenv('BACKTEST_END_DATE', '2024-12-31'),
        '%Y-%m-%d'
    )
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', '10000'))
    RISK_LEVEL = os.getenv('RISK_LEVEL', 'MODERATE')

    # Trading Configuration
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '5'))
    MAX_CORRELATED_POSITIONS = int(os.getenv('MAX_CORRELATED_POSITIONS', '3'))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '0.05'))
    MAX_DRAWDOWN = float(os.getenv('MAX_DRAWDOWN', '0.15'))

    # Execution Configuration
    SPREAD_PIPS = float(os.getenv('SPREAD_PIPS', '2.0'))
    SLIPPAGE_PIPS = float(os.getenv('SLIPPAGE_PIPS', '0.5'))
    COMMISSION_PER_LOT = float(os.getenv('COMMISSION_PER_LOT', '7.0'))

    # Timeframe Configuration
    PRIMARY_TIMEFRAME = os.getenv('PRIMARY_TIMEFRAME', 'H1')
    ADDITIONAL_TIMEFRAMES = os.getenv('ADDITIONAL_TIMEFRAMES', 'M15,H4,D1').split(',')

    # Symbol Selection
    INCLUDE_MAJORS = os.getenv('INCLUDE_MAJORS', 'true').lower() == 'true'
    INCLUDE_MINORS = os.getenv('INCLUDE_MINORS', 'true').lower() == 'true'
    INCLUDE_EXOTICS = os.getenv('INCLUDE_EXOTICS', 'false').lower() == 'true'

    # AI Configuration
    USE_AI_AGENTS = os.getenv('USE_AI_AGENTS', 'true').lower() == 'true'
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '0.4'))
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.3'))

    @classmethod
    def get_timeframes(cls) -> List[str]:
        """Get all configured timeframes"""
        return [cls.PRIMARY_TIMEFRAME] + cls.ADDITIONAL_TIMEFRAMES

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        errors = []

        # Check MT5 credentials (optional for backtest-only mode)
        if not cls.MT5_ACCOUNT and not cls.MT5_PASSWORD:
            errors.append("Warning: MT5 credentials not set. Live trading disabled.")

        # Check at least one AI key if AI is enabled
        if cls.USE_AI_AGENTS:
            if not any([cls.DEEPSEEK_API_KEY, cls.OPENAI_API_KEY,
                       cls.ANTHROPIC_API_KEY, cls.GOOGLE_API_KEY]):
                errors.append("Warning: No AI API keys set. AI features will be disabled.")

        # Check dates
        if cls.BACKTEST_END_DATE <= cls.BACKTEST_START_DATE:
            errors.append("Error: End date must be after start date")
            return False

        if errors:
            for error in errors:
                print(error)

        return True


if __name__ == "__main__":
    # Test configuration
    if Config.validate():
        print("Configuration validated successfully")
        print(f"Backtest period: {Config.BACKTEST_START_DATE} to {Config.BACKTEST_END_DATE}")
        print(f"Initial balance: ${Config.INITIAL_BALANCE}")
        print(f"Risk level: {Config.RISK_LEVEL}")
        print(f"Timeframes: {Config.get_timeframes()}")
        print(f"AI enabled: {Config.USE_AI_AGENTS}")
