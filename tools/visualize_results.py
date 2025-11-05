"""
Visualization Tools for Backtest Results
Creates charts and performance reports
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

sns.set_style("darkgrid")


class ResultsVisualizer:
    """Visualize backtest results"""

    def __init__(self, results_dir: str = "backtest_results"):
        """
        Initialize visualizer

        Args:
            results_dir: Directory containing backtest results
        """
        self.results_dir = Path(results_dir)
        self.trades_df = None
        self.equity_curve = None
        self.summary = None

        self._load_data()

    def _load_data(self):
        """Load backtest results from files"""
        try:
            self.trades_df = pd.read_csv(self.results_dir / "trades.csv")
            self.trades_df['entry_time'] = pd.to_datetime(self.trades_df['entry_time'])
            self.trades_df['exit_time'] = pd.to_datetime(self.trades_df['exit_time'])

            equity_df = pd.read_csv(self.results_dir / "equity_curve.csv")
            equity_df.columns = ['time', 'equity']
            equity_df['time'] = pd.to_datetime(equity_df['time'])
            self.equity_curve = equity_df.set_index('time')['equity']

            self.summary = pd.read_csv(self.results_dir / "summary.csv")

            print(f"Loaded {len(self.trades_df)} trades")
        except Exception as e:
            print(f"Error loading data: {e}")

    def plot_equity_curve(self, save: bool = True):
        """Plot equity curve"""
        if self.equity_curve is None:
            print("No equity curve data")
            return

        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot equity
        ax.plot(self.equity_curve.index, self.equity_curve.values,
               linewidth=2, color='#2E86AB', label='Equity')

        # Add underwater chart (drawdown)
        cummax = self.equity_curve.cummax()
        drawdown = (self.equity_curve - cummax) / cummax * 100

        ax2 = ax.twinx()
        ax2.fill_between(drawdown.index, 0, drawdown.values,
                        alpha=0.3, color='red', label='Drawdown %')

        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Equity ($)', fontsize=12)
        ax2.set_ylabel('Drawdown (%)', fontsize=12)
        ax.set_title('Equity Curve and Drawdown', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            plt.savefig(self.results_dir / 'equity_curve.png', dpi=150, bbox_inches='tight')
            print(f"Saved: {self.results_dir / 'equity_curve.png'}")

        plt.show()

    def plot_trade_distribution(self, save: bool = True):
        """Plot trade P&L distribution"""
        if self.trades_df is None:
            print("No trade data")
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. P&L histogram
        axes[0, 0].hist(self.trades_df['pnl'], bins=30, edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(0, color='red', linestyle='--', linewidth=2)
        axes[0, 0].set_xlabel('P&L ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('P&L Distribution')

        # 2. Win/Loss pie chart
        wins = len(self.trades_df[self.trades_df['pnl'] > 0])
        losses = len(self.trades_df[self.trades_df['pnl'] <= 0])
        axes[0, 1].pie([wins, losses], labels=['Wins', 'Losses'],
                      autopct='%1.1f%%', colors=['#2E8B57', '#DC143C'])
        axes[0, 1].set_title(f'Win Rate: {wins/(wins+losses)*100:.1f}%')

        # 3. Cumulative P&L
        cumulative_pnl = self.trades_df['pnl'].cumsum()
        axes[1, 0].plot(range(len(cumulative_pnl)), cumulative_pnl, linewidth=2)
        axes[1, 0].axhline(0, color='red', linestyle='--', linewidth=1)
        axes[1, 0].set_xlabel('Trade Number')
        axes[1, 0].set_ylabel('Cumulative P&L ($)')
        axes[1, 0].set_title('Cumulative P&L Over Time')
        axes[1, 0].grid(True, alpha=0.3)

        # 4. P&L by symbol
        pnl_by_symbol = self.trades_df.groupby('symbol')['pnl'].sum().sort_values()
        pnl_by_symbol.plot(kind='barh', ax=axes[1, 1], color='steelblue')
        axes[1, 1].set_xlabel('Total P&L ($)')
        axes[1, 1].set_title('P&L by Symbol')
        axes[1, 1].grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save:
            plt.savefig(self.results_dir / 'trade_distribution.png', dpi=150, bbox_inches='tight')
            print(f"Saved: {self.results_dir / 'trade_distribution.png'}")

        plt.show()

    def plot_trade_timeline(self, save: bool = True):
        """Plot trades on timeline"""
        if self.trades_df is None:
            print("No trade data")
            return

        fig, ax = plt.subplots(figsize=(14, 8))

        # Separate wins and losses
        wins = self.trades_df[self.trades_df['pnl'] > 0]
        losses = self.trades_df[self.trades_df['pnl'] <= 0]

        # Plot wins
        ax.scatter(wins['exit_time'], wins['pnl'],
                  c='green', alpha=0.6, s=100, label='Wins', edgecolors='black')

        # Plot losses
        ax.scatter(losses['exit_time'], losses['pnl'],
                  c='red', alpha=0.6, s=100, label='Losses', edgecolors='black')

        ax.axhline(0, color='black', linestyle='-', linewidth=1)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('P&L ($)', fontsize=12)
        ax.set_title('Trade P&L Timeline', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45)
        plt.tight_layout()

        if save:
            plt.savefig(self.results_dir / 'trade_timeline.png', dpi=150, bbox_inches='tight')
            print(f"Saved: {self.results_dir / 'trade_timeline.png'}")

        plt.show()

    def plot_monthly_returns(self, save: bool = True):
        """Plot monthly returns heatmap"""
        if self.trades_df is None:
            print("No trade data")
            return

        # Group by month
        self.trades_df['month'] = self.trades_df['exit_time'].dt.to_period('M')
        monthly_returns = self.trades_df.groupby('month')['pnl'].sum()

        # Create year-month matrix
        monthly_returns.index = monthly_returns.index.to_timestamp()
        monthly_returns_df = monthly_returns.to_frame()
        monthly_returns_df['year'] = monthly_returns_df.index.year
        monthly_returns_df['month'] = monthly_returns_df.index.month

        pivot = monthly_returns_df.pivot(index='year', columns='month', values='pnl')

        # Plot heatmap
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn',
                   center=0, cbar_kws={'label': 'P&L ($)'}, ax=ax)
        ax.set_title('Monthly Returns Heatmap', fontsize=14, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Year')

        plt.tight_layout()

        if save:
            plt.savefig(self.results_dir / 'monthly_returns.png', dpi=150, bbox_inches='tight')
            print(f"Saved: {self.results_dir / 'monthly_returns.png'}")

        plt.show()

    def generate_report(self):
        """Generate comprehensive HTML report"""
        if self.summary is None:
            print("No summary data")
            return

        html = f"""
        <html>
        <head>
            <title>Backtest Results Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                h1 {{ color: #2E86AB; }}
                h2 {{ color: #555; border-bottom: 2px solid #2E86AB; padding-bottom: 10px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background: white; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #2E86AB; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .positive {{ color: green; font-weight: bold; }}
                .negative {{ color: red; font-weight: bold; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>Forex DeepSeeker - Backtest Results</h1>

            <h2>Performance Summary</h2>
            <table>
        """

        for _, row in self.summary.iterrows():
            value_class = ""
            if "Return" in row['Metric'] or "Ratio" in row['Metric']:
                try:
                    val = float(row['Value'].replace('%', '').replace('$', '').replace(',', ''))
                    value_class = 'positive' if val > 0 else 'negative'
                except:
                    pass

            html += f"<tr><td><strong>{row['Metric']}</strong></td><td class='{value_class}'>{row['Value']}</td></tr>\n"

        html += """
            </table>

            <h2>Equity Curve</h2>
            <img src="equity_curve.png" alt="Equity Curve">

            <h2>Trade Distribution</h2>
            <img src="trade_distribution.png" alt="Trade Distribution">

            <h2>Trade Timeline</h2>
            <img src="trade_timeline.png" alt="Trade Timeline">

            <h2>Monthly Returns</h2>
            <img src="monthly_returns.png" alt="Monthly Returns">

        </body>
        </html>
        """

        report_path = self.results_dir / 'report.html'
        with open(report_path, 'w') as f:
            f.write(html)

        print(f"\nReport generated: {report_path}")
        print(f"Open in browser: file://{report_path.absolute()}")

    def plot_all(self, save: bool = True):
        """Generate all plots"""
        print("Generating visualizations...")
        self.plot_equity_curve(save)
        self.plot_trade_distribution(save)
        self.plot_trade_timeline(save)
        self.plot_monthly_returns(save)
        self.generate_report()
        print("\nAll visualizations complete!")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Visualize backtest results')
    parser.add_argument('--dir', type=str, default='backtest_results',
                       help='Results directory')
    args = parser.parse_args()

    viz = ResultsVisualizer(args.dir)
    viz.plot_all(save=True)


if __name__ == "__main__":
    main()
