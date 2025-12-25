"""
Simplified BTC Trading Signal Generator
Works without external dependencies (except requests which is built-in)
"""

import json
from datetime import datetime
try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False

def get_btc_price():
    """Get current BTC price from Binance"""
    if not HAS_REQUESTS:
        print("⚠️  'requests' module not available. Using fallback price.")
        return 86000.0
    
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"⚠️  Error fetching price: {e}")
        return 86000.0

def get_24h_stats():
    """Get 24-hour statistics"""
    if not HAS_REQUESTS:
        return None
    
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        params = {"symbol": "BTCUSDT"}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        return {
            'high': float(data['highPrice']),
            'low': float(data['lowPrice']),
            'change_pct': float(data['priceChangePercent']),
            'volume': float(data['volume'])
        }
    except:
        return None

def calculate_signal(price, capital=500, risk_pct=0.01):
    """Calculate trading signal with two TPs"""
    
    # Simple volatility estimate (3.5% for BTC)
    volatility = 0.035
    
    # Calculate stop distance (1.5 ATR)
    stop_distance = price * volatility * 1.5 / (365 ** 0.5)
    
    # Risk management
    risk_amount = capital * risk_pct
    lot_size = risk_amount / stop_distance
    
    # Simple momentum signal (you'd use the full analyzer for real trading)
    # For demo, we'll assume a bullish bias if price > 85000
    if price > 85000:
        direction = "BUY"
        entry = price + 10
        stop_loss = entry - stop_distance
        tp1 = entry + stop_distance * 1.2
        tp2 = entry + stop_distance * 2.5
        confidence = 65
    else:
        direction = "SELL"
        entry = price - 10
        stop_loss = entry + stop_distance
        tp1 = entry - stop_distance * 1.2
        tp2 = entry - stop_distance * 2.5
        confidence = 60
    
    # Calculate profits
    risk = abs(entry - stop_loss)
    reward1 = abs(tp1 - entry)
    reward2 = abs(tp2 - entry)
    
    profit_tp1 = lot_size * reward1 / 2
    profit_tp2 = lot_size * reward2 / 2
    total_profit = profit_tp1 + profit_tp2
    
    potential_loss = lot_size * risk
    
    return {
        'direction': direction,
        'entry': entry,
        'stop_loss': stop_loss,
        'tp1': tp1,
        'tp2': tp2,
        'confidence': confidence,
        'lot_size': round(lot_size, 3),
        'risk_amount': risk_amount,
        'profit_tp1': profit_tp1,
        'profit_tp2': profit_tp2,
        'total_profit': total_profit,
        'potential_loss': potential_loss,
        'rr1': reward1 / risk,
        'rr2': reward2 / risk
    }

def main():
    print("=" * 70)
    print("🚀 BTC TRADING SIGNAL GENERATOR (LIVE DATA)")
    print("=" * 70)
    print()
    
    # Get current price
    print("📊 Fetching live BTC price from Binance...")
    price = get_btc_price()
    print(f"✅ Current BTC Price: ${price:,.2f}")
    print()
    
    # Get 24h stats
    stats = get_24h_stats()
    if stats:
        print("📈 24-Hour Statistics:")
        print(f"   High: ${stats['high']:,.2f}")
        print(f"   Low: ${stats['low']:,.2f}")
        print(f"   Change: {stats['change_pct']:+.2f}%")
        print(f"   Volume: {stats['volume']:,.2f} BTC")
        print()
    
    # Generate signal
    print("🎯 Generating Trading Signal...")
    signal = calculate_signal(price, capital=500, risk_pct=0.01)
    print()
    
    # Display signal
    print("=" * 70)
    print("TRADING SIGNAL")
    print("=" * 70)
    print(f"Timestamp:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Direction:        {signal['direction']} {'📈' if signal['direction'] == 'BUY' else '📉'}")
    print(f"Confidence:       {signal['confidence']}%")
    print()
    print("ENTRY & EXIT LEVELS:")
    print("-" * 70)
    print(f"Entry Price:      ${signal['entry']:,.2f}")
    print(f"Stop Loss:        ${signal['stop_loss']:,.2f}")
    print(f"TP1 (50%):        ${signal['tp1']:,.2f}")
    print(f"TP2 (50%):        ${signal['tp2']:,.2f}")
    print()
    print("POSITION DETAILS:")
    print("-" * 70)
    print(f"Capital:          $500")
    print(f"Lot Size:         {signal['lot_size']}")
    print(f"Risk Amount:      ${signal['risk_amount']:.2f} (1% of capital)")
    print()
    print("PROFIT/LOSS POTENTIAL:")
    print("-" * 70)
    print(f"Potential Loss:   ${signal['potential_loss']:.2f}")
    print(f"Profit at TP1:    ${signal['profit_tp1']:.2f} (close 50%)")
    print(f"Profit at TP2:    ${signal['profit_tp2']:.2f} (close 50%)")
    print(f"Total Profit:     ${signal['total_profit']:.2f} (if both TPs hit)")
    print()
    print("RISK-REWARD RATIOS:")
    print("-" * 70)
    print(f"TP1 R/R:          1:{signal['rr1']:.2f}")
    print(f"TP2 R/R:          1:{signal['rr2']:.2f}")
    print()
    print("=" * 70)
    print("EXECUTION PLAN:")
    print("=" * 70)
    print(f"1. Enter {signal['direction']} at ${signal['entry']:,.2f}")
    print(f"2. Set Stop Loss at ${signal['stop_loss']:,.2f}")
    print(f"3. When TP1 hits (${signal['tp1']:,.2f}):")
    print(f"   - Close 50% of position")
    print(f"   - Lock in ${signal['profit_tp1']:.2f} profit")
    print(f"   - Move SL to breakeven")
    print(f"4. Let remaining 50% run to TP2 (${signal['tp2']:,.2f})")
    print(f"5. Total profit if both hit: ${signal['total_profit']:.2f}")
    print("=" * 70)
    print()
    print("✅ Signal generated successfully!")
    print()
    print("⚠️  NOTE: This is a simplified demo. For full analysis with")
    print("   Monte Carlo simulation and probabilistic models, install")
    print("   the required packages and run btc_analyzer_v2.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
