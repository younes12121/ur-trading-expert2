"""
Trade Logger and Database Manager
SQLite database for trade tracking and performance monitoring
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import os

class TradeDatabase:
    """Manage trade database"""
    
    def __init__(self, db_path: str = "data_cache/trades.db"):
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                stop_loss REAL NOT NULL,
                take_profit_1 REAL NOT NULL,
                take_profit_2 REAL NOT NULL,
                lot_size REAL NOT NULL,
                confidence REAL NOT NULL,
                status TEXT NOT NULL,
                pnl REAL,
                pnl_pct REAL,
                exit_reason TEXT,
                duration_hours REAL,
                tp1_hit INTEGER DEFAULT 0,
                tp2_hit INTEGER DEFAULT 0
            )
        ''')
        
        # Performance log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                capital REAL NOT NULL,
                daily_pnl REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                winning_trades INTEGER NOT NULL,
                losing_trades INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                drawdown_pct REAL NOT NULL
            )
        ''')
        
        # Signals table (all generated signals, even if not traded)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                confidence REAL NOT NULL,
                signal_strength REAL,
                traded INTEGER DEFAULT 0,
                skip_reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_trade(self, trade: Dict) -> int:
        """Log a new trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, direction, entry_price, stop_loss,
                take_profit_1, take_profit_2, lot_size, confidence, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade.get('timestamp', datetime.now().isoformat()),
            trade['direction'],
            trade['entry_price'],
            trade['stop_loss'],
            trade['take_profit_1'],
            trade['take_profit_2'],
            trade['lot_size'],
            trade['confidence'],
            'OPEN'
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def update_trade(self, trade_id: int, updates: Dict):
        """Update an existing trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [trade_id]
        
        cursor.execute(f'''
            UPDATE trades SET {set_clause} WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def log_signal(self, signal: Dict, traded: bool = False, skip_reason: str = None):
        """Log a generated signal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (
                timestamp, direction, entry_price, confidence,
                signal_strength, traded, skip_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            signal['direction'],
            signal.get('entry_price', 0),
            signal.get('confidence', 0),
            signal.get('signal_strength', 0),
            1 if traded else 0,
            skip_reason
        ))
        
        conn.commit()
        conn.close()
    
    def log_performance(self, stats: Dict):
        """Log daily performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_log (
                timestamp, capital, daily_pnl, total_trades,
                winning_trades, losing_trades, win_rate, drawdown_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            stats['capital'],
            stats['daily_pnl'],
            stats['total_trades'],
            stats['winning_trades'],
            stats['losing_trades'],
            stats['win_rate'],
            stats['drawdown_pct']
        ))
        
        conn.commit()
        conn.close()
    
    def get_trades(self, limit: int = 100, status: str = None) -> pd.DataFrame:
        """Get trades from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM trades"
        if status:
            query += f" WHERE status = '{status}'"
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_performance_stats(self) -> Dict:
        """Get overall performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get trade statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                AVG(CASE WHEN pnl < 0 THEN pnl END) as avg_loss,
                SUM(pnl) as total_pnl
            FROM trades
            WHERE status = 'CLOSED'
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats[0] == 0:
            return {'total_trades': 0}
        
        return {
            'total_trades': stats[0],
            'winning_trades': stats[1] or 0,
            'losing_trades': stats[2] or 0,
            'win_rate': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
            'avg_win': stats[3] or 0,
            'avg_loss': stats[4] or 0,
            'total_pnl': stats[5] or 0
        }
    
    def print_summary(self):
        """Print database summary"""
        stats = self.get_performance_stats()
        
        print("=" * 70)
        print("📊 TRADE DATABASE SUMMARY")
        print("=" * 70)
        
        if stats['total_trades'] == 0:
            print("No trades recorded yet")
        else:
            print(f"Total Trades:      {stats['total_trades']}")
            print(f"Winning Trades:    {stats['winning_trades']}")
            print(f"Losing Trades:     {stats['losing_trades']}")
            print(f"Win Rate:          {stats['win_rate']:.1f}%")
            print(f"Average Win:       ${stats['avg_win']:.2f}")
            print(f"Average Loss:      ${stats['avg_loss']:.2f}")
            print(f"Total P&L:         ${stats['total_pnl']:+.2f}")
        
        print("=" * 70)


class AlertManager:
    """Manage trading alerts (console, file, future: Telegram/Email)"""
    
    def __init__(self, log_file: str = "data_cache/alerts.log"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def send_alert(self, message: str, level: str = "INFO"):
        """Send an alert"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_msg = f"[{timestamp}] [{level}] {message}"
        
        # Print to console
        emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅',
            'TRADE': '💰'
        }.get(level, 'ℹ️')
        
        print(f"{emoji} {formatted_msg}")
        
        # Log to file
        with open(self.log_file, 'a') as f:
            f.write(formatted_msg + '\n')
    
    def alert_trade_opened(self, trade: Dict):
        """Alert when trade is opened"""
        msg = f"Trade Opened: {trade['direction']} at ${trade['entry_price']:,.2f} (Confidence: {trade['confidence']}%)"
        self.send_alert(msg, 'TRADE')
    
    def alert_trade_closed(self, trade: Dict, pnl: float):
        """Alert when trade is closed"""
        msg = f"Trade Closed: {trade['direction']} - P&L: ${pnl:+.2f}"
        level = 'SUCCESS' if pnl > 0 else 'WARNING'
        self.send_alert(msg, level)
    
    def alert_risk_limit(self, reason: str):
        """Alert when risk limit is hit"""
        self.send_alert(f"Risk Limit Hit: {reason}", 'WARNING')
    
    def alert_error(self, error: str):
        """Alert on error"""
        self.send_alert(f"Error: {error}", 'ERROR')


# Test
if __name__ == "__main__":
    print("Testing Trade Database...")
    
    db = TradeDatabase()
    
    # Test trade logging
    test_trade = {
        'timestamp': datetime.now().isoformat(),
        'direction': 'BUY',
        'entry_price': 86000,
        'stop_loss': 85700,
        'take_profit_1': 86300,
        'take_profit_2': 86600,
        'lot_size': 0.02,
        'confidence': 68
    }
    
    trade_id = db.log_trade(test_trade)
    print(f"✅ Logged trade ID: {trade_id}")
    
    # Test alert manager
    alerts = AlertManager()
    alerts.alert_trade_opened(test_trade)
    
    # Print summary
    db.print_summary()
    
    print("\n✅ Database and alerts working!")
