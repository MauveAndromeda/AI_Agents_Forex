"""
Quick Backtest Script
Runs a simple backtest with default settings
"""

import sys
from datetime import datetime, timedelta
import logging

from config import Config
from src.data.mt5_connector import MT5Connector, Timeframe
from src.backtest.forex_backtester import ForexBacktester, BacktestConfig
from src.risk.forex_risk_manager import RiskLevel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run quick backtest"""
    print("=" * 60)
    print("FOREX DEEPSEEKER - QUICK BACKTEST")
    print("=" * 60)

    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed")
        return

    # Initialize MT5 connector
    logger.info("Initializing MT5 connection...")
    connector = MT5Connector(
        account=Config.MT5_ACCOUNT if Config.MT5_ACCOUNT else None,
        password=Config.MT5_PASSWORD if Config.MT5_PASSWORD else None,
        server=Config.MT5_SERVER if Config.MT5_SERVER else None
    )

    if not connector.connect():
        logger.error("Failed to connect to MT5")
        logger.info("Note: For historical backtesting, MT5 connection is required")
        logger.info("Make sure MetaTrader 5 is installed and running")
        return

    # Get available forex pairs
    logger.info("Fetching available forex pairs...")
    symbols = connector.get_forex_pairs(
        include_majors=Config.INCLUDE_MAJORS,
        include_minors=Config.INCLUDE_MINORS,
        include_exotics=Config.INCLUDE_EXOTICS
    )

    if not symbols:
        logger.error("No forex pairs available")
        connector.disconnect()
        return

    logger.info(f"Found {len(symbols)} forex pairs")

    # Limit to top 10 for quick backtest
    symbols = symbols[:10]
    logger.info(f"Using symbols: {symbols}")

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

    # Configure backtest (last 3 months for quick test)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

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

    backtest_config = BacktestConfig(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_balance=Config.INITIAL_BALANCE,
        risk_level=risk_level,
        timeframes=timeframes,
        primary_timeframe=timeframe_map[Config.PRIMARY_TIMEFRAME],
        spread_pips=Config.SPREAD_PIPS,
        slippage_pips=Config.SLIPPAGE_PIPS,
        commission_per_lot=Config.COMMISSION_PER_LOT
    )

    # Run backtest
    logger.info("Starting backtest...")
    logger.info(f"Period: {start_date.date()} to {end_date.date()}")
    logger.info(f"Initial balance: ${Config.INITIAL_BALANCE}")
    logger.info(f"Risk level: {Config.RISK_LEVEL}")
    logger.info(f"AI enabled: {Config.USE_AI_AGENTS}")

    backtester = ForexBacktester(
        config=backtest_config,
        mt5_connector=connector,
        use_ai=Config.USE_AI_AGENTS
    )

    try:
        results = backtester.run()

        # Display results
        print("\n" + "=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print(f"Total Return:      {results.total_return:>10.2%}")
        print(f"Sharpe Ratio:      {results.sharpe_ratio:>10.2f}")
        print(f"Sortino Ratio:     {results.sortino_ratio:>10.2f}")
        print(f"Max Drawdown:      {results.max_drawdown:>10.2%}")
        print(f"Win Rate:          {results.win_rate:>10.2%}")
        print(f"Profit Factor:     {results.profit_factor:>10.2f}")
        print(f"Total Trades:      {results.total_trades:>10}")
        print(f"Winning Trades:    {results.winning_trades:>10}")
        print(f"Losing Trades:     {results.losing_trades:>10}")
        print(f"Average Win:       ${results.avg_win:>9.2f}")
        print(f"Average Loss:      ${results.avg_loss:>9.2f}")
        print(f"Largest Win:       ${results.largest_win:>9.2f}")
        print(f"Largest Loss:      ${results.largest_loss:>9.2f}")
        print(f"Final Balance:     ${results.final_balance:>9.2f}")
        print("=" * 60)

        # Save results
        backtester.save_results(results, "backtest_results")
        print(f"\nDetailed results saved to: backtest_results/")

    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)

    finally:
        connector.disconnect()
        logger.info("MT5 connection closed")


if __name__ == "__main__":
    main()
