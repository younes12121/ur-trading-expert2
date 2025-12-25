"""
Performance Analytics Module
Provides detailed trading performance analysis and visualizations
"""

from datetime import datetime, timedelta
from collections import defaultdict
import json
import os


class PerformanceAnalytics:
    """Advanced performance analytics for trading"""
    
    def __init__(self, tracker):
        """
        Initialize analytics with trade tracker
        
        Args:
            tracker: TradeTracker instance
        """
        self.tracker = tracker
    
    def get_win_rate_by_pair(self):
        """Get win rate broken down by trading pair"""
        closed_trades = self.tracker.get_closed_trades()
        
        pair_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0})
        
        for trade in closed_trades:
            asset = trade['asset']
            pair_stats[asset]['total'] += 1
            
            if trade['pnl'] > 0:
                pair_stats[asset]['wins'] += 1
            else:
                pair_stats[asset]['losses'] += 1
        
        # Calculate win rates
        results = {}
        for asset, stats in pair_stats.items():
            win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
            results[asset] = {
                'wins': stats['wins'],
                'losses': stats['losses'],
                'total': stats['total'],
                'win_rate': round(win_rate, 1)
            }
        
        return results
    
    def get_pnl_distribution(self):
        """Get P&L distribution statistics"""
        closed_trades = self.tracker.get_closed_trades()
        
        if not closed_trades:
            return None
        
        wins = [t for t in closed_trades if t['pnl'] > 0]
        losses = [t for t in closed_trades if t['pnl'] <= 0]
        
        biggest_win = max([t['pnl'] for t in wins]) if wins else 0
        biggest_loss = min([t['pnl'] for t in losses]) if losses else 0
        avg_win = sum([t['pnl'] for t in wins]) / len(wins) if wins else 0
        avg_loss = sum([t['pnl'] for t in losses]) / len(losses) if losses else 0
        
        # Find which trade/pair had biggest win/loss
        biggest_win_trade = max(wins, key=lambda x: x['pnl']) if wins else None
        biggest_loss_trade = min(losses, key=lambda x: x['pnl']) if losses else None
        
        # Calculate achieved R:R
        achieved_rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            'biggest_win': round(biggest_win, 2),
            'biggest_win_pair': biggest_win_trade['asset'] if biggest_win_trade else 'N/A',
            'biggest_loss': round(biggest_loss, 2),
            'biggest_loss_pair': biggest_loss_trade['asset'] if biggest_loss_trade else 'N/A',
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'achieved_rr': round(achieved_rr, 2)
        }
    
    def get_session_performance(self):
        """Get performance broken down by trading session"""
        # This would require storing session info with each trade
        # For now, return placeholder
        return {
            'London/NY Overlap': {'win_rate': 0, 'trades': 0},
            'Tokyo Session': {'win_rate': 0, 'trades': 0},
            'Sydney Session': {'win_rate': 0, 'trades': 0}
        }
    
    def get_monthly_summary(self, year=None, month=None):
        """Get monthly trading summary"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        closed_trades = self.tracker.get_closed_trades()
        
        # Filter trades for this month
        month_trades = []
        for trade in closed_trades:
            if trade['closed_at']:
                trade_date = datetime.strptime(trade['closed_at'], '%Y-%m-%d %H:%M:%S')
                if trade_date.year == year and trade_date.month == month:
                    month_trades.append(trade)
        
        if not month_trades:
            return None
        
        wins = [t for t in month_trades if t['pnl'] > 0]
        losses = [t for t in month_trades if t['pnl'] <= 0]
        
        net_pnl = sum([t['pnl'] for t in month_trades])
        
        # Find best performing pair
        pair_pnl = defaultdict(float)
        for trade in month_trades:
            pair_pnl[trade['asset']] += trade['pnl']
        
        best_pair = max(pair_pnl.items(), key=lambda x: x[1]) if pair_pnl else ('N/A', 0)
        
        # Calculate ROI for the month
        first_trade = min(month_trades, key=lambda x: x['opened_at'])
        capital_start = first_trade['capital_before']
        roi = (net_pnl / capital_start * 100) if capital_start > 0 else 0
        
        return {
            'year': year,
            'month': month,
            'month_name': datetime(year, month, 1).strftime('%B %Y'),
            'total_trades': len(month_trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(len(wins) / len(month_trades) * 100, 1) if month_trades else 0,
            'net_pnl': round(net_pnl, 2),
            'roi': round(roi, 1),
            'best_pair': best_pair[0],
            'best_pair_pnl': round(best_pair[1], 2)
        }
    
    def generate_win_rate_chart(self, pair_stats):
        """Generate text-based win rate chart"""
        chart = "📊 WIN RATE BY PAIR\n"
        
        if not pair_stats:
            chart += "No trades yet\n"
            return chart
        
        # Sort by win rate
        sorted_pairs = sorted(pair_stats.items(), key=lambda x: x[1]['win_rate'], reverse=True)
        
        for asset, stats in sorted_pairs:
            win_rate = stats['win_rate']
            total = stats['total']
            wins = stats['wins']
            
            # Create progress bar (10 blocks)
            filled_blocks = int(win_rate / 10)
            empty_blocks = 10 - filled_blocks
            bar = "█" * filled_blocks + "░" * empty_blocks
            
            chart += f"{asset:8s}: {bar} {win_rate:.0f}% ({wins}/{total})\n"
        
        return chart
    
    def generate_full_analytics_report(self):
        """Generate complete analytics report"""
        stats = self.tracker.get_statistics()
        pair_stats = self.get_win_rate_by_pair()
        pnl_dist = self.get_pnl_distribution()
        monthly = self.get_monthly_summary()
        
        report = "📈 *PERFORMANCE ANALYTICS*\n\n"
        
        # Overall Statistics
        report += "*📊 OVERALL PERFORMANCE*\n"
        report += f"Total Trades: {stats['total_trades']}\n"
        report += f"Wins: {stats['wins']} | Losses: {stats['losses']}\n"
        report += f"Win Rate: {stats['win_rate']}%\n"
        report += f"Total P&L: ${stats['total_pnl']:,.2f}\n"
        report += f"ROI: {stats['total_return_pct']:.1f}%\n\n"
        
        # Win Rate Chart
        if pair_stats:
            report += self.generate_win_rate_chart(pair_stats)
            report += "\n"
        
        # P&L Distribution
        if pnl_dist:
            report += "*💰 P&L DISTRIBUTION*\n"
            report += f"Biggest Win: +${pnl_dist['biggest_win']:.2f} ({pnl_dist['biggest_win_pair']}) \n"
            report += f"Biggest Loss: ${pnl_dist['biggest_loss']:.2f} ({pnl_dist['biggest_loss_pair']})\n"
            report += f"Average Win: +${pnl_dist['avg_win']:.2f}\n"
            report += f"Average Loss: ${pnl_dist['avg_loss']:.2f}\n"
            report += f"R:R Achieved: 1:{pnl_dist['achieved_rr']:.2f}\n\n"
        
        # Monthly Summary
        if monthly:
            report += f"*📅 {monthly['month_name'].upper()}*\n"
            report += f"Trades: {monthly['total_trades']}\n"
            report += f"Wins: {monthly['wins']} ({monthly['win_rate']}%)\n"
            report += f"Net P&L: ${monthly['net_pnl']:,.2f}\n"
            report += f"ROI: {monthly['roi']:.1f}%\n"
            report += f"Best Pair: {monthly['best_pair']} (+${monthly['best_pair_pnl']:.2f})\n\n"
        
        # Capital Progress
        report += "*💵 CAPITAL PROGRESS*\n"
        report += f"Initial: ${stats['initial_capital']:,.2f}\n"
        report += f"Current: ${stats['current_capital']:,.2f}\n"
        report += f"Change: ${stats['total_return']:,.2f} ({stats['total_return_pct']:.1f}%)\n"
        
        return report
    
    def export_to_csv(self, filename="trade_history.csv", filter_type="all", filter_value=None):
        """
        Export trades to CSV file
        
        Args:
            filename: Output CSV filename
            filter_type: Type of filter - 'all', 'monthly', 'pair', 'wins', 'losses'
            filter_value: Value for filter (e.g., month name, pair name)
        
        Returns:
            tuple: (success, filepath, message)
        """
        import csv
        from datetime import datetime
        
        closed_trades = self.tracker.get_closed_trades()
        
        if not closed_trades:
            return (False, None, "No trades to export")
        
        # Apply filters
        filtered_trades = []
        
        if filter_type == "all":
            filtered_trades = closed_trades
            
        elif filter_type == "monthly":
            # Filter by month (e.g., "December 2024" or "12/2024")
            for trade in closed_trades:
                if trade['closed_at']:
                    trade_date = datetime.strptime(trade['closed_at'], '%Y-%m-%d %H:%M:%S')
                    if filter_value:
                        # Support both "December" and month number
                        try:
                            if filter_value.lower() in trade_date.strftime('%B').lower():
                                filtered_trades.append(trade)
                            elif filter_value == str(trade_date.month):
                                filtered_trades.append(trade)
                        except:
                            pass
                    else:
                        # Current month if no value specified
                        now = datetime.now()
                        if trade_date.month == now.month and trade_date.year == now.year:
                            filtered_trades.append(trade)
                            
        elif filter_type == "pair":
            # Filter by trading pair
            for trade in closed_trades:
                if filter_value and trade['asset'].upper() == filter_value.upper():
                    filtered_trades.append(trade)
                    
        elif filter_type == "wins":
            # Only winning trades
            filtered_trades = [t for t in closed_trades if t['pnl'] > 0]
            
        elif filter_type == "losses":
            # Only losing trades
            filtered_trades = [t for t in closed_trades if t['pnl'] <= 0]
        
        if not filtered_trades:
            return (False, None, f"No trades found for filter: {filter_type}")
        
        # Create CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Trade_ID', 'Opened_Date', 'Closed_Date', 'Pair', 'Direction',
                    'Entry_Price', 'Exit_Price', 'Stop_Loss', 'TP1', 'TP2',
                    'Exit_Type', 'Pips', 'PnL_USD', 'Capital_Before', 'Capital_After',
                    'Return_Pct', 'Status'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for trade in filtered_trades:
                    writer.writerow({
                        'Trade_ID': trade['id'],
                        'Opened_Date': trade['opened_at'],
                        'Closed_Date': trade['closed_at'] or 'N/A',
                        'Pair': trade['asset'],
                        'Direction': trade['direction'],
                        'Entry_Price': f"{trade['entry']:.5f}",
                        'Exit_Price': f"{trade['exit_price']:.5f}" if trade['exit_price'] else 'N/A',
                        'Stop_Loss': f"{trade['stop_loss']:.5f}",
                        'TP1': f"{trade['tp1']:.5f}",
                        'TP2': f"{trade['tp2']:.5f}",
                        'Exit_Type': trade.get('exit_type', 'N/A'),
                        'Pips': f"{trade['pips']:.2f}" if trade['pips'] else 'N/A',
                        'PnL_USD': f"{trade['pnl']:.2f}" if trade['pnl'] else 'N/A',
                        'Capital_Before': f"{trade['capital_before']:.2f}",
                        'Capital_After': f"{trade['capital_after']:.2f}" if trade['capital_after'] else 'N/A',
                        'Return_Pct': f"{trade['return_pct']:.2f}%" if trade['return_pct'] else 'N/A',
                        'Status': 'WIN' if trade['pnl'] and trade['pnl'] > 0 else 'LOSS'
                    })
            
            message = f"✅ Exported {len(filtered_trades)} trades to {filename}"
            return (True, filename, message)
            
        except Exception as e:
            return (False, None, f"Error creating CSV: {str(e)}")


# Testing
if __name__ == "__main__":
    from trade_tracker import TradeTracker
    
    tracker = TradeTracker()
    analytics = PerformanceAnalytics(tracker)
    
    # Generate report
    report = analytics.generate_full_analytics_report()
    print(report)
    
    # Test CSV export
    success, filepath, message = analytics.export_to_csv()
    print(f"\n{message}")
