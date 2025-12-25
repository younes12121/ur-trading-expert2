"""
Forex Pip Calculator
Calculate pips, position sizes, and P&L for forex trading
"""


def calculate_pips(pair, entry, exit):
    """
    Calculate pips between entry and exit
    
    Args:
        pair: Forex pair (e.g., "EURUSD", "USDJPY")
        entry: Entry price
        exit: Exit price
    
    Returns:
        float: Number of pips
    """
    price_diff = abs(exit - entry)
    
    # JPY pairs: 1 pip = 0.01
    if "JPY" in pair.upper():
        pips = price_diff * 100
    else:
        # Standard pairs: 1 pip = 0.0001
        pips = price_diff * 10000
    
    return round(pips, 1)


def calculate_position_size(pair, account_balance, risk_percent, entry, stop_loss):
    """
    Calculate position size based on risk
    
    Args:
        pair: Forex pair
        account_balance: Account size in USD
        risk_percent: Risk percentage (e.g., 1 for 1%)
        entry: Entry price
        stop_loss: Stop loss price
    
    Returns:
        dict: {"lots": float, "units": int, "risk_amount": float}
    """
    # Calculate risk amount
    risk_amount = account_balance * (risk_percent / 100)
    
    # Calculate pips to stop loss
    sl_pips = calculate_pips(pair, entry, stop_loss)
    
    # Calculate pip value for standard lot (100,000 units)
    if "JPY" in pair.upper():
        pip_value_per_lot = 1000  # For JPY pairs
    else:
        pip_value_per_lot = 10  # For standard pairs
    
    # Calculate required lots
    if sl_pips > 0:
        lots = risk_amount / (sl_pips * pip_value_per_lot)
    else:
        lots = 0
    
    # Calculate units (1 lot = 100,000 units)
    units = int(lots * 100000)
    
    return {
        "lots": round(lots, 2),
        "units": units,
        "risk_amount": round(risk_amount, 2),
        "sl_pips": sl_pips,
        "pip_value": round(pip_value_per_lot * lots, 2)
    }


def calculate_pnl(pair, entry, exit, lots, direction="BUY"):
    """
    Calculate P&L for a trade
    
    Args:
        pair: Forex pair
        entry: Entry price
        exit: Exit price
        lots: Position size in lots
        direction: "BUY" or "SELL"
    
    Returns:
        dict: {"pips": float, "pnl_usd": float}
    """
    # Calculate pips
    pips = calculate_pips(pair, entry, exit)
    
    # Determine if profit or loss
    if direction.upper() == "BUY":
        if exit > entry:
            pips_signed = pips
        else:
            pips_signed = -pips
    else:  # SELL
        if exit < entry:
            pips_signed = pips
        else:
            pips_signed = -pips
    
    # Calculate pip value
    if "JPY" in pair.upper():
        pip_value_per_lot = 1000
    else:
        pip_value_per_lot = 10
    
    # Calculate P&L in USD
    pnl_usd = pips_signed * pip_value_per_lot * lots
    
    return {
        "pips": pips_signed,
        "pnl_usd": round(pnl_usd, 2)
    }


def get_pip_info(pair, entry, sl, tp1, tp2):
    """
    Get complete pip analysis for a trade setup
    
    Args:
        pair: Forex pair
        entry: Entry price
        sl: Stop loss price
        tp1: Take profit 1 price
        tp2: Take profit 2 price
    
    Returns:
        dict: Complete pip analysis
    """
    sl_pips = calculate_pips(pair, entry, sl)
    tp1_pips = calculate_pips(pair, entry, tp1)
    tp2_pips = calculate_pips(pair, entry, tp2)
    
    return {
        "sl_pips": sl_pips,
        "tp1_pips": tp1_pips,
        "tp2_pips": tp2_pips,
        "rr_tp1": round(tp1_pips / sl_pips, 2) if sl_pips > 0 else 0,
        "rr_tp2": round(tp2_pips / sl_pips, 2) if sl_pips > 0 else 0
    }


def format_price(pair, price):
    """Format price with correct decimal places"""
    if "JPY" in pair.upper():
        return f"{price:.3f}"
    else:
        return f"{price:.5f}"


# Example usage and testing
if __name__ == "__main__":
    print("Testing Forex Pip Calculator...")
    print("=" * 50)
    
    # Test 1: EUR/USD pips
    print("\n1. EUR/USD Pip Calculation:")
    entry = 1.10000
    exit = 1.10050
    pips = calculate_pips("EURUSD", entry, exit)
    print(f"   Entry: {entry:.5f}")
    print(f"   Exit: {exit:.5f}")
    print(f"   Pips: {pips}")
    
    # Test 2: USD/JPY pips
    print("\n2. USD/JPY Pip Calculation:")
    entry = 150.000
    exit = 150.500
    pips = calculate_pips("USDJPY", entry, exit)
    print(f"   Entry: {entry:.3f}")
    print(f"   Exit: {exit:.3f}")
    print(f"   Pips: {pips}")
    
    # Test 3: Position size calculation
    print("\n3. Position Size Calculation:")
    account = 1000
    risk_pct = 1
    entry = 1.10000
    sl = 1.09500
    
    pos_size = calculate_position_size("EURUSD", account, risk_pct, entry, sl)
    print(f"   Account: ${account}")
    print(f"   Risk: {risk_pct}%")
    print(f"   Entry: {entry:.5f}")
    print(f"   SL: {sl:.5f}")
    print(f"   Lots: {pos_size['lots']}")
    print(f"   Units: {pos_size['units']}")
    print(f"   Risk Amount: ${pos_size['risk_amount']}")
    
    # Test 4: P&L calculation
    print("\n4. P&L Calculation:")
    entry = 1.10000
    exit = 1.10100
    lots = 0.2
    
    pnl = calculate_pnl("EURUSD", entry, exit, lots, "BUY")
    print(f"   Entry: {entry:.5f}")
    print(f"   Exit: {exit:.5f}")
    print(f"   Lots: {lots}")
    print(f"   Direction: BUY")
    print(f"   Pips: {pnl['pips']}")
    print(f"   P&L: ${pnl['pnl_usd']}")
    
    # Test 5: Complete pip analysis
    print("\n5. Complete Pip Analysis:")
    entry = 1.10000
    sl = 1.09500
    tp1 = 1.10500
    tp2 = 1.11000
    
    pip_info = get_pip_info("EURUSD", entry, sl, tp1, tp2)
    print(f"   Entry: {entry:.5f}")
    print(f"   SL: {sl:.5f} ({pip_info['sl_pips']} pips)")
    print(f"   TP1: {tp1:.5f} ({pip_info['tp1_pips']} pips, R:R 1:{pip_info['rr_tp1']})")
    print(f"   TP2: {tp2:.5f} ({pip_info['tp2_pips']} pips, R:R 1:{pip_info['rr_tp2']})")
    
    print("\n" + "=" * 50)
    print("✅ Pip Calculator working!")
