"""
Manual calculation of trading signal for BTC at $87,712
Based on BTCScalpingAnalyzer logic
"""

import math

# Current market data
btc_price = 87712.0
usd_index = 103.2
gold_price = 2045.0
oil_price = 73.5
btc_volatility = 0.038  # 3.8% daily volatility
market_sentiment = 0.72  # Bullish
volume_ratio = 1.35

print("=" * 60)
print("BTCUSD CFD SCALPING ANALYSIS - MANUAL CALCULATION")
print("=" * 60)
print(f"Current BTC Price: ${btc_price:,.2f}")
print(f"Market Sentiment: {market_sentiment} (Bullish)")
print(f"Volatility: {btc_volatility * 100:.2f}%")
print()

# 1. ALGEBRAIC PRICE MODEL
print("1. ALGEBRAIC PRICE MODEL:")
print("-" * 60)
alpha = 95000
beta = 210
gamma = 15000

predicted_price = alpha - beta * usd_index + gamma * market_sentiment
print(f"   Linear Model Price: ${predicted_price:,.2f}")

# Nonlinear volatility adjustment
vol_factor = 1 + math.tanh(btc_volatility - 0.03) * 0.1
adjusted_price = predicted_price * vol_factor
print(f"   Volatility Adjusted Price: ${adjusted_price:,.2f}")

price_deviation = (adjusted_price - btc_price) / btc_price
signal_strength = abs(price_deviation)

print(f"   Price Deviation: {price_deviation * 100:.2f}%")
print(f"   Signal Strength: {signal_strength * 100:.2f}%")

algebraic_signal = 1 if price_deviation > 0 else -1
print(f"   Algebraic Signal: {'BUY' if algebraic_signal > 0 else 'SELL'}")
print()

# 2. PROBABILISTIC ANALYSIS
print("2. PROBABILISTIC ANALYSIS:")
print("-" * 60)
mu = 0.001 * market_sentiment - 0.0005
sigma = btc_volatility / math.sqrt(24)

print(f"   Expected Return (mu): {mu * 100:.4f}%")
print(f"   Hourly Volatility (sigma): {sigma * 100:.2f}%")

# Approximate normal CDF for prob_up
z_score = -mu / sigma
# Using approximation: P(Z > z) ≈ 0.5 - 0.5*erf(z/sqrt(2))
# For simplicity, if mu > 0, prob_up > 0.5
prob_up = 0.5 + mu / (sigma * 2.5)  # Approximation
prob_down = 1 - prob_up

print(f"   Probability Up: {prob_up * 100:.1f}%")
print(f"   Probability Down: {prob_down * 100:.1f}%")

if market_sentiment > 0.7:
    current_state = "Bullish"
elif market_sentiment < 0.3:
    current_state = "Bearish"
else:
    current_state = "Neutral"

print(f"   Market State: {current_state}")

probabilistic_signal = 1 if prob_up > 0.55 else -1
print(f"   Probabilistic Signal: {'BUY' if probabilistic_signal > 0 else 'SELL'}")
print()

# 3. MONTE CARLO SIMULATION (Simplified)
print("3. MONTE CARLO SIMULATION (4-hour forecast):")
print("-" * 60)
dt = 1/24
hours = 4
# Expected price after 4 hours
expected_price_4h = btc_price * math.exp(mu * dt * hours)
price_std_4h = btc_price * sigma * math.sqrt(dt * hours)

print(f"   Expected Price (4h): ${expected_price_4h:,.2f}")
print(f"   Price Std Dev: ${price_std_4h:,.2f}")
print(f"   95% Range: ${expected_price_4h - 2*price_std_4h:,.2f} - ${expected_price_4h + 2*price_std_4h:,.2f}")

mc_signal = 1 if expected_price_4h > btc_price else -1
print(f"   Monte Carlo Signal: {'BUY' if mc_signal > 0 else 'SELL'}")
print()

# 4. COMBINED SIGNAL
print("4. COMBINED TRADING SIGNAL:")
print("-" * 60)
signal_weight = (algebraic_signal * 0.3 + 
                probabilistic_signal * 0.4 + 
                mc_signal * 0.3)

print(f"   Signal Weight: {signal_weight:.2f}")
print(f"   Algebraic: {algebraic_signal} (30%)")
print(f"   Probabilistic: {probabilistic_signal} (40%)")
print(f"   Monte Carlo: {mc_signal} (30%)")
print()

# 5. RISK MANAGEMENT
print("5. RISK MANAGEMENT:")
print("-" * 60)
capital = 300
lot_size = 0.02
risk_per_trade = 0.02

# Stop loss calculation
atr_multiplier = 1.5
stop_distance = btc_price * btc_volatility * atr_multiplier / math.sqrt(365)
risk_amount = capital * risk_per_trade

print(f"   Capital: ${capital}")
print(f"   Risk per Trade: {risk_per_trade * 100}%")
print(f"   Risk Amount: ${risk_amount:.2f}")
print(f"   Stop Distance: ${stop_distance:.2f}")
print()

# 6. FINAL TRADING DECISION
print("=" * 60)
print("FINAL TRADING RECOMMENDATION:")
print("=" * 60)

if signal_weight > 0.3:
    direction = "BUY"
    entry_price = btc_price + 5
    stop_loss = entry_price - stop_distance
    take_profit = entry_price + stop_distance * 1.5
elif signal_weight < -0.3:
    direction = "SELL"
    entry_price = btc_price - 5
    stop_loss = entry_price + stop_distance
    take_profit = entry_price - stop_distance * 1.5
else:
    direction = "HOLD"
    entry_price = btc_price
    stop_loss = None
    take_profit = None

confidence = min(95, 50 + abs(signal_weight) * 30 + signal_strength * 20)

print(f"Direction: {direction}")
print(f"Entry Price: ${entry_price:,.2f}")
if stop_loss:
    print(f"Stop Loss: ${stop_loss:,.2f}")
    print(f"Take Profit: ${take_profit:,.2f}")
else:
    print("Stop Loss: N/A")
    print("Take Profit: N/A")
print(f"Confidence: {confidence:.1f}%")
print(f"Lot Size: {lot_size}")
print()

if direction != "HOLD":
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    rr_ratio = reward / risk
    
    potential_loss = lot_size * risk
    potential_profit = lot_size * reward
    
    print("RISK-REWARD ANALYSIS:")
    print(f"Risk per unit: ${risk:.2f}")
    print(f"Reward per unit: ${reward:.2f}")
    print(f"Risk-Reward Ratio: 1:{rr_ratio:.2f}")
    print(f"Potential Loss: ${potential_loss:.2f}")
    print(f"Potential Profit: ${potential_profit:.2f}")

print()
print("=" * 60)
print("SCALPING NOTES:")
print("- Monitor 15m-1h timeframes")
print("- Consider partial profit at 50% TP")
print("- Move SL to breakeven after 30% profit")
print("=" * 60)
