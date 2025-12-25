"""
Mobile API Handler for Telegram Mini App
Provides REST API endpoints for the mobile web app
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from signal_api import UltimateSignalAPI
    from user_manager import UserManager
    from performance_analytics import PerformanceAnalytics
    from signal_tracker import SignalTracker
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")

app = Flask(__name__)
CORS(app)  # Enable CORS for Telegram WebApp

# Initialize services
signal_api = UltimateSignalAPI()
user_manager = UserManager()
signal_tracker = SignalTracker()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "UR Trading Expert Mobile API"})


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    """Get user information and tier"""
    try:
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user_id": user_id,
            "tier": user.get('tier', 'free'),
            "name": user.get('name', 'User'),
            "joined_date": user.get('joined_date'),
            "total_signals": user.get('total_signals', 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/signals/latest', methods=['GET'])
def get_latest_signals():
    """Get latest trading signals"""
    try:
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        # Get signals for all supported assets
        assets = ['BTCUSDT', 'XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
        signals = []
        
        for asset in assets[:limit]:
            try:
                signal = signal_api.get_signal(asset, timeframe='M15')
                if signal:
                    signals.append({
                        'pair': asset,
                        'direction': signal.get('direction', 'BUY'),
                        'entry': signal.get('entry', 0),
                        'tp': signal.get('tp', 0),
                        'sl': signal.get('sl', 0),
                        'criteria': signal.get('criteria_passed', 0),
                        'timeframe': signal.get('timeframe', 'M15'),
                        'timestamp': signal.get('timestamp', ''),
                        'confidence': signal.get('confidence', 0)
                    })
            except:
                continue
        
        return jsonify({
            "signals": signals,
            "count": len(signals)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/signals/<signal_id>', methods=['GET'])
def get_signal_detail(signal_id):
    """Get detailed information about a specific signal"""
    try:
        signal = signal_tracker.get_signal_by_id(int(signal_id))
        if not signal:
            return jsonify({"error": "Signal not found"}), 404
        
        return jsonify(signal)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall trading statistics"""
    try:
        stats = signal_tracker.get_live_stats()
        weekly = signal_tracker.get_weekly_stats()
        
        return jsonify({
            "overall": {
                "total_signals": stats.get('total_signals', 0),
                "win_rate": stats.get('win_rate', 0),
                "total_pips": stats.get('total_pips', 0),
                "closed_signals": stats.get('closed_signals', 0)
            },
            "weekly": {
                "win_rate": weekly.get('win_rate', 0),
                "count": weekly.get('count', 0),
                "pips": weekly.get('pips', 0)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/<int:user_id>', methods=['GET'])
def get_user_analytics(user_id):
    """Get user-specific analytics"""
    try:
        # Mock data for now - integrate with your analytics system
        return jsonify({
            "profit_loss": "+1247.50",
            "trades_taken": 45,
            "win_rate": 68.5,
            "best_pair": "EUR/USD",
            "total_pips": 347,
            "roi": 12.4
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/education/tip', methods=['GET'])
def get_daily_tip():
    """Get a random educational tip"""
    try:
        from educational_assistant import EducationalAssistant
        edu = EducationalAssistant()
        
        user_id = request.args.get('user_id', type=int)
        category = request.args.get('category')
        
        tip = edu.get_daily_tip(user_id=user_id, category=category)
        
        return jsonify({
            "tip": tip,
            "total_tips": len(edu.trading_tips)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/assets', methods=['GET'])
def get_supported_assets():
    """Get list of supported trading assets"""
    return jsonify({
        "assets": [
            {"symbol": "BTCUSDT", "name": "Bitcoin", "type": "crypto"},
            {"symbol": "XAUUSD", "name": "Gold", "type": "commodity"},
            {"symbol": "ES", "name": "E-mini S&P 500", "type": "futures"},
            {"symbol": "NQ", "name": "E-mini NASDAQ", "type": "futures"},
            {"symbol": "EURUSD", "name": "EUR/USD", "type": "forex"},
            {"symbol": "GBPUSD", "name": "GBP/USD", "type": "forex"},
            {"symbol": "USDJPY", "name": "USD/JPY", "type": "forex"},
            {"symbol": "AUDUSD", "name": "AUD/USD", "type": "forex"},
            {"symbol": "USDCAD", "name": "USD/CAD", "type": "forex"},
            {"symbol": "NZDUSD", "name": "NZD/USD", "type": "forex"},
            {"symbol": "EURJPY", "name": "EUR/JPY", "type": "forex"},
            {"symbol": "EURGBP", "name": "EUR/GBP", "type": "forex"},
            {"symbol": "GBPJPY", "name": "GBP/JPY", "type": "forex"},
            {"symbol": "AUDJPY", "name": "AUD/JPY", "type": "forex"},
            {"symbol": "USDCHF", "name": "USD/CHF", "type": "forex"}
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"[*] Mobile API Server starting on port {port}")
    print(f"[*] Telegram Mini App API Ready")
    print(f"[*] API Endpoint: http://localhost:{port}/api")
    print(f"[*] Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

