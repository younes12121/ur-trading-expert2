"""
Paper Trading Module
Virtual trading environment for testing strategies without real money
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class PaperTrading:
    """Manages paper trading (virtual trading) accounts"""
    
    def __init__(self, data_file="paper_trading.json"):
        self.data_file = data_file
        self.accounts = {}  # {user_id: {enabled, balance, equity, trades, positions}}
        self.load_data()
    
    def load_data(self):
        """Load paper trading data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.accounts = json.load(f)
            except:
                self.accounts = {}
        else:
            self.accounts = {}
    
    def save_data(self):
        """Save paper trading data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.accounts, f, indent=2)
    
    def enable_paper_trading(self, user_id: int, starting_balance: float = 10000.0) -> bool:
        """Enable paper trading for a user
        
        Args:
            user_id: User ID
            starting_balance: Starting virtual balance (default $10,000)
        
        Returns:
            True if enabled
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.accounts:
            self.accounts[user_id_str] = {
                'enabled': True,
                'balance': starting_balance,
                'equity': starting_balance,
                'starting_balance': starting_balance,
                'trades': [],
                'open_positions': [],
                'closed_positions': [],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0.0
            }
        else:
            self.accounts[user_id_str]['enabled'] = True
        
        self.save_data()
        return True
    
    def disable_paper_trading(self, user_id: int) -> bool:
        """Disable paper trading for a user"""
        user_id_str = str(user_id)
        
        if user_id_str in self.accounts:
            self.accounts[user_id_str]['enabled'] = False
            self.save_data()
            return True
        return False
    
    def is_enabled(self, user_id: int) -> bool:
        """Check if paper trading is enabled for user"""
        user_id_str = str(user_id)
        return self.accounts.get(user_id_str, {}).get('enabled', False)
    
    def get_account(self, user_id: int) -> Optional[Dict]:
        """Get paper trading account info"""
        user_id_str = str(user_id)
        return self.accounts.get(user_id_str)
    
    def open_position(self, user_id: int, symbol: str, direction: str, 
                     entry_price: float, lots: float, sl: float, tp: float) -> Dict:
        """Open a paper trading position
        
        Args:
            user_id: User ID
            symbol: Trading symbol
            direction: 'buy' or 'sell'
            entry_price: Entry price
            lots: Position size in lots
            sl: Stop loss price
            tp: Take profit price
        
        Returns:
            Dict with position info or error
        """
        user_id_str = str(user_id)
        
        if not self.is_enabled(user_id):
            return {'success': False, 'error': 'Paper trading not enabled'}
        
        account = self.accounts[user_id_str]
        
        # Calculate position value (simplified - would use proper margin calculation)
        position_value = lots * 100000  # Standard lot = 100,000 units
        margin_required = position_value * 0.01  # 1% margin (100:1 leverage)
        
        if account['equity'] < margin_required:
            return {'success': False, 'error': 'Insufficient margin'}
        
        # Create position
        position = {
            'id': len(account['open_positions']) + 1,
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'lots': lots,
            'sl': sl,
            'tp': tp,
            'opened_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'margin_used': margin_required
        }
        
        account['open_positions'].append(position)
        account['equity'] -= margin_required
        account['total_trades'] += 1
        
        self.save_data()
        
        return {
            'success': True,
            'position_id': position['id'],
            'position': position
        }
    
    def close_position(self, user_id: int, position_id: int, exit_price: float) -> Dict:
        """Close a paper trading position
        
        Args:
            user_id: User ID
            position_id: Position ID to close
            exit_price: Exit price
        
        Returns:
            Dict with result
        """
        user_id_str = str(user_id)
        
        if not self.is_enabled(user_id):
            return {'success': False, 'error': 'Paper trading not enabled'}
        
        account = self.accounts[user_id_str]
        
        # Find position
        position = None
        position_index = None
        for i, pos in enumerate(account['open_positions']):
            if pos['id'] == position_id:
                position = pos
                position_index = i
                break
        
        if not position:
            return {'success': False, 'error': 'Position not found'}
        
        # Calculate P&L
        if position['direction'] == 'buy':
            pips = (exit_price - position['entry_price']) * 10000  # For forex
            pnl = pips * position['lots'] * 10  # Simplified calculation
        else:  # sell
            pips = (position['entry_price'] - exit_price) * 10000
            pnl = pips * position['lots'] * 10
        
        # Update account
        account['balance'] += pnl
        account['equity'] += pnl + position['margin_used']  # Return margin + P&L
        account['total_pnl'] += pnl
        
        if pnl > 0:
            account['winning_trades'] += 1
        else:
            account['losing_trades'] += 1
        
        # Move to closed positions
        closed_position = position.copy()
        closed_position['exit_price'] = exit_price
        closed_position['pnl'] = pnl
        closed_position['pips'] = pips
        closed_position['closed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        account['closed_positions'].append(closed_position)
        account['open_positions'].pop(position_index)
        
        self.save_data()
        
        return {
            'success': True,
            'position_id': position_id,
            'pnl': pnl,
            'pips': pips,
            'balance': account['balance'],
            'equity': account['equity']
        }
    
    def get_account_summary(self, user_id: int) -> str:
        """Get formatted account summary"""
        account = self.get_account(user_id)
        
        if not account:
            return "❌ Paper trading not enabled. Use `/paper on` to start."
        
        if not account['enabled']:
            return "❌ Paper trading is disabled. Use `/paper on` to enable."
        
        total_closed = account['winning_trades'] + account['losing_trades']
        win_rate = (account['winning_trades'] / total_closed * 100) if total_closed > 0 else 0
        
        msg = "📊 *PAPER TRADING ACCOUNT*\n\n"
        msg += f"*Balance:* ${account['balance']:,.2f}\n"
        msg += f"*Equity:* ${account['equity']:,.2f}\n"
        msg += f"*Starting Balance:* ${account['starting_balance']:,.2f}\n"
        msg += f"*Total P&L:* ${account['total_pnl']:,.2f}\n"
        msg += f"*Return:* {((account['balance'] - account['starting_balance']) / account['starting_balance'] * 100):.2f}%\n\n"
        
        msg += f"*Open Positions:* {len(account['open_positions'])}\n"
        msg += f"*Total Trades:* {account['total_trades']}\n"
        msg += f"*Wins:* {account['winning_trades']}\n"
        msg += f"*Losses:* {account['losing_trades']}\n"
        msg += f"*Win Rate:* {win_rate:.1f}%\n\n"
        
        if account['open_positions']:
            msg += "*OPEN POSITIONS:*\n"
            for pos in account['open_positions'][:5]:
                msg += f"• #{pos['id']}: {pos['symbol']} {pos['direction'].upper()} "
                msg += f"{pos['lots']} lots @ ${pos['entry_price']:,.2f}\n"
            if len(account['open_positions']) > 5:
                msg += f"...and {len(account['open_positions']) - 5} more\n"
        
        return msg

