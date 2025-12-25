"""
Signal Performance Tracker
Tracks signal outcomes and calculates real-time win rates
Logs signal lifecycle: generated → executed → outcome
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


class SignalPerformanceTracker:
    """
    Tracks signal performance and calculates real-time metrics
    """
    
    def __init__(self, storage_file: str = "signal_performance.json"):
        self.storage_file = storage_file
        self.signals = self._load_signals()
    
    def _load_signals(self) -> List[Dict]:
        """Load signals from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_signals(self):
        """Save signals to storage file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.signals, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving signals: {e}")
    
    def log_signal_generated(self, signal: Dict) -> str:
        """
        Log when a signal is generated
        
        Args:
            signal: Signal dictionary with signal details
            
        Returns:
            signal_id: Unique identifier for this signal
        """
        signal_id = f"{signal.get('symbol', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        signal_record = {
            'signal_id': signal_id,
            'symbol': signal.get('symbol', 'UNKNOWN'),
            'direction': signal.get('direction', 'UNKNOWN'),
            'entry_price': signal.get('entry', signal.get('entry_price')),
            'stop_loss': signal.get('stop_loss'),
            'take_profit_1': signal.get('take_profit_1'),
            'take_profit_2': signal.get('take_profit_2'),
            'confidence': signal.get('confidence', 0),
            'criteria_met': signal.get('criteria_met', 0),
            'quality_score': signal.get('quality_score'),
            'generated_at': datetime.now().isoformat(),
            'status': 'GENERATED',
            'executed': False,
            'outcome': None,
            'executed_at': None,
            'closed_at': None,
            'final_pnl': None,
            'win': None
        }
        
        self.signals.append(signal_record)
        self._save_signals()
        
        return signal_id
    
    def log_signal_executed(self, signal_id: str, execution_price: float, 
                           execution_time: Optional[datetime] = None):
        """
        Log when a signal is executed
        
        Args:
            signal_id: Signal identifier
            execution_price: Price at which signal was executed
            execution_time: Time of execution (defaults to now)
        """
        signal = self._find_signal(signal_id)
        if signal:
            signal['executed'] = True
            signal['execution_price'] = execution_price
            signal['executed_at'] = (execution_time or datetime.now()).isoformat()
            signal['status'] = 'EXECUTED'
            self._save_signals()
    
    def log_signal_outcome(self, signal_id: str, outcome: str, 
                          final_price: float, pnl: float = None):
        """
        Log signal outcome (WIN/LOSS)
        
        Args:
            signal_id: Signal identifier
            outcome: 'WIN' or 'LOSS'
            final_price: Final price when position closed
            pnl: Profit/Loss amount (optional)
        """
        signal = self._find_signal(signal_id)
        if signal:
            signal['outcome'] = outcome
            signal['win'] = (outcome == 'WIN')
            signal['final_price'] = final_price
            signal['closed_at'] = datetime.now().isoformat()
            signal['status'] = 'CLOSED'
            if pnl is not None:
                signal['final_pnl'] = pnl
            self._save_signals()
    
    def _find_signal(self, signal_id: str) -> Optional[Dict]:
        """Find signal by ID"""
        for signal in self.signals:
            if signal.get('signal_id') == signal_id:
                return signal
        return None
    
    def calculate_win_rate(self, days: Optional[int] = None, 
                         symbol: Optional[str] = None) -> Dict:
        """
        Calculate win rate statistics
        
        Args:
            days: Number of days to look back (None = all time)
            symbol: Filter by symbol (None = all symbols)
            
        Returns:
            Dict with win rate statistics
        """
        # Filter signals
        filtered_signals = self.signals
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_signals = [
                s for s in filtered_signals
                if s.get('generated_at') and 
                datetime.fromisoformat(s['generated_at']) >= cutoff_date
            ]
        
        if symbol:
            filtered_signals = [
                s for s in filtered_signals
                if s.get('symbol') == symbol
            ]
        
        # Only count closed signals
        closed_signals = [s for s in filtered_signals if s.get('status') == 'CLOSED']
        
        if not closed_signals:
            return {
                'total_signals': 0,
                'closed_signals': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'message': 'No closed signals found'
            }
        
        wins = sum(1 for s in closed_signals if s.get('win') == True)
        losses = sum(1 for s in closed_signals if s.get('win') == False)
        total = len(closed_signals)
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        return {
            'total_signals': len(filtered_signals),
            'closed_signals': total,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'period': f"{days} days" if days else "All time",
            'symbol': symbol or "All symbols"
        }
    
    def calculate_performance_by_quality(self) -> Dict:
        """Calculate performance breakdown by quality score"""
        closed_signals = [s for s in self.signals if s.get('status') == 'CLOSED']
        
        if not closed_signals:
            return {'message': 'No closed signals found'}
        
        quality_buckets = {
            'EXCELLENT': {'wins': 0, 'losses': 0, 'signals': []},
            'VERY_GOOD': {'wins': 0, 'losses': 0, 'signals': []},
            'GOOD': {'wins': 0, 'losses': 0, 'signals': []},
            'FAIR': {'wins': 0, 'losses': 0, 'signals': []},
            'POOR': {'wins': 0, 'losses': 0, 'signals': []},
            'INSUFFICIENT': {'wins': 0, 'losses': 0, 'signals': []}
        }
        
        for signal in closed_signals:
            grade = signal.get('quality_grade', 'UNKNOWN')
            if grade in quality_buckets:
                quality_buckets[grade]['signals'].append(signal)
                if signal.get('win'):
                    quality_buckets[grade]['wins'] += 1
                else:
                    quality_buckets[grade]['losses'] += 1
        
        # Calculate win rates for each bucket
        results = {}
        for grade, data in quality_buckets.items():
            total = data['wins'] + data['losses']
            if total > 0:
                win_rate = (data['wins'] / total * 100)
                results[grade] = {
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'total': total,
                    'win_rate': round(win_rate, 2)
                }
        
        return results
    
    def calculate_performance_by_symbol(self) -> Dict:
        """Calculate performance breakdown by trading symbol"""
        closed_signals = [s for s in self.signals if s.get('status') == 'CLOSED']
        
        if not closed_signals:
            return {'message': 'No closed signals found'}
        
        symbol_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})
        
        for signal in closed_signals:
            symbol = signal.get('symbol', 'UNKNOWN')
            if signal.get('win'):
                symbol_stats[symbol]['wins'] += 1
            else:
                symbol_stats[symbol]['losses'] += 1
        
        # Calculate win rates
        results = {}
        for symbol, stats in symbol_stats.items():
            total = stats['wins'] + stats['losses']
            win_rate = (stats['wins'] / total * 100) if total > 0 else 0
            results[symbol] = {
                'wins': stats['wins'],
                'losses': stats['losses'],
                'total': total,
                'win_rate': round(win_rate, 2)
            }
        
        return results
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get most recent signals"""
        sorted_signals = sorted(
            self.signals,
            key=lambda x: x.get('generated_at', ''),
            reverse=True
        )
        return sorted_signals[:limit]
    
    def get_statistics(self) -> Dict:
        """Get comprehensive performance statistics"""
        closed_signals = [s for s in self.signals if s.get('status') == 'CLOSED']
        
        if not closed_signals:
            return {
                'total_generated': len(self.signals),
                'total_executed': sum(1 for s in self.signals if s.get('executed')),
                'total_closed': 0,
                'message': 'No closed signals yet'
            }
        
        wins = [s for s in closed_signals if s.get('win') == True]
        losses = [s for s in closed_signals if s.get('win') == False]
        
        # Calculate average confidence for wins vs losses
        win_confidence = [s.get('confidence', 0) for s in wins if s.get('confidence')]
        loss_confidence = [s.get('confidence', 0) for s in losses if s.get('confidence')]
        
        return {
            'total_generated': len(self.signals),
            'total_executed': sum(1 for s in self.signals if s.get('executed')),
            'total_closed': len(closed_signals),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(len(wins) / len(closed_signals) * 100, 2) if closed_signals else 0,
            'avg_confidence_wins': round(statistics.mean(win_confidence), 2) if win_confidence else 0,
            'avg_confidence_losses': round(statistics.mean(loss_confidence), 2) if loss_confidence else 0,
            'by_quality': self.calculate_performance_by_quality(),
            'by_symbol': self.calculate_performance_by_symbol()
        }


# =================================================================
# USAGE EXAMPLE
# =================================================================

if __name__ == "__main__":
    print("SIGNAL PERFORMANCE TRACKER - TESTING")
    print("="*60)
    
    tracker = SignalPerformanceTracker("test_performance.json")
    
    # Example: Log a generated signal
    example_signal = {
        'symbol': 'BTC',
        'direction': 'BUY',
        'entry': 43000,
        'stop_loss': 42500,
        'take_profit_1': 44000,
        'take_profit_2': 45000,
        'confidence': 85,
        'criteria_met': 18,
        'quality_score': 88.5
    }
    
    signal_id = tracker.log_signal_generated(example_signal)
    print(f"\nLogged signal: {signal_id}")
    
    # Log execution
    tracker.log_signal_executed(signal_id, 43050)
    print(f"Logged execution at $43,050")
    
    # Log outcome (example: WIN)
    tracker.log_signal_outcome(signal_id, 'WIN', 44500, 450)
    print(f"Logged outcome: WIN")
    
    # Get statistics
    stats = tracker.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total Generated: {stats['total_generated']}")
    print(f"  Total Closed: {stats['total_closed']}")
    print(f"  Win Rate: {stats['win_rate']}%")
    
    # Clean up test file
    if os.path.exists("test_performance.json"):
        os.remove("test_performance.json")
    
    print("\n" + "="*60)
    print("Signal performance tracker loaded successfully!")

