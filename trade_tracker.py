"""
Trade Tracker - Track trades, calculate pips, P&L, and capital
"""

import json
import os
from datetime import datetime


class TradeTracker:
    """Track trading performance with pip calculations"""
    
    def __init__(self, data_file="trade_history.json"):
        self.data_file = data_file
        self.trades = []
        self.initial_capital = 1000  # Default starting capital
        self.current_capital = 1000
        self.load_data()
    
    def load_data(self):
        """Load trade history from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.trades = data.get('trades', [])
                    self.initial_capital = data.get('initial_capital', 1000)
                    self.current_capital = data.get('current_capital', 1000)
            except:
                pass
    
    def save_data(self):
        """Save trade history to file"""
        data = {
            'trades': self.trades,
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def set_initial_capital(self, amount):
        """Set starting capital"""
        self.initial_capital = amount
        self.current_capital = amount
        self.save_data()
    
    def calculate_pips(self, asset, entry, exit_price):
        """Calculate pips based on asset type"""
        if asset.upper() == "BTC":
            # For BTC: 1 pip = $1 (simplified)
            pips = abs(exit_price - entry)
        elif asset.upper() in ["GOLD", "XAU", "XAUUSD"]:
            # For Gold: 1 pip = $0.10
            pips = abs(exit_price - entry) * 10
        else:
            pips = abs(exit_price - entry)
        
        return round(pips, 2)
    
    def calculate_profit_loss(self, entry, exit_price, position_size, direction):
        """Calculate P&L in dollars"""
        if direction.upper() == "BUY":
            pnl = (exit_price - entry) * position_size
        else:  # SELL
            pnl = (entry - exit_price) * position_size
        
        return round(pnl, 2)
    
    def add_trade(self, asset, direction, entry, sl, tp1, tp2, position_size, signal_id=None, signal_tier=None, is_daily_signal=False):
        """Add a new trade
        
        Args:
            asset: Trading asset
            direction: BUY or SELL
            entry: Entry price
            sl: Stop loss price
            tp1: Take profit 1 price
            tp2: Take profit 2 price
            position_size: Position size
            signal_id: Optional signal ID (for daily signals)
            signal_tier: Optional signal tier (A_PLUS, A_GRADE, B_GRADE)
            is_daily_signal: Whether this is from daily signals system
        """
        trade = {
            'id': len(self.trades) + 1,
            'asset': asset,
            'direction': direction,
            'entry': entry,
            'stop_loss': sl,
            'tp1': tp1,
            'tp2': tp2,
            'position_size': position_size,
            'status': 'OPEN',
            'opened_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'closed_at': None,
            'exit_price': None,
            'pips': None,
            'pnl': None,
            'capital_before': self.current_capital,
            'capital_after': None,
            'return_pct': None,
            'signal_id': signal_id,
            'signal_tier': signal_tier,
            'is_daily_signal': is_daily_signal
        }
        
        self.trades.append(trade)
        self.save_data()
        return trade['id']
    
    def close_trade(self, trade_id, exit_price, exit_type="TP"):
        """Close a trade and calculate results"""
        trade = None
        for t in self.trades:
            if t['id'] == trade_id and t['status'] == 'OPEN':
                trade = t
                break
        
        if not trade:
            return None
        
        # Calculate pips
        pips = self.calculate_pips(trade['asset'], trade['entry'], exit_price)
        
        # Calculate P&L
        pnl = self.calculate_profit_loss(
            trade['entry'],
            exit_price,
            trade['position_size'],
            trade['direction']
        )
        
        # Update capital
        new_capital = self.current_capital + pnl
        return_pct = (pnl / self.current_capital) * 100
        
        # Update trade
        trade['status'] = 'CLOSED'
        trade['exit_price'] = exit_price
        trade['exit_type'] = exit_type
        trade['pips'] = pips
        trade['pnl'] = pnl
        trade['capital_after'] = new_capital
        trade['return_pct'] = round(return_pct, 2)
        trade['closed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.current_capital = new_capital
        self.save_data()
        
        # If this is a daily signal, update the daily signals system
        if trade.get('is_daily_signal') and trade.get('signal_id'):
            try:
                from daily_signals_system import update_daily_signal_outcome
                outcome = 'WIN' if pnl > 0 else 'LOSS' if pnl < 0 else 'BREAKEVEN'
                update_daily_signal_outcome(trade['signal_id'], outcome, pnl)
            except Exception as e:
                # Silently fail if daily signals system not available
                pass
        
        return trade
    
    def get_open_trades(self):
        """Get all open trades"""
        return [t for t in self.trades if t['status'] == 'OPEN']
    
    def get_closed_trades(self):
        """Get all closed trades"""
        return [t for t in self.trades if t['status'] == 'CLOSED']
    
    def get_statistics(self, daily_signals_only=False):
        """Get trading statistics
        
        Args:
            daily_signals_only: If True, only include trades from daily signals system
        """
        closed = self.get_closed_trades()
        
        # Filter for daily signals if requested
        if daily_signals_only:
            closed = [t for t in closed if t.get('is_daily_signal', False)]
        
        if not closed:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'total_pips': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'initial_capital': self.initial_capital,
                'current_capital': self.current_capital,
                'total_return': 0,
                'total_return_pct': 0,
                'daily_signals_only': daily_signals_only
            }
        
        wins = [t for t in closed if t['pnl'] > 0]
        losses = [t for t in closed if t['pnl'] <= 0]
        
        total_pips = sum(t['pips'] for t in closed if t['pnl'] > 0) - sum(t['pips'] for t in closed if t['pnl'] < 0)
        total_pnl = sum(t['pnl'] for t in closed)
        
        avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
        
        gross_profit = sum(t['pnl'] for t in wins)
        gross_loss = abs(sum(t['pnl'] for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        total_return = self.current_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Add tier-specific stats for daily signals
        tier_stats = {}
        if daily_signals_only:
            for tier in ['A_PLUS', 'A_GRADE', 'B_GRADE']:
                tier_trades = [t for t in closed if t.get('signal_tier') == tier]
                if tier_trades:
                    tier_wins = len([t for t in tier_trades if t['pnl'] > 0])
                    tier_pnl = sum(t['pnl'] for t in tier_trades)
                    tier_stats[tier] = {
                        'count': len(tier_trades),
                        'wins': tier_wins,
                        'win_rate': round((tier_wins / len(tier_trades)) * 100, 2),
                        'total_pnl': round(tier_pnl, 2)
                    }
        
        stats = {
            'total_trades': len(closed),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round((len(wins) / len(closed)) * 100, 2) if closed else 0,
            'total_pips': round(total_pips, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'initial_capital': self.initial_capital,
            'current_capital': round(self.current_capital, 2),
            'total_return': round(total_return, 2),
            'total_return_pct': round(total_return_pct, 2),
            'daily_signals_only': daily_signals_only
        }
        
        if tier_stats:
            stats['tier_statistics'] = tier_stats
        
        return stats
    
    def get_pip_info(self, asset, entry, sl, tp1, tp2):
        """Get pip information for a trade setup"""
        sl_pips = self.calculate_pips(asset, entry, sl)
        tp1_pips = self.calculate_pips(asset, entry, tp1)
        tp2_pips = self.calculate_pips(asset, entry, tp2)
        
        return {
            'sl_pips': sl_pips,
            'tp1_pips': tp1_pips,
            'tp2_pips': tp2_pips,
            'rr_tp1': round(tp1_pips / sl_pips, 2) if sl_pips > 0 else 0,
            'rr_tp2': round(tp2_pips / sl_pips, 2) if sl_pips > 0 else 0
        }


# Example usage
if __name__ == "__main__":
    tracker = TradeTracker()
    
    # Set initial capital
    tracker.set_initial_capital(1000)
    
    # Add a trade
    trade_id = tracker.add_trade(
        asset="BTC",
        direction="BUY",
        entry=95000,
        sl=94500,
        tp1=96000,
        tp2=97000,
        position_size=0.01
    )
    
    print(f"Trade #{trade_id} opened!")
    
    # Get pip info
    pip_info = tracker.get_pip_info("BTC", 95000, 94500, 96000, 97000)
    print(f"SL: {pip_info['sl_pips']} pips")
    print(f"TP1: {pip_info['tp1_pips']} pips (R:R 1:{pip_info['rr_tp1']})")
    print(f"TP2: {pip_info['tp2_pips']} pips (R:R 1:{pip_info['rr_tp2']})")
    
    # Close trade at TP1
    result = tracker.close_trade(trade_id, 96000, "TP1")
    print(f"\nTrade closed!")
    print(f"Pips: {result['pips']}")
    print(f"P&L: ${result['pnl']}")
    print(f"New Capital: ${result['capital_after']}")
    print(f"Return: {result['return_pct']}%")
    
    # Get statistics
    stats = tracker.get_statistics()
    print(f"\nStatistics:")
    print(f"Win Rate: {stats['win_rate']}%")
    print(f"Total P&L: ${stats['total_pnl']}")
    print(f"Total Return: {stats['total_return_pct']}%")
