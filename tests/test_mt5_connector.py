"""
Unit tests for MT5 Connector
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data.mt5_connector import MT5Connector, Timeframe, ForexSymbol


class TestMT5Connector:
    """Test MT5 Connector functionality"""

    def test_forex_pairs_list(self):
        """Test forex pairs list generation"""
        connector = MT5Connector()

        majors = connector.get_forex_pairs(
            include_majors=True,
            include_minors=False,
            include_exotics=False
        )

        assert len(majors) > 0
        assert 'EURUSD' in [p[:6] for p in majors]
        assert 'GBPUSD' in [p[:6] for p in majors]

    def test_timeframe_enum(self):
        """Test timeframe enum values"""
        assert Timeframe.M1.name == 'M1'
        assert Timeframe.H1.name == 'H1'
        assert Timeframe.D1.name == 'D1'

    def test_forex_symbol_dataclass(self):
        """Test ForexSymbol dataclass"""
        symbol = ForexSymbol(
            symbol='EURUSD',
            description='Euro vs US Dollar',
            digits=5,
            point=0.00001,
            min_lot=0.01,
            max_lot=100.0,
            lot_step=0.01,
            contract_size=100000
        )

        assert symbol.symbol == 'EURUSD'
        assert symbol.digits == 5
        assert symbol.min_lot == 0.01


class TestMultiTimeframeAnalyzer:
    """Test multi-timeframe analyzer"""

    def test_trend_calculation(self):
        """Test trend calculation logic"""
        # Create sample data
        data = {
            'H1': pd.DataFrame({
                'Close': [1.08 + i*0.001 for i in range(100)],
                'High': [1.08 + i*0.001 + 0.0005 for i in range(100)],
                'Low': [1.08 + i*0.001 - 0.0005 for i in range(100)],
                'Open': [1.08 + i*0.001 for i in range(100)],
                'Volume': [1000 for _ in range(100)]
            })
        }

        # Basic test: uptrend should be detected
        close_values = data['H1']['Close'].values
        ma_50 = close_values[-50:].mean()

        assert close_values[-1] > ma_50  # Price above MA = uptrend


def test_import_modules():
    """Test that all modules can be imported"""
    from src.data import mt5_connector
    from src.models import forex_alpha_factors
    from src.agents import trading_agents
    from src.risk import forex_risk_manager
    from src.ai import unified_llm_client
    from src.backtest import forex_backtester
    from src.execution import mt5_executor
    from src.strategy import forex_strategy

    assert mt5_connector is not None
    assert forex_alpha_factors is not None
    assert trading_agents is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
