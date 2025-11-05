"""
Live Trading Strategy Runner
Run the forex strategy in live or demo mode
"""

import sys
import logging
from datetime import datetime

from config import Config
from src.data.mt5_connector import Timeframe
from src.strategy.forex_strategy import ForexStrategy
from src.risk.forex_risk_manager import RiskLevel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'strategy_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    print("=" * 60)
    print("FOREX DEEPSEEKER - LIVE TRADING STRATEGY")
    print("=" * 60)

    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed")
        return

    # Ask for confirmation
    mode = "LIVE TRADING" if not Config.USE_AI_AGENTS else "AI-ENHANCED TRADING"
    print(f"\nMode: {mode}")
    print(f"Symbols: Top 10 forex pairs")
    print(f"Risk Level: {Config.RISK_LEVEL}")
    print(f"Max Positions: {Config.MAX_POSITIONS}")

    response = input("\nThis will start live trading. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted by user")
        return

    # Map timeframe strings to Timeframe enum
    timeframe_map = {
        'M1': Timeframe.M1,
        'M5': Timeframe.M5,
        'M15': Timeframe.M15,
        'M30': Timeframe.M30,
        'H1': Timeframe.H1,
        'H4': Timeframe.H4,
        'D1': Timeframe.D1,
        'W1': Timeframe.W1,
        'MN1': Timeframe.MN1
    }

    timeframes = [timeframe_map[Config.PRIMARY_TIMEFRAME]]
    for tf_str in Config.ADDITIONAL_TIMEFRAMES:
        if tf_str in timeframe_map:
            timeframes.append(timeframe_map[tf_str])

    # Map risk level
    risk_map = {
        'CONSERVATIVE': RiskLevel.CONSERVATIVE,
        'MODERATE': RiskLevel.MODERATE,
        'AGGRESSIVE': RiskLevel.AGGRESSIVE
    }
    risk_level = risk_map.get(Config.RISK_LEVEL, RiskLevel.MODERATE)

    # Initialize strategy
    logger.info("Initializing strategy...")

    # Get forex pairs (will be fetched from MT5)
    # For now, use common pairs
    symbols = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
        'AUDUSD', 'USDCAD', 'NZDUSD', 'EURJPY',
        'GBPJPY', 'EURGBP'
    ]

    strategy = ForexStrategy(
        symbols=symbols,
        timeframes=timeframes,
        initial_balance=Config.INITIAL_BALANCE,
        risk_level=risk_level,
        use_ai=Config.USE_AI_AGENTS,
        dry_run=False  # Set to True for paper trading
    )

    if not strategy.initialize():
        logger.error("Strategy initialization failed")
        return

    try:
        logger.info("Strategy initialized successfully")
        logger.info("Starting continuous trading...")

        # Run continuously with 1 hour interval
        strategy.run_continuous(interval_minutes=60)

    except KeyboardInterrupt:
        logger.info("\nStrategy stopped by user")
    except Exception as e:
        logger.error(f"Strategy error: {e}", exc_info=True)
    finally:
        strategy.shutdown()
        logger.info("Strategy shutdown complete")


if __name__ == "__main__":
    main()
