"""
Complete Signal Summary - Everything You Need in One Shot
Shows all critical information for immediate trading decision
"""

import subprocess
import sys
import re
from datetime import datetime


def run_generator(script):
    """Run generator and get full output"""
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


def extract_complete_info(output, asset):
    """Extract ALL information from signal output"""
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
        'risk_reward': 'N/A',
        'news_safe': False,
        'key_failures': []
    }
    
    # Check for signal
    info['has_signal'] = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output
    
    # Extract direction
    dir_match = re.search(r'Direction: (BUY|SELL|HOLD)', output)
    if dir_match:
        info['direction'] = dir_match.group(1)
    
    # Extract confidence
    conf_match = re.search(r'Confidence: ([\d.]+)%', output)
    if conf_match:
        info['confidence'] = f"{conf_match.group(1)}%"
    
    # Extract price
    price_match = re.search(r'Current Price: \$([\d,]+\.[\d]+)', output)
    if price_match:
        info['price'] = f"${price_match.group(1)}"
    
    # Extract trade details
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
    
    # Extract criteria
    criteria_match = re.search(r'\[NOT .*?\]\s*\((\d+)/(\d+)', output)
    if criteria_match:
        info['criteria_passed'] = criteria_match.group(1)
        info['criteria_total'] = criteria_match.group(2)
    elif info['has_signal']:
        info['criteria_passed'] = "17"
        info['criteria_total'] = "17"
    
    # Extract R:R
    rr_match = re.search(r'R:R \(1:([\d.]+)\)', output)
    if rr_match:
        info['risk_reward'] = f"1:{rr_match.group(1)}"
    
    # Check news
    info['news_safe'] = "No major news" in output or "[OK] No major news" in output
    
    # Extract failures
    fail_lines = re.findall(r'\[FAIL\] (.+)', output)
    info['key_failures'] = fail_lines[:5]  # Top 5 failures
    
    return info


def print_complete_summary(btc_info, gold_info):
    """Print everything in clean tables"""
    print("\n" + "="*120)
    print("COMPLETE SIGNAL SUMMARY - BTC vs GOLD")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CET')}")
    print("="*120)
    
    # Main comparison table
    print("\n" + "-"*120)
    print(f"{'METRIC':<20} | {'BTC (BITCOIN)':<45} | {'GOLD (XAU/USD)':<45}")
    print("-"*120)
    
    if btc_info and gold_info:
        # Price
        print(f"{'Price':<20} | {btc_info['price']:<45} | {gold_info['price']:<45}")
        
        # Direction
        print(f"{'Direction':<20} | {btc_info['direction']:<45} | {gold_info['direction']:<45}")
        
        # Confidence
        btc_conf = btc_info['confidence']
        gold_conf = gold_info['confidence']
        print(f"{'Confidence':<20} | {btc_conf:<45} | {gold_conf:<45}")
        
        # Criteria
        btc_crit = f"{btc_info['criteria_passed']}/{btc_info['criteria_total']}"
        gold_crit = f"{gold_info['criteria_passed']}/{gold_info['criteria_total']}"
        print(f"{'Criteria Passed':<20} | {btc_crit:<45} | {gold_crit:<45}")
        
        # Signal status
        btc_status = "SIGNAL FOUND!" if btc_info['has_signal'] else "NO SIGNAL"
        gold_status = "SIGNAL FOUND!" if gold_info['has_signal'] else "NO SIGNAL"
        print(f"{'Status':<20} | {btc_status:<45} | {gold_status:<45}")
        
        print("-"*120)
        
        # Trade setup table (if signal exists)
        if btc_info['has_signal'] or gold_info['has_signal']:
            print("\n" + "-"*120)
            print("TRADE SETUP")
            print("-"*120)
            print(f"{'LEVEL':<20} | {'BTC':<45} | {'GOLD':<45}")
            print("-"*120)
            
            if btc_info['has_signal']:
                print(f"{'Entry':<20} | {btc_info['entry']:<45} | {gold_info['entry'] if gold_info['has_signal'] else 'N/A':<45}")
                print(f"{'Stop Loss':<20} | {btc_info['stop_loss']:<45} | {gold_info['stop_loss'] if gold_info['has_signal'] else 'N/A':<45}")
                print(f"{'TP1 (50%)':<20} | {btc_info['tp1']:<45} | {gold_info['tp1'] if gold_info['has_signal'] else 'N/A':<45}")
                print(f"{'TP2 (50%)':<20} | {btc_info['tp2']:<45} | {gold_info['tp2'] if gold_info['has_signal'] else 'N/A':<45}")
                print(f"{'Risk:Reward':<20} | {btc_info['risk_reward']:<45} | {gold_info['risk_reward'] if gold_info['has_signal'] else 'N/A':<45}")
            elif gold_info['has_signal']:
                print(f"{'Entry':<20} | {'N/A':<45} | {gold_info['entry']:<45}")
                print(f"{'Stop Loss':<20} | {'N/A':<45} | {gold_info['stop_loss']:<45}")
                print(f"{'TP1 (50%)':<20} | {'N/A':<45} | {gold_info['tp1']:<45}")
                print(f"{'TP2 (50%)':<20} | {'N/A':<45} | {gold_info['tp2']:<45}")
                print(f"{'Risk:Reward':<20} | {'N/A':<45} | {gold_info['risk_reward']:<45}")
            
            print("-"*120)
        
        # Key issues table
        print("\n" + "-"*120)
        print("KEY ISSUES (What's Missing)")
        print("-"*120)
        
        max_issues = max(len(btc_info['key_failures']), len(gold_info['key_failures']))
        
        if max_issues > 0:
            print(f"{'#':<5} | {'BTC ISSUES':<52} | {'GOLD ISSUES':<52}")
            print("-"*120)
            
            for i in range(max_issues):
                btc_issue = btc_info['key_failures'][i] if i < len(btc_info['key_failures']) else ""
                gold_issue = gold_info['key_failures'][i] if i < len(gold_info['key_failures']) else ""
                print(f"{i+1:<5} | {btc_issue:<52} | {gold_issue:<52}")
        else:
            print("No issues - both assets have signals!")
        
        print("-"*120)
    
    # Summary
    print("\n" + "="*120)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*120)
    
    if btc_info and gold_info:
        btc_signal = btc_info['has_signal']
        gold_signal = gold_info['has_signal']
        
        if btc_signal and gold_signal:
            print("\n[RARE] BOTH BTC AND GOLD HAVE SIGNALS!")
            print("   - Consider diversifying across both assets")
            print("   - Use highest tier signals for best win rate")
        elif btc_signal:
            print("\n[BTC SIGNAL] Bitcoin signal available")
            print("   - Focus on BTC trade")
            print("   - Follow execution checklist")
        elif gold_signal:
            print("\n[GOLD SIGNAL] Gold signal available")
            print("   - Focus on Gold trade")
            print("   - Follow execution checklist")
        else:
            print("\n[NO SIGNALS] Wait for better conditions")
            
            # Progress comparison
            btc_pct = (int(btc_info['criteria_passed']) / int(btc_info['criteria_total'])) * 100
            gold_pct = (int(gold_info['criteria_passed']) / int(gold_info['criteria_total'])) * 100
            
            print(f"\nPROGRESS:")
            print(f"   BTC:  {btc_info['criteria_passed']}/{btc_info['criteria_total']} ({btc_pct:.1f}%)")
            print(f"   GOLD: {gold_info['criteria_passed']}/{gold_info['criteria_total']} ({gold_pct:.1f}%)")
            
            if gold_pct > btc_pct:
                print(f"\n[WATCH GOLD] Closer to signal ({gold_pct:.1f}% complete)")
            elif btc_pct > gold_pct:
                print(f"\n[WATCH BTC] Closer to signal ({btc_pct:.1f}% complete)")
            else:
                print(f"\n[EQUAL] Both at {btc_pct:.1f}% - watch both")
            
            print("\nWHAT TO DO:")
            print("   - Be patient - wait for all criteria to align")
            print("   - Check back in 2-4 hours")
            print("   - Best times: 14:00 CET (NY Open) or 20:00 CET (NY Active)")
        
        # News safety
        print(f"\nNEWS CHECK:")
        btc_news = "SAFE" if btc_info['news_safe'] else "CAUTION"
        gold_news = "SAFE" if gold_info['news_safe'] else "CAUTION"
        print(f"   BTC:  {btc_news}")
        print(f"   GOLD: {gold_news}")
    
    print("\n" + "="*120 + "\n")


def main():
    """Main function"""
    print("\n[INFO] Fetching complete signal data...")
    print("This will take ~60 seconds...\n")
    
    # Run both ELITE generators
    print("[1/2] Checking BTC ELITE...")
    btc_output = run_generator("elite_signal_generator.py")
    
    print("[2/2] Checking GOLD ELITE...")
    gold_output = run_generator("Gold expert/elite_signal_generator.py")
    
    # Extract all information
    btc_info = extract_complete_info(btc_output, "BTC")
    gold_info = extract_complete_info(gold_output, "GOLD")
    
    # Print complete summary
    print_complete_summary(btc_info, gold_info)


if __name__ == "__main__":
    main()
