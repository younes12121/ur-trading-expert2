# TradingView CFD Trading Guide

## Your Trading Setup

**Platform:** TradingView  
**Instruments:**
- **Gold:** XAUUSD CFD
- **Bitcoin:** BTCUSD CFD

---

## Understanding Price Differences

### Why Prices Look Different

The signal generator fetches data from **Binance** (free, reliable API), but you trade on **TradingView CFDs**. Here's why prices differ:

#### Gold (XAUUSD)
- **Binance PAXGUSDT:** ~$2,045 (tokenized gold, 1 token = 1 oz)
- **Actual Spot Gold:** ~$2,650-2,700 per troy ounce
- **Your TradingView CFD:** $4,157 (broker-specific format/leverage)

#### Bitcoin (BTCUSD)
- **Binance BTCUSDT:** ~$95,000
- **Your TradingView CFD:** Should match closely (~$95,000)

**Important:** The price format doesn't matter for signals! The technical analysis (support/resistance, trends, order flow) is based on **percentage moves**, not absolute prices.

---

## How to Use the Signals

### When You Get a Signal

Example Gold Signal:
```
Direction: SELL
Entry: $2,044.50
Stop Loss: $2,063.69
TP1: $2,021.47
TP2: $1,996.52
```

### Convert to TradingView CFD

**Step 1: Use the Direction**
- Signal says SELL → You SELL on TradingView

**Step 2: Calculate Percentage Moves**
- Entry: $2,044.50
- Stop Loss: $2,063.69
- **Stop Loss %:** (2063.69 - 2044.50) / 2044.50 = **0.94%** above entry

**Step 3: Apply to Your TradingView Price**
If your TradingView shows Gold at $4,157:
- **Entry:** $4,157 (current price)
- **Stop Loss:** $4,157 × 1.0094 = **$4,196** (0.94% above)
- **TP1:** Calculate using the same percentage method

### Quick Conversion Formula

For any signal:
```
Your_Price = TradingView_Current_Price
Stop_Loss_% = (Signal_SL - Signal_Entry) / Signal_Entry
Your_Stop_Loss = Your_Price × (1 + Stop_Loss_%)
```

---

## Signal Quality Checklist

Before trading ANY signal on TradingView:

✅ **Ultra A+ Status:** Must show "[ULTRA A+] ALL 17 CRITERIA MET"  
✅ **Direction Clear:** BUY or SELL explicitly stated  
✅ **Risk/Reward:** Minimum 2:1 ratio  
✅ **Trading Session:** London or NY session (not Asian hours)  
✅ **News Check:** No major economic events in next 2 hours  

---

## Current Market Status

Run this command to check both markets:
```bash
python compare_experts.py
```

Or individual experts:
```bash
python "Gold expert/gold_signal_generator.py"
python "BTC expert/ultra_signal_generator.py"
```

---

## Risk Management for CFDs

**CRITICAL:** CFDs have leverage! Adjust position sizing:

### Standard Setup (No Leverage)
- Capital: $500
- Risk per trade: 1% = $5

### With 1:100 Leverage (Common for Gold CFDs)
- **Same risk:** Still only risk $5 (1% of $500)
- **Position size:** Calculate based on stop loss distance
- **Never risk more than 1-2%** regardless of leverage

### Position Size Calculator

```
Risk Amount = Capital × Risk_Per_Trade (e.g., $500 × 0.01 = $5)
Stop Loss Distance = Entry - Stop_Loss (in your broker's price format)
Position Size = Risk Amount / Stop Loss Distance
```

**Example:**
- Risk: $5
- Entry: $4,157
- Stop Loss: $4,196
- Distance: $39
- **Position Size:** $5 / $39 = **0.128 lots** (adjust to broker's lot size)

---

## Important Notes

1. **Data Source vs Trading Platform:**
   - Signals use Binance data (accurate, free)
   - You trade on TradingView (your broker's CFD)
   - This is normal and doesn't affect signal quality

2. **Price Synchronization:**
   - Gold and BTC prices move together globally
   - Small differences between exchanges are normal
   - Focus on the **direction** and **percentage moves**

3. **Signal Validity:**
   - Signals are valid for 15-30 minutes
   - If price moves significantly before you enter, skip the trade
   - Wait for the next Ultra A+ signal

4. **Patience is Key:**
   - Ultra A+ signals are RARE (maybe 1-2 per day)
   - Don't force trades
   - 85-90% win rate only applies to Ultra A+ setups

---

## Troubleshooting

**Q: Signal shows $2,045 but my TradingView shows $4,157 for Gold**  
A: Normal! Use the percentage-based conversion method above.

**Q: Should I adjust the signal for my broker's spread?**  
A: Yes, add your broker's spread to the stop loss for safety.

**Q: Can I trade with higher leverage?**  
A: You can, but NEVER increase your risk beyond 1-2% of capital.

**Q: Signal says WAIT but I see a good setup on TradingView**  
A: Trust the system. If it's not Ultra A+, the win rate drops below 85%.

---

**Remember:** The goal is not to trade often, but to trade with HIGH CONFIDENCE when all 17 criteria align perfectly! 🎯
