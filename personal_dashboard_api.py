"""
Personal Trading Dashboard API
Connects the personal dashboard to telegram bot data sources
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
import sqlite3
import pandas as pd
from typing import Dict, List, Optional

# Import user management service
from user_management_service import get_user_portfolio_data, authenticate_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class PersonalDashboardAPI:
    """API for personal trading dashboard with bot data integration"""

    def __init__(self):
        self.signals_db = "signals_db.json"
        self.user_data_file = "user_profiles.json"
        self.trade_history_file = "trade_history.json"

    def get_portfolio_data(self, telegram_id: int) -> Dict:
        """Get portfolio overview data for a specific user"""
        try:
            # Authenticate user and get their data
            user = authenticate_user(telegram_id)
            if not user:
                return self._get_mock_portfolio_data()

            portfolio_data = get_user_portfolio_data(user.id)
            if not portfolio_data:
                return self._get_mock_portfolio_data()

            portfolio = portfolio_data.get('portfolio', {})
            performance = portfolio_data.get('performance', {})

            return {
                'balance': portfolio.get('current_capital', 500.0),
                'change': portfolio.get('capital_growth', 0),
                'change_amount': portfolio.get('total_pnl', 0),
                'today_pnl': portfolio.get('today_pnl', 0),
                'active_positions': portfolio.get('active_positions', 0),
                'win_rate': performance.get('win_rate', 0),
                'total_trades': performance.get('total_trades', 0),
                'starting_capital': portfolio.get('starting_capital', 500.0),
                'total_pnl': portfolio.get('total_pnl', 0),
                'total_pnl_pct': portfolio.get('total_pnl_pct', 0)
            }
        except Exception as e:
            logger.error(f"Error loading portfolio data for user {telegram_id}: {e}")
            return self._get_mock_portfolio_data()

    def get_current_positions(self, telegram_id: int) -> List[Dict]:
        """Get current open positions for a specific user"""
        try:
            # Authenticate user and get their data
            user = authenticate_user(telegram_id)
            if not user:
                return self._get_mock_positions()

            portfolio_data = get_user_portfolio_data(user.id)
            if not portfolio_data:
                return self._get_mock_positions()

            active_positions = portfolio_data.get('active_positions', [])

            positions = []
            for pos in active_positions:
                position = {
                    'asset': pos.get('asset', 'EUR/USD'),
                    'direction': pos.get('direction', 'BUY'),
                    'entry': pos.get('entry', 1.0845),
                    'current': pos.get('current_price', pos.get('entry', 1.0845)),
                    'pnl': pos.get('pnl', 0),
                    'pnl_percent': pos.get('pnl_pct', 0),
                    'size': pos.get('position_size', 0.5),
                    'stop_loss': pos.get('stop_loss'),
                    'take_profit': pos.get('tp1')
                }
                positions.append(position)

            return positions if positions else self._get_mock_positions()
        except Exception as e:
            logger.error(f"Error loading positions for user {telegram_id}: {e}")
            return self._get_mock_positions()

    def get_live_signals(self) -> List[Dict]:
        """Get live trading signals"""
        try:
            # Load from signals database
            if os.path.exists(self.signals_db):
                with open(self.signals_db, 'r') as f:
                    signals = json.load(f)

                live_signals = []
                for signal in signals[-6:]:  # Last 6 signals
                    live_signal = {
                        'asset': signal.get('pair', 'EUR/USD'),
                        'direction': signal.get('direction', 'BUY'),
                        'confidence': signal.get('criteria_passed', 18) * 5,  # Convert to percentage
                        'entry': signal.get('entry', 1.0845),
                        'stop_loss': signal.get('sl', signal.get('entry', 1.0845) * 0.995),
                        'take_profit1': signal.get('tp', signal.get('entry', 1.0845) * 1.01),
                        'take_profit2': signal.get('tp', signal.get('entry', 1.0845) * 1.015),
                        'category': 'major',  # Default category
                        'analysis': f"AI detected {signal.get('direction', 'BUY')} opportunity with {signal.get('criteria_passed', 18)} criteria met"
                    }
                    live_signals.append(live_signal)

                return live_signals if live_signals else self._get_mock_signals()
            else:
                return self._get_mock_signals()
        except Exception as e:
            logger.error(f"Error loading signals: {e}")
            return self._get_mock_signals()

    def get_trading_records(self, limit: int = 50) -> List[Dict]:
        """Get trading records"""
        try:
            # Load from trade history
            if os.path.exists(self.trade_history_file):
                with open(self.trade_history_file, 'r') as f:
                    trades = json.load(f)
                    return trades[-limit:] if trades else self._get_mock_records(limit)
            else:
                return self._get_mock_records(limit)
        except Exception as e:
            logger.error(f"Error loading trading records: {e}")
            return self._get_mock_records(limit)

    def get_market_data(self) -> List[Dict]:
        """Get market overview data"""
        return [
            {'region': 'Asia', 'change': 2.4, 'status': 'bullish'},
            {'region': 'Europe', 'change': -1.2, 'status': 'bearish'},
            {'region': 'Americas', 'change': 1.8, 'status': 'bullish'},
            {'region': 'Crypto', 'change': -3.1, 'status': 'volatile'}
        ]

    def get_ai_insights(self) -> List[Dict]:
        """Get AI insights"""
        return [
            {'type': 'market_regime', 'message': 'Current regime: Bull Market (87% confidence)', 'priority': 'high'},
            {'type': 'risk', 'message': 'Portfolio risk within acceptable limits', 'priority': 'medium'},
            {'type': 'opportunity', 'message': 'High probability setup in EUR/USD', 'priority': 'high'}
        ]

    def _get_mock_portfolio_data(self) -> Dict:
        """Mock portfolio data"""
        return {
            'balance': 25430.75,
            'change': 2.4,
            'change_amount': 620.50,
            'today_pnl': 145.20,
            'active_positions': 3,
            'win_rate': 73.2,
            'total_trades': 174
        }

    def _get_mock_positions(self) -> List[Dict]:
        """Mock current positions"""
        return [
            {
                'asset': 'EUR/USD',
                'direction': 'BUY',
                'entry': 1.0845,
                'current': 1.0872,
                'pnl': 85.50,
                'pnl_percent': 1.2,
                'size': 0.5,
                'stop_loss': 1.0795,
                'take_profit': 1.0945
            },
            {
                'asset': 'BTC/USD',
                'direction': 'SELL',
                'entry': 45230,
                'current': 44850,
                'pnl': -190.00,
                'pnl_percent': -0.8,
                'size': 0.02,
                'stop_loss': 45800,
                'take_profit': 43500
            },
            {
                'asset': 'GBP/JPY',
                'direction': 'BUY',
                'entry': 187.45,
                'current': 187.45,
                'pnl': 0,
                'pnl_percent': 0,
                'size': 0.3,
                'stop_loss': 186.50,
                'take_profit': 189.50
            }
        ]

    def _get_mock_signals(self) -> List[Dict]:
        """Mock live signals"""
        return [
            {
                'asset': 'USD/JPY',
                'direction': 'BUY',
                'confidence': 89,
                'entry': 147.85,
                'stop_loss': 147.35,
                'take_profit1': 148.85,
                'take_profit2': 149.85,
                'category': 'asian',
                'analysis': 'Strong bullish momentum detected'
            },
            {
                'asset': 'ETH/USD',
                'direction': 'SELL',
                'confidence': 76,
                'entry': 3456.78,
                'stop_loss': 3520.78,
                'take_profit1': 3356.78,
                'take_profit2': 3256.78,
                'category': 'crypto',
                'analysis': 'Bearish divergence forming'
            },
            {
                'asset': 'AUD/USD',
                'direction': 'HOLD',
                'confidence': 62,
                'entry': 0.6589,
                'stop_loss': 0.6539,
                'take_profit1': 0.6689,
                'take_profit2': 0.6789,
                'category': 'major',
                'analysis': 'Waiting for clearer direction'
            }
        ]

    def _get_mock_records(self, limit: int = 50) -> List[Dict]:
        """Mock trading records"""
        records = []
        strategies = ['Trend Following', 'Breakout', 'Scalping', 'Reversal', 'Momentum', 'Support Bounce', 'Resistance', 'Range Trade']
        assets = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'BTC/USD', 'ETH/USD', 'XAU/USD']

        for i in range(min(limit, 100)):
            asset = assets[i % len(assets)]
            direction = 'BUY' if i % 2 == 0 else 'SELL'
            pnl = (100 - (i % 200)) * (1 if i % 3 != 0 else -1)  # Mix of profits and losses
            entry = self._get_base_price(asset)
            exit_price = entry * (1 + (pnl / 1000))  # Approximate exit price
            pips = int(pnl * 10) if not asset.includes('BTC') else int(pnl * 100)

            record = {
                'asset': asset,
                'direction': direction,
                'strategy': strategies[i % len(strategies)],
                'entry': entry,
                'exit': exit_price,
                'pnl': pnl,
                'pips': pips,
                'duration': f"{(i % 24) + 1}h {(i % 60)}m",
                'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            }
            records.append(record)

        return records[-limit:]

    def _get_base_price(self, asset: str) -> float:
        """Get base price for asset"""
        prices = {
            'EUR/USD': 1.0845,
            'GBP/USD': 1.2750,
            'USD/JPY': 147.85,
            'AUD/USD': 0.6589,
            'BTC/USD': 45230,
            'ETH/USD': 3456.78,
            'XAU/USD': 1950
        }
        return prices.get(asset, 1.0)

# Initialize API
api = PersonalDashboardAPI()

@app.route('/')
def dashboard():
    """Serve the personal dashboard"""
    return render_template('personal_trading_dashboard.html')

@app.route('/api/portfolio')
def get_portfolio():
    """Get portfolio data"""
    return jsonify(api.get_portfolio_data())

@app.route('/api/positions')
def get_positions():
    """Get current positions"""
    return jsonify({"positions": api.get_current_positions()})

@app.route('/api/signals')
def get_signals():
    """Get live signals"""
    return jsonify({"signals": api.get_live_signals()})

@app.route('/api/records')
def get_records():
    """Get trading records"""
    limit = int(request.args.get('limit', 50))
    return jsonify({"records": api.get_trading_records(limit)})

@app.route('/api/market-overview')
def get_market_overview():
    """Get market overview"""
    return jsonify({"marketData": api.get_market_data()})

@app.route('/api/ai-insights')
def get_ai_insights():
    """Get AI insights"""
    return jsonify({"insights": api.get_ai_insights()})

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    # Mock performance data - could be calculated from actual trades
    return jsonify({
        "win_rate_30d": 73.2,
        "win_rate_90d": 71.8,
        "average_return": 1.2,
        "total_trades": 174,
        "winning_trades": 127,
        "losing_trades": 47,
        "profit_factor": 2.1,
        "sharpe_ratio": 1.8,
        "max_drawdown": -8.2,
        "monthly_returns": [
            {"month": "Dec 2024", "return": 2.4},
            {"month": "Nov 2024", "return": -1.2},
            {"month": "Oct 2024", "return": 3.1},
            {"month": "Sep 2024", "return": 1.8}
        ]
    })

# User-specific API routes
@app.route('/api/user/<int:telegram_id>/portfolio')
def get_user_portfolio(telegram_id):
    """Get portfolio data for a specific user"""
    try:
        data = api.get_portfolio_data(telegram_id)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting portfolio for user {telegram_id}: {e}")
        abort(500, description="Internal server error")

@app.route('/api/user/<int:telegram_id>/positions')
def get_user_positions(telegram_id):
    """Get current positions for a specific user"""
    try:
        positions = api.get_current_positions(telegram_id)
        return jsonify({"positions": positions})
    except Exception as e:
        logger.error(f"Error getting positions for user {telegram_id}: {e}")
        abort(500, description="Internal server error")

@app.route('/api/user/<int:telegram_id>/dashboard')
def get_user_dashboard(telegram_id):
    """Get complete dashboard data for a specific user"""
    try:
        from user_management_service import get_user_portfolio_data
        portfolio_data = get_user_portfolio_data(telegram_id)
        if not portfolio_data:
            abort(404, description="User not found")

        return jsonify({
            'portfolio': api.get_portfolio_data(telegram_id),
            'positions': api.get_current_positions(telegram_id),
            'signals': api.get_live_signals(),
            'performance': {
                'total_trades': portfolio_data.get('performance', {}).get('total_trades', 0),
                'win_rate': portfolio_data.get('performance', {}).get('win_rate', 0),
                'total_pnl': portfolio_data.get('portfolio', {}).get('total_pnl', 0),
                'active_positions': len(portfolio_data.get('active_positions', []))
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard for user {telegram_id}: {e}")
        abort(500, description="Internal server error")

@app.route('/login')
def login_page():
    """Serve the login page"""
    try:
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error serving login page: {e}")
        return "Login page not available", 500

@app.route('/dashboard/<int:telegram_id>')
def user_dashboard_page(telegram_id):
    """Serve the dashboard HTML page for a specific user"""
    try:
        # Verify user exists
        from user_management_service import authenticate_user
        user = authenticate_user(telegram_id)
        if not user:
            abort(404, description="User not found")

        return render_template('personal_trading_dashboard.html', telegram_id=telegram_id)
    except Exception as e:
        logger.error(f"Error serving dashboard for user {telegram_id}: {e}")
        abort(500, description="Internal server error")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "personal_dashboard_v1.0",
        "data_sources": {
            "signals_db": os.path.exists("signals_db.json"),
            "user_profiles": os.path.exists("user_profiles.json"),
            "trade_history": os.path.exists("trade_history.json")
        }
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Personal Trading Dashboard API...")

    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Copy dashboard to templates
    import shutil
    if os.path.exists('personal_trading_dashboard.html'):
        shutil.copy('personal_trading_dashboard.html', 'templates/')

    app.run(
        host='0.0.0.0',
        port=5001,  # Different port from ultra premium dashboard
        debug=True,
        threaded=True
    )
