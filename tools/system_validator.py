"""
System Validation and Optimization Tool
Checks system health, validates configuration, and suggests optimizations
"""

import sys
import os
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemValidator:
    """Validates and optimizes the trading system"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")

        required = [
            ('pandas', 'pandas'),
            ('numpy', 'numpy'),
            ('MetaTrader5', 'MetaTrader5'),
            ('talib', 'TA-Lib'),
            ('scipy', 'scipy'),
        ]

        optional = [
            ('openai', 'OpenAI'),
            ('anthropic', 'Anthropic Claude'),
            ('google.generativeai', 'Google Gemini'),
            ('matplotlib', 'Matplotlib (for visualization)'),
            ('seaborn', 'Seaborn (for visualization)'),
        ]

        all_ok = True

        for module, name in required:
            try:
                __import__(module)
                logger.info(f"  ✓ {name}")
            except ImportError:
                logger.error(f"  ✗ {name} - REQUIRED")
                self.errors.append(f"Missing required dependency: {name}")
                all_ok = False

        for module, name in optional:
            try:
                __import__(module)
                logger.info(f"  ✓ {name}")
            except ImportError:
                logger.warning(f"  ! {name} - Optional")
                self.warnings.append(f"Missing optional dependency: {name}")

        return all_ok

    def check_configuration(self) -> bool:
        """Validate configuration file"""
        logger.info("\nChecking configuration...")

        try:
            from config import Config

            # Check MT5 credentials
            if not Config.MT5_ACCOUNT:
                self.warnings.append("MT5_ACCOUNT not set - live trading disabled")

            # Check API keys
            has_api_key = any([
                Config.DEEPSEEK_API_KEY,
                Config.OPENAI_API_KEY,
                Config.ANTHROPIC_API_KEY,
                Config.GOOGLE_API_KEY
            ])

            if not has_api_key and Config.USE_AI_AGENTS:
                self.warnings.append("No AI API keys configured - AI features will be limited")
                self.suggestions.append("Get a DeepSeek API key for cost-effective AI enhancement")

            # Check dates
            if Config.BACKTEST_END_DATE <= Config.BACKTEST_START_DATE:
                self.errors.append("Invalid backtest date range")
                return False

            # Check risk parameters
            if Config.MAX_DAILY_LOSS > 0.1:
                self.warnings.append("Daily loss limit > 10% - consider reducing for safety")

            if Config.MAX_DRAWDOWN > 0.25:
                self.warnings.append("Max drawdown > 25% - very aggressive")

            logger.info("  ✓ Configuration valid")
            return True

        except Exception as e:
            logger.error(f"  ✗ Configuration error: {e}")
            self.errors.append(f"Configuration error: {e}")
            return False

    def check_modules(self) -> bool:
        """Check if all modules can be imported"""
        logger.info("\nChecking modules...")

        modules = [
            ('src.data.mt5_connector', 'MT5 Connector'),
            ('src.models.forex_alpha_factors', 'Alpha Factors'),
            ('src.agents.trading_agents', 'Trading Agents'),
            ('src.risk.forex_risk_manager', 'Risk Manager'),
            ('src.ai.unified_llm_client', 'LLM Client'),
            ('src.backtest.forex_backtester', 'Backtester'),
            ('src.execution.mt5_executor', 'Executor'),
            ('src.strategy.forex_strategy', 'Strategy'),
        ]

        all_ok = True
        for module, name in modules:
            try:
                __import__(module)
                logger.info(f"  ✓ {name}")
            except ImportError as e:
                logger.error(f"  ✗ {name}: {e}")
                self.errors.append(f"Module import failed: {name}")
                all_ok = False

        return all_ok

    def check_mt5_connection(self) -> bool:
        """Test MT5 connection"""
        logger.info("\nTesting MT5 connection...")

        try:
            import MetaTrader5 as mt5

            if not mt5.initialize():
                logger.warning("  ! MT5 not initialized - make sure MT5 terminal is running")
                self.warnings.append("MT5 terminal not running or accessible")
                return False

            terminal_info = mt5.terminal_info()
            if terminal_info:
                logger.info(f"  ✓ Connected to {terminal_info.company}")
                logger.info(f"    Version: {terminal_info.version}")
                logger.info(f"    Build: {terminal_info.build}")

            mt5.shutdown()
            return True

        except Exception as e:
            logger.error(f"  ✗ MT5 connection error: {e}")
            self.errors.append(f"MT5 connection error: {e}")
            return False

    def check_performance(self) -> dict:
        """Check system performance metrics"""
        logger.info("\nChecking performance...")

        import psutil

        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        logger.info(f"  CPU Cores: {cpu_count}")
        logger.info(f"  RAM: {memory.total / (1024**3):.1f} GB (Available: {memory.available / (1024**3):.1f} GB)")
        logger.info(f"  Disk: {disk.total / (1024**3):.1f} GB (Free: {disk.free / (1024**3):.1f} GB)")

        # Suggestions
        if cpu_count < 4:
            self.suggestions.append("Consider upgrading to 4+ CPU cores for better performance")

        if memory.total < 8 * 1024**3:
            self.suggestions.append("Consider upgrading to 8GB+ RAM for better performance")

        if disk.free < 5 * 1024**3:
            self.warnings.append("Low disk space - less than 5GB free")

        return {
            'cpu_cores': cpu_count,
            'ram_gb': memory.total / (1024**3),
            'disk_free_gb': disk.free / (1024**3)
        }

    def suggest_optimizations(self):
        """Suggest system optimizations"""
        logger.info("\nOptimization suggestions:")

        suggestions = [
            "1. Enable alpha factor caching for better performance (forex_alpha_factors_optimized.py)",
            "2. Use DeepSeek API for cost-effective AI enhancement ($0.14/million tokens)",
            "3. Run backtests on VPS with 24/7 availability",
            "4. Monitor system with proper logging and alerting",
            "5. Start with paper trading before live deployment",
            "6. Keep position sizes small initially (0.01 lots)",
            "7. Review and adjust risk parameters based on backtest results",
            "8. Use multiple timeframe confirmation for better trade quality",
            "9. Enable MT5 retry logic for stable connectivity",
            "10. Regular backup of backtest results and configurations"
        ]

        for suggestion in suggestions:
            logger.info(f"  💡 {suggestion}")

        self.suggestions.extend(suggestions)

    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("=" * 60)
        report.append("FOREX DEEPSEEKER - SYSTEM VALIDATION REPORT")
        report.append("=" * 60)

        if self.errors:
            report.append("\n🔴 ERRORS:")
            for error in self.errors:
                report.append(f"  - {error}")

        if self.warnings:
            report.append("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                report.append(f"  - {warning}")

        if not self.errors:
            report.append("\n✅ System validation passed!")
        else:
            report.append("\n❌ System validation failed - fix errors above")

        report.append("\n💡 SUGGESTIONS:")
        for suggestion in self.suggestions[:5]:  # Top 5
            report.append(f"  {suggestion}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)

    def run_full_validation(self) -> bool:
        """Run complete system validation"""
        logger.info("Starting full system validation...\n")

        results = {
            'dependencies': self.check_dependencies(),
            'configuration': self.check_configuration(),
            'modules': self.check_modules(),
            'mt5': self.check_mt5_connection(),
        }

        try:
            results['performance'] = self.check_performance()
        except Exception as e:
            logger.warning(f"Performance check skipped: {e}")

        self.suggest_optimizations()

        # Print report
        report = self.generate_report()
        print(report)

        # Save report
        report_path = Path("system_validation_report.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"\nReport saved to: {report_path}")

        return all([results['dependencies'], results['configuration'], results['modules']])


def main():
    """Main function"""
    validator = SystemValidator()
    success = validator.run_full_validation()

    if success:
        print("\n✅ System is ready for use!")
        print("   Next steps:")
        print("   1. Configure .env file with your credentials")
        print("   2. Run: python quick_backtest.py")
        return 0
    else:
        print("\n❌ System validation failed")
        print("   Please fix the errors above before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
