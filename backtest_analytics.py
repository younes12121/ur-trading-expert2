"""
Comprehensive Backtest Analytics Module
Calculates institutional-grade performance metrics and generates reports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from pathlib import Path


class BacktestAnalytics:
    """Comprehensive analytics for backtest results"""
    
    def __init__(self, trades_df: pd.DataFrame, equity_curve_df: pd.DataFrame,
                 initial_capital: float, start_date: datetime, end_date: datetime):
        self.trades_df = trades_df
        self.equity_curve_df = equity_curve_df
        self.initial_capital = initial_capital
        self.start_date = start_date
        self.end_date = end_date
        
        if len(equity_curve_df) > 0:
            self.final_capital = equity_curve_df['equity'].iloc[-1]
        else:
            self.final_capital = initial_capital
        
        # Calculate trading period
        self.trading_days = (end_date - start_date).days
        self.trading_years = self.trading_days / 365.25
    
    def calculate_all_metrics(self) -> Dict:
        """Calculate all performance metrics"""
        if len(self.trades_df) == 0:
            return self._empty_metrics()
        
        metrics = {}
        
        # Basic metrics
        metrics.update(self._calculate_basic_metrics())
        
        # Risk-adjusted metrics
        metrics.update(self._calculate_risk_metrics())
        
        # Trade analysis
        metrics.update(self._calculate_trade_metrics())
        
        # Advanced metrics
        metrics.update(self._calculate_advanced_metrics())
        
        # Cost analysis
        metrics.update(self._calculate_cost_metrics())
        
        return metrics
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics when no trades"""
        return {
            'total_trades': 0,
            'total_return_pct': 0,
            'total_pnl': 0,
            'message': 'No trades executed'
        }
    
    def _calculate_basic_metrics(self) -> Dict:
        """Calculate basic performance metrics"""
        total_trades = len(self.trades_df)
        winning_trades = self.trades_df[self.trades_df['pnl'] > 0]
        losing_trades = self.trades_df[self.trades_df['pnl'] < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = self.trades_df['pnl'].sum()
        total_return = (self.final_capital - self.initial_capital) / self.initial_capital * 100
        
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return_pct': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'best_trade': self.trades_df['pnl'].max(),
            'worst_trade': self.trades_df['pnl'].min(),
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital
        }
    
    def _calculate_risk_metrics(self) -> Dict:
        """Calculate risk-adjusted metrics"""
        equity = self.equity_curve_df['equity'].values
        
        if len(equity) < 2:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'calmar_ratio': 0,
                'max_drawdown_pct': 0,
                'max_drawdown_duration_days': 0,
                'volatility': 0,
                'downside_deviation': 0
            }
        
        # Calculate returns
        returns = pd.Series(equity).pct_change().dropna()
        
        # Sharpe Ratio (annualized)
        if len(returns) > 0 and returns.std() != 0:
            # Annualize based on trading period
            periods_per_year = len(returns) / max(self.trading_years, 0.01)
            sharpe = (returns.mean() / returns.std()) * np.sqrt(periods_per_year)
        else:
            sharpe = 0
        
        # Sortino Ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() != 0:
            periods_per_year = len(returns) / max(self.trading_years, 0.01)
            sortino = (returns.mean() / downside_returns.std()) * np.sqrt(periods_per_year)
            downside_dev = downside_returns.std() * np.sqrt(periods_per_year) * 100
        else:
            sortino = 0
            downside_dev = 0
        
        # Maximum Drawdown
        peak = pd.Series(equity).expanding().max()
        drawdown = (pd.Series(equity) - peak) / peak * 100
        max_drawdown = drawdown.min()
        
        # Max drawdown duration
        max_dd_duration = self._calculate_max_drawdown_duration(equity, self.equity_curve_df.index)
        
        # Calmar Ratio (CAGR / Max Drawdown)
        cagr = self._calculate_cagr()
        calmar = abs(cagr / max_drawdown) if max_drawdown != 0 else 0
        
        # Volatility (annualized)
        if len(returns) > 0:
            periods_per_year = len(returns) / max(self.trading_years, 0.01)
            volatility = returns.std() * np.sqrt(periods_per_year) * 100
        else:
            volatility = 0
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'max_drawdown_pct': max_drawdown,
            'max_drawdown_duration_days': max_dd_duration,
            'volatility': volatility,
            'downside_deviation': downside_dev
        }
    
    def _calculate_trade_metrics(self) -> Dict:
        """Calculate trade-specific metrics"""
        if len(self.trades_df) == 0:
            return {}
        
        # Average trade duration
        avg_duration = self.trades_df['duration_hours'].mean()
        median_duration = self.trades_df['duration_hours'].median()
        
        # TP hit rates
        tp1_hit_rate = (self.trades_df['tp1_hit'].sum() / len(self.trades_df)) * 100 if 'tp1_hit' in self.trades_df.columns else 0
        tp2_hit_rate = (self.trades_df['tp2_hit'].sum() / len(self.trades_df)) * 100 if 'tp2_hit' in self.trades_df.columns else 0
        
        # Exit reason breakdown
        exit_reasons = self.trades_df['exit_reason'].value_counts().to_dict() if 'exit_reason' in self.trades_df.columns else {}
        
        # Consecutive wins/losses
        pnl_signs = (self.trades_df['pnl'] > 0).astype(int)
        consecutive_wins = self._max_consecutive(pnl_signs, 1)
        consecutive_losses = self._max_consecutive(pnl_signs, 0)
        
        # Expectancy
        win_prob = len(self.trades_df[self.trades_df['pnl'] > 0]) / len(self.trades_df)
        loss_prob = 1 - win_prob
        avg_win = self.trades_df[self.trades_df['pnl'] > 0]['pnl'].mean() if win_prob > 0 else 0
        avg_loss = abs(self.trades_df[self.trades_df['pnl'] < 0]['pnl'].mean()) if loss_prob > 0 else 0
        expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)
        
        # Exposure time (time in market)
        total_exposure_hours = self.trades_df['duration_hours'].sum()
        exposure_pct = (total_exposure_hours / (self.trading_days * 24)) * 100 if self.trading_days > 0 else 0
        
        return {
            'avg_trade_duration_hours': avg_duration,
            'median_trade_duration_hours': median_duration,
            'tp1_hit_rate': tp1_hit_rate,
            'tp2_hit_rate': tp2_hit_rate,
            'exit_reasons': exit_reasons,
            'max_consecutive_wins': consecutive_wins,
            'max_consecutive_losses': consecutive_losses,
            'expectancy': expectancy,
            'exposure_time_pct': exposure_pct,
            'total_exposure_hours': total_exposure_hours
        }
    
    def _calculate_advanced_metrics(self) -> Dict:
        """Calculate advanced performance metrics"""
        if len(self.trades_df) == 0:
            return {}
        
        # CAGR
        cagr = self._calculate_cagr()
        
        # Turnover (how often positions are opened/closed)
        total_trades = len(self.trades_df)
        turnover = total_trades / max(self.trading_years, 0.01)
        
        # Win/Loss ratio
        winning_trades = self.trades_df[self.trades_df['pnl'] > 0]
        losing_trades = self.trades_df[self.trades_df['pnl'] < 0]
        win_loss_ratio = abs(winning_trades['pnl'].mean() / losing_trades['pnl'].mean()) if len(losing_trades) > 0 and losing_trades['pnl'].mean() != 0 else 0
        
        # Recovery factor (net profit / max drawdown)
        total_pnl = self.trades_df['pnl'].sum()
        max_dd = abs(self._calculate_risk_metrics()['max_drawdown_pct'])
        recovery_factor = total_pnl / (self.initial_capital * max_dd / 100) if max_dd > 0 else 0
        
        # Average win/loss by exit reason
        exit_reason_stats = {}
        if 'exit_reason' in self.trades_df.columns:
            for reason in self.trades_df['exit_reason'].unique():
                reason_trades = self.trades_df[self.trades_df['exit_reason'] == reason]
                exit_reason_stats[reason] = {
                    'count': len(reason_trades),
                    'avg_pnl': reason_trades['pnl'].mean(),
                    'win_rate': (reason_trades['pnl'] > 0).sum() / len(reason_trades) * 100
                }
        
        return {
            'cagr': cagr,
            'turnover': turnover,
            'win_loss_ratio': win_loss_ratio,
            'recovery_factor': recovery_factor,
            'exit_reason_stats': exit_reason_stats,
            'trading_days': self.trading_days,
            'trading_years': self.trading_years
        }
    
    def _calculate_cost_metrics(self) -> Dict:
        """Calculate cost analysis (fees, slippage)"""
        if len(self.trades_df) == 0:
            return {
                'total_fees': 0,
                'total_slippage': 0,
                'cost_drag_pct': 0
            }
        
        total_fees = 0
        total_slippage = 0
        
        if 'total_fees' in self.trades_df.columns:
            total_fees = self.trades_df['total_fees'].sum()
        
        if 'entry_slippage' in self.trades_df.columns and 'exit_slippage' in self.trades_df.columns:
            total_slippage = (self.trades_df['entry_slippage'] + self.trades_df['exit_slippage']).sum()
        
        total_costs = total_fees + total_slippage
        cost_drag_pct = (total_costs / self.initial_capital) * 100
        
        return {
            'total_fees': total_fees,
            'total_slippage': total_slippage,
            'total_costs': total_costs,
            'cost_drag_pct': cost_drag_pct,
            'avg_fee_per_trade': total_fees / len(self.trades_df) if len(self.trades_df) > 0 else 0,
            'avg_slippage_per_trade': total_slippage / len(self.trades_df) if len(self.trades_df) > 0 else 0
        }
    
    def _calculate_cagr(self) -> float:
        """Calculate Compound Annual Growth Rate"""
        if self.trading_years <= 0 or self.initial_capital <= 0:
            return 0
        
        if self.final_capital <= 0:
            return -100
        
        cagr = ((self.final_capital / self.initial_capital) ** (1 / self.trading_years) - 1) * 100
        return cagr
    
    def _calculate_max_drawdown_duration(self, equity: np.ndarray, timestamps: pd.Index) -> float:
        """Calculate maximum drawdown duration in days"""
        if len(equity) < 2:
            return 0
        
        peak = pd.Series(equity).expanding().max()
        drawdown = pd.Series(equity) - peak
        
        # Find periods in drawdown
        in_drawdown = drawdown < 0
        if not in_drawdown.any():
            return 0
        
        # Find longest drawdown period
        max_duration = 0
        current_duration = 0
        
        for i, in_dd in enumerate(in_drawdown):
            if in_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        # Convert to days (assuming timestamps are datetime)
        if isinstance(timestamps, pd.DatetimeIndex) and len(timestamps) > 1:
            time_delta = (timestamps[-1] - timestamps[0]).total_seconds() / 3600 / 24
            periods = len(equity)
            days_per_period = time_delta / periods if periods > 0 else 0
            return max_duration * days_per_period
        
        return max_duration
    
    def _max_consecutive(self, series: pd.Series, value: int) -> int:
        """Calculate maximum consecutive occurrences of a value"""
        max_count = 0
        current_count = 0
        
        for v in series:
            if v == value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    def generate_tearsheet(self, output_dir: str = "backtests", filename: str = None) -> Dict:
        """Generate comprehensive tearsheet report"""
        all_metrics = self.calculate_all_metrics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_tearsheet_{timestamp}"
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save JSON
        json_path = output_path / f"{filename}.json"
        with open(json_path, 'w') as f:
            json.dump(all_metrics, f, indent=2, default=str)
        
        # Generate HTML report
        html_path = output_path / f"{filename}.html"
        html_content = self._generate_html_tearsheet(all_metrics)
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        # Generate CSV summary
        csv_path = output_path / f"{filename}_summary.csv"
        summary_df = self._generate_summary_dataframe(all_metrics)
        summary_df.to_csv(csv_path, index=False)
        
        return {
            'json_path': str(json_path),
            'html_path': str(html_path),
            'csv_path': str(csv_path),
            'metrics': all_metrics
        }
    
    def _generate_summary_dataframe(self, metrics: Dict) -> pd.DataFrame:
        """Generate summary DataFrame for CSV export"""
        summary_data = {
            'Metric': [],
            'Value': []
        }
        
        # Basic metrics
        summary_data['Metric'].extend([
            'Total Trades', 'Winning Trades', 'Losing Trades', 'Win Rate (%)',
            'Total Return (%)', 'CAGR (%)', 'Total P&L', 'Initial Capital', 'Final Capital'
        ])
        summary_data['Value'].extend([
            metrics.get('total_trades', 0),
            metrics.get('winning_trades', 0),
            metrics.get('losing_trades', 0),
            f"{metrics.get('win_rate', 0):.2f}",
            f"{metrics.get('total_return_pct', 0):.2f}",
            f"{metrics.get('cagr', 0):.2f}",
            f"{metrics.get('total_pnl', 0):.2f}",
            f"{metrics.get('initial_capital', 0):.2f}",
            f"{metrics.get('final_capital', 0):.2f}"
        ])
        
        # Risk metrics
        summary_data['Metric'].extend([
            'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio',
            'Max Drawdown (%)', 'Volatility (%)', 'Max Drawdown Duration (days)'
        ])
        summary_data['Value'].extend([
            f"{metrics.get('sharpe_ratio', 0):.2f}",
            f"{metrics.get('sortino_ratio', 0):.2f}",
            f"{metrics.get('calmar_ratio', 0):.2f}",
            f"{metrics.get('max_drawdown_pct', 0):.2f}",
            f"{metrics.get('volatility', 0):.2f}",
            f"{metrics.get('max_drawdown_duration_days', 0):.1f}"
        ])
        
        # Trade metrics
        summary_data['Metric'].extend([
            'Profit Factor', 'Expectancy', 'Avg Win', 'Avg Loss',
            'Best Trade', 'Worst Trade', 'Turnover'
        ])
        summary_data['Value'].extend([
            f"{metrics.get('profit_factor', 0):.2f}",
            f"{metrics.get('expectancy', 0):.2f}",
            f"{metrics.get('avg_win', 0):.2f}",
            f"{metrics.get('avg_loss', 0):.2f}",
            f"{metrics.get('best_trade', 0):.2f}",
            f"{metrics.get('worst_trade', 0):.2f}",
            f"{metrics.get('turnover', 0):.2f}"
        ])
        
        # Cost metrics
        summary_data['Metric'].extend([
            'Total Fees', 'Total Slippage', 'Cost Drag (%)'
        ])
        summary_data['Value'].extend([
            f"{metrics.get('total_fees', 0):.2f}",
            f"{metrics.get('total_slippage', 0):.2f}",
            f"{metrics.get('cost_drag_pct', 0):.2f}"
        ])
        
        return pd.DataFrame(summary_data)
    
    def _generate_html_tearsheet(self, metrics: Dict) -> str:
        """Generate HTML tearsheet"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Backtest Tearsheet</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric-card {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; margin-top: 5px; }}
        .positive {{ color: #4CAF50; }}
        .negative {{ color: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        .section {{ margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Backtest Performance Report</h1>
        <p><strong>Period:</strong> {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}</p>
        <p><strong>Trading Days:</strong> {metrics.get('trading_days', 0)} | <strong>Trading Years:</strong> {metrics.get('trading_years', 0):.2f}</p>
        
        <div class="section">
            <h2>Performance Overview</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Return</div>
                    <div class="metric-value {'positive' if metrics.get('total_return_pct', 0) >= 0 else 'negative'}">
                        {metrics.get('total_return_pct', 0):+.2f}%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">CAGR</div>
                    <div class="metric-value {'positive' if metrics.get('cagr', 0) >= 0 else 'negative'}">
                        {metrics.get('cagr', 0):+.2f}%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Sharpe Ratio</div>
                    <div class="metric-value">{metrics.get('sharpe_ratio', 0):.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Max Drawdown</div>
                    <div class="metric-value negative">{metrics.get('max_drawdown_pct', 0):.2f}%</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Trade Statistics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Trades</td><td>{metrics.get('total_trades', 0)}</td></tr>
                <tr><td>Winning Trades</td><td>{metrics.get('winning_trades', 0)}</td></tr>
                <tr><td>Losing Trades</td><td>{metrics.get('losing_trades', 0)}</td></tr>
                <tr><td>Win Rate</td><td>{metrics.get('win_rate', 0):.2f}%</td></tr>
                <tr><td>Profit Factor</td><td>{metrics.get('profit_factor', 0):.2f}</td></tr>
                <tr><td>Expectancy</td><td>${metrics.get('expectancy', 0):.2f}</td></tr>
                <tr><td>Average Win</td><td>${metrics.get('avg_win', 0):.2f}</td></tr>
                <tr><td>Average Loss</td><td>${metrics.get('avg_loss', 0):.2f}</td></tr>
                <tr><td>Best Trade</td><td>${metrics.get('best_trade', 0):.2f}</td></tr>
                <tr><td>Worst Trade</td><td>${metrics.get('worst_trade', 0):.2f}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Risk Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Sortino Ratio</td><td>{metrics.get('sortino_ratio', 0):.2f}</td></tr>
                <tr><td>Calmar Ratio</td><td>{metrics.get('calmar_ratio', 0):.2f}</td></tr>
                <tr><td>Volatility</td><td>{metrics.get('volatility', 0):.2f}%</td></tr>
                <tr><td>Downside Deviation</td><td>{metrics.get('downside_deviation', 0):.2f}%</td></tr>
                <tr><td>Max Drawdown Duration</td><td>{metrics.get('max_drawdown_duration_days', 0):.1f} days</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Cost Analysis</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Fees</td><td>${metrics.get('total_fees', 0):.2f}</td></tr>
                <tr><td>Total Slippage</td><td>${metrics.get('total_slippage', 0):.2f}</td></tr>
                <tr><td>Total Costs</td><td>${metrics.get('total_costs', 0):.2f}</td></tr>
                <tr><td>Cost Drag</td><td>{metrics.get('cost_drag_pct', 0):.2f}%</td></tr>
            </table>
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def print_comprehensive_report(self):
        """Print comprehensive performance report"""
        metrics = self.calculate_all_metrics()
        
        if metrics.get('total_trades', 0) == 0:
            print("=" * 70)
            print("No trades executed in backtest")
            print("=" * 70)
            return
        
        print("=" * 70)
        print("📊 COMPREHENSIVE BACKTEST REPORT")
        print("=" * 70)
        print(f"Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        print(f"Trading Days: {metrics.get('trading_days', 0)} | Years: {metrics.get('trading_years', 0):.2f}")
        print()
        
        print("PERFORMANCE OVERVIEW:")
        print("-" * 70)
        print(f"Initial Capital:        ${metrics.get('initial_capital', 0):,.2f}")
        print(f"Final Capital:          ${metrics.get('final_capital', 0):,.2f}")
        print(f"Total Return:           {metrics.get('total_return_pct', 0):+.2f}%")
        print(f"CAGR:                   {metrics.get('cagr', 0):+.2f}%")
        print()
        
        print("TRADE STATISTICS:")
        print("-" * 70)
        print(f"Total Trades:           {metrics.get('total_trades', 0)}")
        print(f"Winning Trades:         {metrics.get('winning_trades', 0)}")
        print(f"Losing Trades:          {metrics.get('losing_trades', 0)}")
        print(f"Win Rate:               {metrics.get('win_rate', 0):.1f}%")
        print(f"Profit Factor:          {metrics.get('profit_factor', 0):.2f}")
        print(f"Expectancy:             ${metrics.get('expectancy', 0):.2f}")
        print(f"Average Win:            ${metrics.get('avg_win', 0):,.2f}")
        print(f"Average Loss:           ${metrics.get('avg_loss', 0):,.2f}")
        print(f"Best Trade:             ${metrics.get('best_trade', 0):+,.2f}")
        print(f"Worst Trade:            ${metrics.get('worst_trade', 0):+,.2f}")
        print()
        
        print("RISK METRICS:")
        print("-" * 70)
        print(f"Sharpe Ratio:           {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"Sortino Ratio:          {metrics.get('sortino_ratio', 0):.2f}")
        print(f"Calmar Ratio:           {metrics.get('calmar_ratio', 0):.2f}")
        print(f"Max Drawdown:           {metrics.get('max_drawdown_pct', 0):.2f}%")
        print(f"Max DD Duration:        {metrics.get('max_drawdown_duration_days', 0):.1f} days")
        print(f"Volatility:             {metrics.get('volatility', 0):.2f}%")
        print(f"Downside Deviation:     {metrics.get('downside_deviation', 0):.2f}%")
        print()
        
        print("COST ANALYSIS:")
        print("-" * 70)
        print(f"Total Fees:             ${metrics.get('total_fees', 0):,.2f}")
        print(f"Total Slippage:         ${metrics.get('total_slippage', 0):,.2f}")
        print(f"Total Costs:            ${metrics.get('total_costs', 0):,.2f}")
        print(f"Cost Drag:              {metrics.get('cost_drag_pct', 0):.2f}%")
        print()
        
        if metrics.get('exit_reasons'):
            print("EXIT REASONS:")
            print("-" * 70)
            for reason, count in metrics['exit_reasons'].items():
                pct = (count / metrics['total_trades']) * 100
                print(f"{reason:20s} {count:3d} ({pct:.1f}%)")
            print()
        
        print("=" * 70)


if __name__ == "__main__":
    print("Backtest analytics module ready!")
