"""
PERSONAL TRADING DASHBOARD - Complete Trading Intelligence Platform
Flask-based web application for comprehensive trading analysis and signals
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import pandas as pd
import numpy as np
from functools import wraps
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key-change-in-production'

# Database setup
DATABASE = 'trading_dashboard.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                take_profit_1 REAL,
                take_profit_2 REAL,
                confidence INTEGER,
                category TEXT,
                session TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                pnl REAL,
                win_rate REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS market_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                status TEXT,
                start_time TIME,
                end_time TIME,
                active_pairs TEXT
            )
        ''')

        # Insert default market sessions
        conn.execute('''
            INSERT OR IGNORE INTO market_sessions (session_name, status, start_time, end_time, active_pairs)
            VALUES
            ('Asian Session', 'active', '00:00', '09:00', 'CNY,JPY,AUD'),
            ('European Session', 'active', '08:00', '17:00', 'EUR,GBP,CHF'),
            ('American Session', 'opening_soon', '13:30', '22:00', 'USD,CAD'),
            ('Crypto Markets', 'always_active', '00:00', '23:59', 'BTC,ETH')
        ''')

        conn.commit()

# Initialize database
init_db()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('personal_dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page"""
    if request.method == 'POST':
        # Simple authentication - replace with proper auth in production
        password = request.form.get('password')
        if password == 'trading2024':  # Change this!
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/signals')
@login_required
def get_signals():
    """Get live trading signals"""
    with get_db() as conn:
        signals = conn.execute('''
            SELECT * FROM signals
            WHERE status = 'active'
            ORDER BY timestamp DESC
            LIMIT 50
        ''').fetchall()

    signals_list = []
    for signal in signals:
        signals_list.append({
            'id': signal['id'],
            'symbol': signal['symbol'],
            'direction': signal['direction'],
            'entry': signal['entry_price'],
            'target': signal['take_profit_1'],
            'stop_loss': signal['stop_loss'],
            'confidence': signal['confidence'],
            'category': signal['category'],
            'session': signal['session'],
            'timestamp': signal['timestamp'],
            'time_ago': format_time_ago(signal['timestamp']),
            'status': signal['status']
        })

    return jsonify({'signals': signals_list})

@app.route('/api/performance')
@login_required
def get_performance():
    """Get performance analytics"""
    with get_db() as conn:
        # Get latest performance data
        performance = conn.execute('''
            SELECT * FROM performance
            ORDER BY date DESC
            LIMIT 30
        ''').fetchall()

    if performance:
        latest = performance[0]
        performance_data = {
            'win_rate_30d': latest['win_rate'],
            'total_trades': latest['total_trades'],
            'winning_trades': latest['winning_trades'],
            'losing_trades': latest['total_trades'] - latest['winning_trades'],
            'average_return': latest['pnl'] / latest['total_trades'] if latest['total_trades'] > 0 else 0,
            'total_pnl': latest['pnl'],
            'monthly_returns': [
                {'month': row['date'], 'return': row['pnl']}
                for row in performance[:12]
            ]
        }
    else:
        # Mock data if no real data
        performance_data = {
            'win_rate_30d': 85.5,
            'total_trades': 247,
            'winning_trades': 211,
            'losing_trades': 36,
            'average_return': 2.8,
            'total_pnl': 692.50,
            'monthly_returns': [
                {'month': 'Dec 2024', 'return': 12.4},
                {'month': 'Nov 2024', 'return': 8.7},
                {'month': 'Oct 2024', 'return': 15.2}
            ]
        }

    return jsonify(performance_data)

@app.route('/api/market-regime')
@login_required
def get_market_regime():
    """Get current market regime analysis"""
    regimes = ['Bull Market', 'Bear Market', 'Sideways', 'Breakout', 'Volatile']
    regime_data = {
        'current_regime': random.choice(regimes),
        'confidence': random.randint(75, 95),
        'duration_days': random.randint(5, 25),
        'next_change_probability': random.randint(10, 40),
        'regime_history': [
            {'regime': 'Bull', 'duration': 15, 'performance': 12.4},
            {'regime': 'Sideways', 'duration': 8, 'performance': 3.2},
            {'regime': 'Bear', 'duration': 6, 'performance': -4.1}
        ]
    }
    return jsonify(regime_data)

@app.route('/api/sessions')
@login_required
def get_sessions():
    """Get active market sessions"""
    with get_db() as conn:
        sessions = conn.execute('SELECT * FROM market_sessions').fetchall()

    sessions_data = []
    for session in sessions:
        sessions_data.append({
            'name': session['session_name'],
            'status': session['status'],
            'active_pairs': session['active_pairs'].split(',') if session['active_pairs'] else []
        })

    return jsonify({'sessions': sessions_data})

@app.route('/api/alerts')
@login_required
def get_alerts():
    """Get market alerts"""
    alerts = [
        {
            'type': 'warning',
            'title': 'High Volatility Alert',
            'message': 'BTC showing extreme volatility. Exercise caution on crypto positions.',
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat()
        },
        {
            'type': 'success',
            'title': 'Strong Signal Generated',
            'message': 'New BUY signal for EUR/USD with 92% confidence.',
            'timestamp': (datetime.now() - timedelta(minutes=12)).isoformat()
        },
        {
            'type': 'info',
            'title': 'Session Change',
            'message': 'European session now active. EUR and GBP pairs becoming more volatile.',
            'timestamp': (datetime.now() - timedelta(minutes=25)).isoformat()
        }
    ]
    return jsonify({'alerts': alerts})

@app.route('/api/correlation')
@login_required
def get_correlation():
    """Get market correlation data"""
    # Mock correlation data - replace with real calculations
    correlation_data = {
        'labels': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'BTC/USD'],
        'data': [0.85, 0.78, -0.65, 0.72, -0.45, 0.25]
    }
    return jsonify(correlation_data)

@app.route('/api/regional-performance')
@login_required
def get_regional_performance():
    """Get regional market performance"""
    regions = [
        {
            'name': 'Asia Pacific',
            'pairs': ['CNY', 'JPY', 'AUD'],
            'change_24h': 2.4,
            'status': 'bullish'
        },
        {
            'name': 'Europe',
            'pairs': ['EUR', 'GBP', 'CHF'],
            'change_24h': -1.2,
            'status': 'bearish'
        },
        {
            'name': 'Americas',
            'pairs': ['BRL', 'CAD', 'MXN'],
            'change_24h': 1.8,
            'status': 'bullish'
        },
        {
            'name': 'Crypto',
            'pairs': ['BTC', 'ETH'],
            'change_24h': 5.6,
            'status': 'volatile'
        }
    ]
    return jsonify({'regions': regions})

def format_time_ago(timestamp_str):
    """Format timestamp to time ago string"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds // 3600 > 0:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds // 60 > 0:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"
    except:
        return "Unknown"

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': 'personal_dashboard_v1.0'
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Personal Trading Dashboard...")

    # Create templates directory
    if not os.path.exists('templates'):
        os.makedirs('templates')

    app.run(
        host='0.0.0.0',
        port=5001,  # Different port from ultra premium dashboard
        debug=True,
        threaded=True
    )
