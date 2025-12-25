"""
ULTIMATE COMPLETE SIGNAL ANALYZER
Everything you need: Signal Status + Order Book + Final Recommendation
From start to end - complete trading decision in one command
"""

import subprocess
import sys
import re
import requests
from datetime import datetime


def run_generator(script):
    """Run signal generator and get output"""
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=90
        )
        return result.stdout if result.returncode == 0 else None
    except:
        return None


def extract_signal_info(output, asset):
    """Extract all signal information"""
    if not output:
        return None
    
    info = {
        'asset': asset,
        'has_signal': False,
        'direction': 'N/A',
        'confidence': 'N/A',
        'price': 'N/A',
        'entry': 'N/A',
        'stop_loss': 'N/A',
        'tp1': 'N/A',
        'tp2': 'N/A',
        'criteria_passed': 'N/A',
        'criteria_total': 'N/A',
        'key_failures': []
    }
    
    info['has_signal'] = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output
    
    dir_match = re.search(r'Direction: (BUY|SELL|HOLD)', output)
    if dir_match:
        info['direction'] = dir_match.group(1)
    
    conf_match = re.search(r'Confidence: ([\d.]+)%', output)
    if conf_match:
        info['confidence'] = f"{conf_match.group(1)}%"
    
    price_match = re.search(r'Current Price: \$([\d,]+\.[\d]+)', output)
    if price_match:
        info['price'] = f"${price_match.group(1)}"
    
    entry_match = re.search(r'Entry: \$([\d,]+\.[\d]+)', output)
    if entry_match:
        info['entry'] = f"${entry_match.group(1)}"
    
    sl_match = re.search(r'Stop Loss: \$([\d,]+\.[\d]+)', output)
    if sl_match:
        info['stop_loss'] = f"${sl_match.group(1)}"
    
    tp1_match = re.search(r'TP1.*?: \$([\d,]+\.[\d]+)', output)
    if tp1_match:
        info['tp1'] = f"${tp1_match.group(1)}"
    
    tp2_match = re.search(r'TP2.*?: \$([\d,]+\.[\d]+)', output)
    if tp2_match:
        info['tp2'] = f"${tp2_match.group(1)}"
    
    criteria_match = re.search(r'\[NOT .*?\]\s*\((\d+)/(\d+)', output)
    if criteria_match:
        info['criteria_passed'] = criteria_match.group(1)
        info['criteria_total'] = criteria_match.group(2)
    elif info['has_signal']:
        info['criteria_passed'] = "17"
        info['criteria_total'] = "17"
    
    fail_lines = re.findall(r'\[FAIL\] (.+)', output)
    info['key_failures'] = fail_lines[:5]
    
    return info


def get_order_book_data(symbol):
    """Get order book analysis"""
    try:
        url = "https://api.binance.com/api/v3/depth"
        response = requests.get(url, params={'symbol': symbol, 'limit': 100}, timeout=10)
        data = response.json()
        
        bids = data.get('bids', [])
        asks = data.get('asks', [])
        
        total_bid = sum(float(b[1]) for b in bids)
        total_ask = sum(float(a[1]) for a in asks)
        
        imbalance = (total_bid - total_ask) / (total_bid + total_ask) * 100 if (total_bid + total_ask) > 0 else 0
        
        return {
            'bid_volume': total_bid,
            'ask_volume': total_ask,
            'imbalance': imbalance,
            'pressure': 'BUY' if imbalance > 0 else 'SELL'
        }
    except:
        return None


def print_complete_analysis():
    """Print everything - signals + order book + recommendation"""
    
    print("\n" + "="*120)
    print("ULTIMATE COMPLETE SIGNAL ANALYZER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CET')}")
    print("="*120)
    
    # Step 1: Get signals
    print("\n[STEP 1/3] Fetching ELITE signals...")
    btc_output = run_generator("elite_signal_generator.py")
    gold_output = run_generator("Gold expert/elite_signal_generator.py")
    
    btc_signal = extract_signal_info(btc_output, "BTC")
    gold_signal = extract_signal_info(gold_output, "GOLD")
    
    # Step 2: Get order book
    print("[STEP 2/3] Analyzing order book...")
    btc_orderbook = get_order_book_data('BTCUSDT')
    gold_orderbook = get_order_book_data('PAXGUSDT')
    
    print("[STEP 3/3] Generating complete analysis...\n")
    
    # Print signal comparison
    print("="*120)
    print("PART 1: SIGNAL STATUS (17 Criteria Filter)")
    print("="*120)
    
    print(f"\n{'-'*120}")
    print(f"{'METRIC':<20} | {'BTC (BITCOIN)':<45} | {'GOLD (XAU/USD)':<45}")
    print(f"{'-'*120}")
    
    if btc_signal and gold_signal:
        print(f"{'Price':<20} | {btc_signal['price']:<45} | {gold_signal['price']:<45}")
        print(f"{'Direction':<20} | {btc_signal['direction']:<45} | {gold_signal['direction']:<45}")
        print(f"{'Confidence':<20} | {btc_signal['confidence']:<45} | {gold_signal['confidence']:<45}")
        
        btc_crit = f"{btc_signal['criteria_passed']}/{btc_signal['criteria_total']}"
        gold_crit = f"{gold_signal['criteria_passed']}/{gold_signal['criteria_total']}"
        print(f"{'Criteria Passed':<20} | {btc_crit:<45} | {gold_crit:<45}")
        
        btc_status = "SIGNAL FOUND!" if btc_signal['has_signal'] else "NO SIGNAL"
        gold_status = "SIGNAL FOUND!" if gold_signal['has_signal'] else "NO SIGNAL"
        print(f"{'Signal Status':<20} | {btc_status:<45} | {gold_status:<45}")
    
    print(f"{'-'*120}")
    
    # Print order book
    print(f"\n{'='*120}")
    print("PART 2: ORDER BOOK ANALYSIS (Real-Time Market Pressure)")
    print(f"{'='*120}")
    
    print(f"\n{'-'*120}")
    print(f"{'METRIC':<20} | {'BTC':<45} | {'GOLD':<45}")
    print(f"{'-'*120}")
    
    if btc_orderbook and gold_orderbook:
        print(f"{'Bid Volume':<20} | {btc_orderbook['bid_volume']:<45.4f} | {gold_orderbook['bid_volume']:<45.4f}")
        print(f"{'Ask Volume':<20} | {btc_orderbook['ask_volume']:<45.4f} | {gold_orderbook['ask_volume']:<45.4f}")
        
        btc_imb = f"{btc_orderbook['imbalance']:+.2f}% ({btc_orderbook['pressure']} PRESSURE)"
        gold_imb = f"{gold_orderbook['imbalance']:+.2f}% ({gold_orderbook['pressure']} PRESSURE)"
        print(f"{'Order Imbalance':<20} | {btc_imb:<45} | {gold_imb:<45}")
    
    print(f"{'-'*120}")
    
    # Print key issues
    if btc_signal and gold_signal and (btc_signal['key_failures'] or gold_signal['key_failures']):
        print(f"\n{'='*120}")
        print("PART 3: KEY ISSUES (What's Missing)")
        print(f"{'='*120}")
        
        print(f"\n{'-'*120}")
        max_issues = max(len(btc_signal['key_failures']), len(gold_signal['key_failures']))
        
        if max_issues > 0:
            print(f"{'#':<5} | {'BTC ISSUES':<52} | {'GOLD ISSUES':<52}")
            print(f"{'-'*120}")
            
            for i in range(min(max_issues, 5)):
                btc_issue = btc_signal['key_failures'][i] if i < len(btc_signal['key_failures']) else ""
                gold_issue = gold_signal['key_failures'][i] if i < len(gold_signal['key_failures']) else ""
                print(f"{i+1:<5} | {btc_issue:<52} | {gold_issue:<52}")
        
        print(f"{'-'*120}")
    
    # Final recommendation
    print(f"\n{'='*120}")
    print("PART 4: FINAL RECOMMENDATION & ACTION PLAN")
    print(f"{'='*120}\n")
    
    if btc_signal and gold_signal:
        btc_has_signal = btc_signal['has_signal']
        gold_has_signal = gold_signal['has_signal']
        
        if btc_has_signal or gold_has_signal:
            print("[SIGNAL FOUND!]")
            if btc_has_signal:
                print(f"\n>>> BTC SIGNAL READY <<<")
                print(f"   Entry: {btc_signal['entry']}")
                print(f"   Stop Loss: {btc_signal['stop_loss']}")
                print(f"   TP1: {btc_signal['tp1']}")
                print(f"   TP2: {btc_signal['tp2']}")
            
            if gold_has_signal:
                print(f"\n>>> GOLD SIGNAL READY <<<")
                print(f"   Entry: {gold_signal['entry']}")
                print(f"   Stop Loss: {gold_signal['stop_loss']}")
                print(f"   TP1: {gold_signal['tp1']}")
                print(f"   TP2: {gold_signal['tp2']}")
            
            print("\nACTION: Execute trade following the setup above!")
        
        else:
            # No signals - provide detailed analysis
            print("[NO SIGNALS YET] - Detailed Analysis:\n")
            
            # Calculate progress
            btc_pct = (int(btc_signal['criteria_passed']) / int(btc_signal['criteria_total'])) * 100
            gold_pct = (int(gold_signal['criteria_passed']) / int(gold_signal['criteria_total'])) * 100
            
            print(f"SIGNAL PROGRESS:")
            print(f"   BTC:  {btc_signal['criteria_passed']}/{btc_signal['criteria_total']} ({btc_pct:.1f}%)")
            print(f"   GOLD: {gold_signal['criteria_passed']}/{gold_signal['criteria_total']} ({gold_pct:.1f}%)")
            
            # Order book analysis
            if btc_orderbook and gold_orderbook:
                print(f"\nORDER BOOK PRESSURE:")
                print(f"   BTC:  {btc_orderbook['imbalance']:+.1f}% ({btc_orderbook['pressure']} pressure)")
                print(f"   GOLD: {gold_orderbook['imbalance']:+.1f}% ({gold_orderbook['pressure']} pressure)")
            
            # Combined recommendation
            print(f"\nCOMBINED ANALYSIS:")
            
            # BTC analysis
            btc_improving = btc_orderbook and btc_orderbook['imbalance'] > 10
            print(f"\n   BTC: {btc_pct:.1f}% complete")
            if btc_improving:
                print(f"      [IMPROVING] Strong buy pressure ({btc_orderbook['imbalance']:+.1f}%)")
                print(f"      Watch closely - momentum building!")
            else:
                print(f"      [NEUTRAL] Waiting for stronger momentum")
            
            # Gold analysis
            gold_improving = gold_orderbook and gold_orderbook['imbalance'] > 10
            print(f"\n   GOLD: {gold_pct:.1f}% complete")
            if gold_improving:
                print(f"      [IMPROVING] Strong buy pressure ({gold_orderbook['imbalance']:+.1f}%)")
                print(f"      Watch closely - momentum building!")
            else:
                print(f"      [NEUTRAL] Waiting for stronger momentum")
            
            # Best opportunity
            print(f"\nRECOMMENDATION:")
            if gold_pct > btc_pct:
                print(f"   [WATCH GOLD] Closer to signal ({gold_pct:.1f}% vs {btc_pct:.1f}%)")
            elif btc_pct > gold_pct:
                print(f"   [WATCH BTC] Closer to signal ({btc_pct:.1f}% vs {gold_pct:.1f}%)")
            else:
                print(f"   [WATCH BOTH] Equal progress ({btc_pct:.1f}%)")
            
            print(f"\nACTION PLAN:")
            print(f"   1. Be patient - wait for all 17 criteria to align")
            print(f"   2. Check back in 2-4 hours")
            print(f"   3. Best times: 14:00 CET (NY Open) or 20:00 CET (NY Active)")
            print(f"   4. Run this script again: python ultimate_signal.py")
    
    print(f"\n{'='*120}\n")


if __name__ == "__main__":
    print_complete_analysis()
