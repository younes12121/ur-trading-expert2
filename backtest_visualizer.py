"""
Backtest Visualizer
Generate charts and reports for backtest results
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os

class BacktestVisualizer:
    """Create visualizations for backtest results"""
    
    def __init__(self, trades_df: pd.DataFrame, equity_df: pd.DataFrame, 
                 initial_capital: float):
        self.trades_df = trades_df
        self.equity_df = equity_df
        self.initial_capital = initial_capital
        
        # Create output directory
        self.output_dir = "backtest_reports"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def plot_equity_curve(self, save: bool = True):
        """Plot equity curve over time"""
        plt.figure(figsize=(12, 6))
        
        plt.plot(self.equity_df['timestamp'], self.equity_df['equity'], 
                linewidth=2, color='#2E86AB', label='Equity')
        plt.axhline(y=self.initial_capital, color='gray', linestyle='--', 
                   alpha=0.5, label='Initial Capital')
        
        plt.title('Equity Curve', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Equity ($)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/equity_curve.png', dpi=300)
            print(f"✅ Saved: {self.output_dir}/equity_curve.png")
        
        plt.close()
    
    def plot_drawdown(self, save: bool = True):
        """Plot drawdown chart"""
        equity = self.equity_df['equity'].values
        peak = pd.Series(equity).expanding().max()
        drawdown = (pd.Series(equity) - peak) / peak * 100
        
        plt.figure(figsize=(12, 6))
        
        plt.fill_between(range(len(drawdown)), drawdown, 0, 
                        color='#A23B72', alpha=0.3)
        plt.plot(drawdown, color='#A23B72', linewidth=2)
        
        plt.title('Drawdown Chart', fontsize=16, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Drawdown (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/drawdown.png', dpi=300)
            print(f"✅ Saved: {self.output_dir}/drawdown.png")
        
        plt.close()
    
    def plot_trade_distribution(self, save: bool = True):
        """Plot P&L distribution"""
        if len(self.trades_df) == 0:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histogram of P&L
        pnl = self.trades_df['pnl'].dropna()
        ax1.hist(pnl, bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax1.set_title('P&L Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('P&L ($)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Win/Loss pie chart
        wins = len(self.trades_df[self.trades_df['pnl'] > 0])
        losses = len(self.trades_df[self.trades_df['pnl'] < 0])
        
        ax2.pie([wins, losses], labels=['Wins', 'Losses'], 
               colors=['#18A558', '#A23B72'], autopct='%1.1f%%',
               startangle=90)
        ax2.set_title('Win/Loss Ratio', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/trade_distribution.png', dpi=300)
            print(f"✅ Saved: {self.output_dir}/trade_distribution.png")
        
        plt.close()
    
    def plot_monthly_returns(self, save: bool = True):
        """Plot monthly returns heatmap"""
        if len(self.trades_df) == 0:
            return
        
        # Calculate monthly returns
        self.trades_df['month'] = pd.to_datetime(self.trades_df['entry_time']).dt.to_period('M')
        monthly_pnl = self.trades_df.groupby('month')['pnl'].sum()
        
        plt.figure(figsize=(12, 6))
        
        colors = ['#A23B72' if x < 0 else '#18A558' for x in monthly_pnl.values]
        plt.bar(range(len(monthly_pnl)), monthly_pnl.values, color=colors, alpha=0.7)
        
        plt.title('Monthly Returns', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('P&L ($)', fontsize=12)
        plt.xticks(range(len(monthly_pnl)), 
                  [str(m) for m in monthly_pnl.index], rotation=45)
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/monthly_returns.png', dpi=300)
            print(f"✅ Saved: {self.output_dir}/monthly_returns.png")
        
        plt.close()
    
    def generate_html_report(self):
        """Generate HTML report with all charts"""
        from performance_metrics import PerformanceMetrics
        
        metrics_calc = PerformanceMetrics(self.trades_df, self.equity_df, 
                                         self.initial_capital)
        metrics = metrics_calc.calculate_all_metrics()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Backtest Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2E86AB;
            text-align: center;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2E86AB;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .chart {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        img {{
            width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>📊 Backtest Report</h1>
    <p style="text-align: center; color: #666;">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value">{metrics.get('total_return_pct', 0):.2f}%</div>
            <div class="metric-label">Total Return</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('win_rate', 0):.1f}%</div>
            <div class="metric-label">Win Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('sharpe_ratio', 0):.2f}</div>
            <div class="metric-label">Sharpe Ratio</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('total_trades', 0)}</div>
            <div class="metric-label">Total Trades</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('max_drawdown_pct', 0):.2f}%</div>
            <div class="metric-label">Max Drawdown</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('profit_factor', 0):.2f}</div>
            <div class="metric-label">Profit Factor</div>
        </div>
    </div>
    
    <div class="chart">
        <h2>Equity Curve</h2>
        <img src="equity_curve.png" alt="Equity Curve">
    </div>
    
    <div class="chart">
        <h2>Drawdown</h2>
        <img src="drawdown.png" alt="Drawdown">
    </div>
    
    <div class="chart">
        <h2>Trade Distribution</h2>
        <img src="trade_distribution.png" alt="Trade Distribution">
    </div>
    
    <div class="chart">
        <h2>Monthly Returns</h2>
        <img src="monthly_returns.png" alt="Monthly Returns">
    </div>
</body>
</html>
"""
        
        report_path = f'{self.output_dir}/backtest_report.html'
        with open(report_path, 'w') as f:
            f.write(html)
        
        print(f"✅ Saved: {report_path}")
        return report_path
    
    def generate_all(self):
        """Generate all visualizations and report"""
        print("=" * 70)
        print("📊 GENERATING BACKTEST VISUALIZATIONS")
        print("=" * 70)
        print()
        
        self.plot_equity_curve()
        self.plot_drawdown()
        self.plot_trade_distribution()
        self.plot_monthly_returns()
        report_path = self.generate_html_report()
        
        print()
        print("=" * 70)
        print("✅ ALL VISUALIZATIONS GENERATED!")
        print("=" * 70)
        print(f"\n📁 Output directory: {self.output_dir}/")
        print(f"📄 Open {report_path} in your browser to view the report")
        
        return report_path


# Test
if __name__ == "__main__":
    print("Backtest Visualizer ready!")
    print("\nTo use:")
    print("  from backtest_visualizer import BacktestVisualizer")
    print("  viz = BacktestVisualizer(trades_df, equity_df, initial_capital)")
    print("  viz.generate_all()")
