"""
Trading Signal Analysis for BTC at $87,670
After pullback from $88,200 high
"""

import math

# Current market data
btc_price = 87670.0
previous_high = 88200.0
support_level = 87400.0
resistance_level = 88000.0

# Market conditions after pullback
btc_volatility = 0.042  # Increased volatility after rejection
market_sentiment = 0.58  # Neutral-bullish (pullback reduces sentiment)
volume_ratio = 1.15     # Lower volume on pullback

print("=" * 70)
print("         BTCUSD TRADING SIGNAL - PRICE: $87,670")
print("=" * 70)
print(f"Current Price:    ${btc_price:,.2f}")
print(f"Previous High:    ${previous_high:,.2f}")
print(f"Pullback:         ${previous_high - btc_price:,.2f} (-{((previous_high - btc_price)/previous_high)*100:.2f}%)")
print(f"Support Level:    ${support_level:,.2f}")
print(f"Resistance:       ${resistance_level:,.2f}")
print()

# Technical Analysis
print("TECHNICAL ANALYSIS:")
print("-" * 70)

# Price position
distance_from_support = btc_price - support_level
distance_to_resistance = resistance_level - btc_price

print(f"Distance from Support ($87,400): ${distance_from_support:,.2f}")
print(f"Distance to Resistance ($88,000): ${distance_to_resistance:,.2f}")

# Trend analysis
if btc_price > 87500:
    trend = "Bullish (above mid-range)"
    trend_signal = 1
elif btc_price < 87300:
    trend = "Bearish (below mid-range)"
    trend_signal = -1
else:
    trend = "Neutral (consolidation)"
    trend_signal = 0

print(f"Trend: {trend}")
print()

# Signal Generation
print("SIGNAL ANALYSIS:")
print("-" * 70)

# Calculate stop distance based on volatility
atr_multiplier = 1.5
stop_distance = btc_price * btc_volatility * atr_multiplier / math.sqrt(365)

print(f"ATR-based Stop Distance: ${stop_distance:.2f}")

# Determine direction
# After pullback, looking for bounce or continuation down
if btc_price > 87500 and distance_from_support > 200:
    direction = "BUY"
    bias = "Expecting bounce from pullback"
    entry_price = btc_price + 10  # Market entry with slippage
    stop_loss = entry_price - stop_distance
    tp1 = entry_price + stop_distance * 1.2
    tp2 = entry_price + stop_distance * 2.5
    confidence = 58
elif btc_price < 87400:
    direction = "SELL"
    bias = "Breakdown continuation"
    entry_price = btc_price - 10
    stop_loss = entry_price + stop_distance
    tp1 = entry_price - stop_distance * 1.2
    tp2 = entry_price - stop_distance * 2.5
    confidence = 55
else:
    direction = "WAIT"
    bias = "Price in no-trade zone, wait for breakout"
    entry_price = btc_price
    stop_loss = None
    tp1 = None
    tp2 = None
    confidence = 0

print(f"Direction: {direction}")
print(f"Bias: {bias}")
print(f"Confidence: {confidence}%")
print()

# Display Trading Setup
print("=" * 70)
print("                    TRADING SETUP")
print("=" * 70)
print(f"Direction:        {direction} {'📈' if direction == 'BUY' else '📉' if direction == 'SELL' else '⏸️'}")
print(f"Entry Price:      ${entry_price:,.2f}")

if stop_loss:
    print(f"Stop Loss:        ${stop_loss:,.2f}")
    print("-" * 70)
    print(f"TP1 (50% close):  ${tp1:,.2f}")
    print(f"TP2 (50% close):  ${tp2:,.2f}")
    print("-" * 70)
    
    # Risk-Reward Calculation
    risk = abs(entry_price - stop_loss)
    reward1 = abs(tp1 - entry_price)
    reward2 = abs(tp2 - entry_price)
    
    rr1 = reward1 / risk
    rr2 = reward2 / risk
    
    print()
    print("RISK-REWARD ANALYSIS:")
    print("-" * 70)
    print(f"Risk per unit:         ${risk:.2f}")
    print(f"Reward TP1:            ${reward1:.2f} (RR 1:{rr1:.2f})")
    print(f"Reward TP2:            ${reward2:.2f} (RR 1:{rr2:.2f})")
    print()
    
    # Position sizing (0.02 lot)
    lot_size = 0.02
    capital = 300
    
    potential_loss = lot_size * risk
    potential_profit_tp1 = lot_size * reward1
    potential_profit_tp2 = lot_size * reward2
    
    print("POSITION DETAILS (Lot Size: 0.02):")
    print("-" * 70)
    print(f"Capital:               ${capital:.2f}")
    print(f"Lot Size:              {lot_size}")
    print(f"Potential Loss:        ${potential_loss:.2f} ({(potential_loss/capital)*100:.2f}% of capital)")
    print(f"Profit at TP1 (50%):   ${potential_profit_tp1/2:.2f}")
    print(f"Profit at TP2 (50%):   ${potential_profit_tp2/2:.2f}")
    print(f"Total if both hit:     ${(potential_profit_tp1/2 + potential_profit_tp2/2):.2f}")
    print()
    
    # Trading Plan
    print("=" * 70)
    print("EXECUTION PLAN:")
    print("=" * 70)
    print(f"1. Enter {direction} at ${entry_price:,.2f}")
    print(f"2. Set Stop Loss at ${stop_loss:,.2f}")
    print(f"3. When TP1 hit (${tp1:,.2f}):")
    print(f"   - Close 50% position (0.01 lot)")
    print(f"   - Lock profit: ${potential_profit_tp1/2:.2f}")
    print(f"   - Move SL to breakeven (${entry_price:,.2f})")
    print(f"4. Let remaining 50% run to TP2 (${tp2:,.2f})")
    print(f"5. Trail stop if price moves strongly in your favor")
else:
    print("Stop Loss:        N/A")
    print("Take Profit:      N/A")
    print()
    print("⚠️  WAIT FOR BETTER SETUP")
    print("   - Watch for break above $87,750 (BUY)")
    print("   - Watch for break below $87,400 (SELL)")

print("=" * 70)
print("MARKET NOTES:")
print("-" * 70)
print("• Price pulled back from $88,200 high")
print("• Currently in consolidation zone")
print("• Key support at $87,400")
print("• Key resistance at $88,000")
print("• Watch for volume confirmation on breakout")
print("=" * 70)
