"""
Trading Execution Engine
Simulates trade execution based on signals and tracks PnL for users
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from database import TradeDirection
from user_management_service import record_user_trade, close_user_trade, get_user_portfolio_data
from quantum_elite_signal_integration import enhance_signal_with_quantum_elite

logger = logging.getLogger(__name__)

class TradeStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class TradingExecutionEngine:
    """Engine for executing trades based on signals and tracking performance"""

    def __init__(self):
        self.active_trades = {}  # telegram_id -> list of active trade IDs
        self.pending_signals = {}  # telegram_id -> list of pending signals

    def execute_signal_for_user(self, telegram_id: int, signal: Dict, risk_amount: float = None) -> Dict[str, Any]:
        """Execute a trading signal for a user"""
        try:
            # Enhance signal with AI if available
            enhanced_signal = self._enhance_signal(signal)

            # Calculate position size based on risk management
            position_size = self._calculate_position_size(telegram_id, enhanced_signal, risk_amount)

            if position_size <= 0:
                return {
                    'success': False,
                    'error': 'Insufficient capital or risk management limits',
                    'signal': enhanced_signal
                }

            # Create trade record
            trade_data = {
                'asset': enhanced_signal.get('asset', signal.get('pair', 'EURUSD')),
                'direction': enhanced_signal.get('signal_type', signal.get('direction', 'BUY')),
                'entry': enhanced_signal.get('price', signal.get('entry', 1.0)),
                'stop_loss': enhanced_signal.get('stop_loss'),
                'tp1': enhanced_signal.get('tp1'),
                'tp2': enhanced_signal.get('tp2'),
                'position_size': position_size,
                'is_open': True
            }

            # Record the trade
            success = record_user_trade(telegram_id, trade_data)

            if success:
                # Add to active trades
                if telegram_id not in self.active_trades:
                    self.active_trades[telegram_id] = []
                # Note: We'd need to get the trade ID back from record_user_trade

                return {
                    'success': True,
                    'message': f'Trade executed: {trade_data["direction"]} {trade_data["asset"]} at {trade_data["entry"]}',
                    'trade': trade_data,
                    'enhanced_signal': enhanced_signal
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to record trade',
                    'signal': enhanced_signal
                }

        except Exception as e:
            logger.error(f"Error executing signal for user {telegram_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'signal': signal
            }

    def close_position_for_user(self, telegram_id: int, trade_id: int, exit_price: float,
                               exit_type: str = 'MANUAL') -> Dict[str, Any]:
        """Close an open position for a user"""
        try:
            success = close_user_trade(trade_id, exit_price, exit_type)

            if success:
                # Remove from active trades
                if telegram_id in self.active_trades:
                    if trade_id in self.active_trades[telegram_id]:
                        self.active_trades[telegram_id].remove(trade_id)

                return {
                    'success': True,
                    'message': f'Position closed at {exit_price}',
                    'exit_price': exit_price,
                    'exit_type': exit_type
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to close position'
                }

        except Exception as e:
            logger.error(f"Error closing position for user {telegram_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_user_active_trades(self, telegram_id: int) -> List[Dict]:
        """Get all active trades for a user"""
        try:
            portfolio_data = get_user_portfolio_data(telegram_id)
            return portfolio_data.get('active_positions', [])
        except Exception as e:
            logger.error(f"Error getting active trades for user {telegram_id}: {e}")
            return []

    def simulate_market_movement(self, telegram_id: int) -> Dict[str, Any]:
        """Simulate market movement and update positions (for demo purposes)"""
        try:
            active_trades = self.get_user_active_trades(telegram_id)

            updates = []
            for trade in active_trades:
                # Simulate price movement (±0.1% to ±2%)
                import random
                price_change_pct = random.uniform(-0.02, 0.02)
                current_price = trade['entry'] * (1 + price_change_pct)

                # Check if stop loss or take profit hit
                should_close = False
                exit_type = 'MANUAL'

                if trade.get('stop_loss'):
                    if trade['direction'] == 'BUY' and current_price <= trade['stop_loss']:
                        should_close = True
                        exit_type = 'SL'
                        current_price = trade['stop_loss']
                    elif trade['direction'] == 'SELL' and current_price >= trade['stop_loss']:
                        should_close = True
                        exit_type = 'SL'
                        current_price = trade['stop_loss']

                if trade.get('tp1'):
                    if trade['direction'] == 'BUY' and current_price >= trade['tp1']:
                        should_close = True
                        exit_type = 'TP1'
                        current_price = trade['tp1']
                    elif trade['direction'] == 'SELL' and current_price <= trade['tp1']:
                        should_close = True
                        exit_type = 'TP1'
                        current_price = trade['tp1']

                if should_close:
                    result = self.close_position_for_user(telegram_id, trade['id'], current_price, exit_type)
                    updates.append({
                        'trade_id': trade['id'],
                        'action': 'closed',
                        'exit_price': current_price,
                        'exit_type': exit_type,
                        'result': result
                    })
                else:
                    updates.append({
                        'trade_id': trade['id'],
                        'action': 'updated',
                        'current_price': current_price,
                        'pnl': self._calculate_pnl(trade, current_price)
                    })

            return {
                'success': True,
                'updates': updates,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error simulating market movement for user {telegram_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _enhance_signal(self, signal: Dict) -> Dict:
        """Enhance a signal with AI capabilities"""
        try:
            asset_symbol = signal.get('asset', signal.get('pair', 'EURUSD'))
            return enhance_signal_with_quantum_elite(signal, asset_symbol)
        except Exception as e:
            logger.warning(f"Failed to enhance signal: {e}")
            return signal

    def _calculate_position_size(self, telegram_id: int, signal: Dict, risk_amount: float = None) -> float:
        """Calculate position size based on risk management"""
        try:
            portfolio_data = get_user_portfolio_data(telegram_id)
            portfolio = portfolio_data.get('portfolio', {})

            current_capital = portfolio.get('current_capital', 500.0)
            risk_per_trade_pct = 0.01  # 1% default risk per trade

            # Use provided risk amount or calculate based on percentage
            if risk_amount:
                risk_amount = min(risk_amount, current_capital * 0.02)  # Max 2% of capital
            else:
                risk_amount = current_capital * risk_per_trade_pct

            entry_price = signal.get('price', signal.get('entry', 1.0))
            stop_loss = signal.get('stop_loss')

            if not stop_loss or entry_price == 0:
                return 0

            # Calculate pip risk
            pip_risk = abs(entry_price - stop_loss) / entry_price

            # Position size = risk amount / pip risk
            position_size = risk_amount / pip_risk if pip_risk > 0 else 0

            # Limit position size to reasonable bounds
            max_position_size = current_capital * 0.1  # Max 10% of capital per trade
            position_size = min(position_size, max_position_size)

            return position_size

        except Exception as e:
            logger.error(f"Error calculating position size for user {telegram_id}: {e}")
            return 0

    def _calculate_pnl(self, trade: Dict, current_price: float) -> float:
        """Calculate current P&L for a trade"""
        try:
            entry = trade.get('entry', 0)
            direction = trade.get('direction', 'BUY')
            position_size = trade.get('position_size', 0)

            if direction == 'BUY':
                pnl = (current_price - entry) * position_size * 100000  # Forex multiplier
            else:
                pnl = (entry - current_price) * position_size * 100000

            return pnl

        except Exception as e:
            logger.error(f"Error calculating PnL: {e}")
            return 0

    def get_user_performance_summary(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive performance summary for a user"""
        try:
            portfolio_data = get_user_portfolio_data(telegram_id)

            if not portfolio_data:
                return {}

            portfolio = portfolio_data.get('portfolio', {})
            performance = portfolio_data.get('performance', {})
            active_positions = portfolio_data.get('active_positions', [])
            recent_trades = portfolio_data.get('recent_trades', [])

            # Calculate additional metrics
            total_trades = performance.get('total_trades', 0)
            winning_trades = performance.get('winning_trades', 0)
            win_rate = performance.get('win_rate', 0)

            # Risk metrics
            max_drawdown = performance.get('max_drawdown', 0)
            profit_factor = performance.get('profit_factor', 0)

            # Current exposure
            active_exposure = sum([pos.get('position_size', 0) for pos in active_positions])
            total_exposure_pct = (active_exposure / portfolio.get('current_capital', 1)) * 100

            return {
                'overview': {
                    'total_trades': total_trades,
                    'win_rate': win_rate,
                    'total_pnl': portfolio.get('total_pnl', 0),
                    'current_capital': portfolio.get('current_capital', 0),
                    'capital_growth': portfolio.get('capital_growth', 0),
                    'active_positions': len(active_positions),
                    'total_exposure': active_exposure,
                    'exposure_percentage': total_exposure_pct
                },
                'risk_metrics': {
                    'max_drawdown': max_drawdown,
                    'profit_factor': profit_factor,
                    'avg_win': performance.get('avg_win', 0),
                    'avg_loss': performance.get('avg_loss', 0),
                    'largest_win': max([t.get('pnl', 0) for t in recent_trades if t.get('pnl', 0) > 0] or [0]),
                    'largest_loss': min([t.get('pnl', 0) for t in recent_trades if t.get('pnl', 0) < 0] or [0])
                },
                'active_positions': active_positions,
                'recent_trades': recent_trades[:10],  # Last 10 trades
                'daily_pnl': self._calculate_daily_pnl(recent_trades)
            }

        except Exception as e:
            logger.error(f"Error getting performance summary for user {telegram_id}: {e}")
            return {}

    def _calculate_daily_pnl(self, trades: List[Dict]) -> List[Dict]:
        """Calculate daily P&L from trade history"""
        try:
            daily_pnl = {}
            today = datetime.now().date()

            for trade in trades:
                if trade.get('closed_at'):
                    trade_date = datetime.fromisoformat(trade['closed_at']).date()
                    pnl = trade.get('pnl', 0)

                    if trade_date not in daily_pnl:
                        daily_pnl[trade_date] = 0
                    daily_pnl[trade_date] += pnl

            # Convert to list and sort by date
            daily_data = [
                {'date': date.isoformat(), 'pnl': pnl}
                for date, pnl in sorted(daily_pnl.items())
            ]

            return daily_data[-30:]  # Last 30 days

        except Exception as e:
            logger.error(f"Error calculating daily PnL: {e}")
            return []

# Global instance
trading_engine = TradingExecutionEngine()

# Convenience functions
def execute_user_signal(telegram_id: int, signal: Dict, risk_amount: float = None) -> Dict[str, Any]:
    """Execute a signal for a user"""
    return trading_engine.execute_signal_for_user(telegram_id, signal, risk_amount)

def close_user_position(telegram_id: int, trade_id: int, exit_price: float, exit_type: str = 'MANUAL') -> Dict[str, Any]:
    """Close a position for a user"""
    return trading_engine.close_position_for_user(telegram_id, trade_id, exit_price, exit_type)

def get_user_trading_performance(telegram_id: int) -> Dict[str, Any]:
    """Get trading performance for a user"""
    return trading_engine.get_user_performance_summary(telegram_id)

def simulate_user_market_movement(telegram_id: int) -> Dict[str, Any]:
    """Simulate market movement for user positions"""
    return trading_engine.simulate_market_movement(telegram_id)










