"""
2-Step BTC + Gold Comparison
Step 1: Run all BTC tiers
Step 2: Run all Gold tiers
Shows results in a clean comparison table
"""

import subprocess
import sys
import re
from datetime import datetime


def extract_signal_info(output):
    """Extract key information from signal generator output"""
    criteria = "N/A"
    confidence = "N/A"
    price = "N/A"
    has_signal = False
    
    # Check for signal
    has_signal = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output or "ALL 14 CRITERIA MET" in output
    
    # Extract criteria - try multiple patterns
    match = re.search(r'\[NOT .*?\]\s*\((\d+)/(\d+)', output)
    if match:
        criteria = f"{match.group(1)}/{match.group(2)}"
    elif has_signal:
        if "ELITE" in output or "ULTRA" in output:
            criteria = "17/17"
        elif "ENHANCED" in output:
            criteria = "14/14"
        else:
            criteria = "8/8"
    
    # Extract confidence
    conf_match = re.search(r'Confidence: ([\d.]+)%', output)
    if conf_match:
        confidence = f"{conf_match.group(1)}%"
    
    # Extract price
    price_match = re.search(r'Current Price: \$([\d,]+\.[\d]+)', output)
    if price_match:
        price = f"${price_match.group(1)}"
    
    return criteria, confidence, price, has_signal


def run_tier(name, script, timeout=90):
    """Run a single tier and return results"""
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return {
                'name': name,
                'criteria': 'ERROR',
                'confidence': 'N/A',
                'price': 'N/A',
                'status': f'Exit {result.returncode}',
                'success': False
            }
        
        criteria, confidence, price, has_signal = extract_signal_info(result.stdout)
        
        return {
            'name': name,
            'criteria': criteria,
            'confidence': confidence,
            'price': price,
            'status': '[SIGNAL]' if has_signal else '[WAIT]',
            'success': True,
            'has_signal': has_signal
        }
        
    except subprocess.TimeoutExpired:
        return {
            'name': name,
            'criteria': 'ERROR',
            'confidence': 'N/A',
            'price': 'N/A',
            'status': 'Timeout',
            'success': False
        }
    except Exception as e:
        return {
            'name': name,
            'criteria': 'ERROR',
            'confidence': 'N/A',
            'price': 'N/A',
            'status': str(e)[:20],
            'success': False
        }


def print_header():
    """Print header"""
    print("\n" + "="*100)
    print("2-STEP COMPARISON - BTC vs GOLD - ALL 4 TIERS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)


def run_btc_tiers():
    """Step 1: Run all BTC tiers"""
    print("\n" + ">"*100)
    print("STEP 1: RUNNING BTC TIERS (4 generators)")
    print(">"*100)
    
    btc_tiers = [
        ("Tier 1: Original A+", "aplus_signal_generator.py"),
        ("Tier 2: Enhanced A+", "enhanced_signal_generator.py"),
        ("Tier 3: Ultra A+", "ultra_signal_generator.py"),
        ("Tier 4: ELITE A+", "elite_signal_generator.py"),
    ]
    
    results = []
    for i, (name, script) in enumerate(btc_tiers, 1):
        print(f"\n   [{i}/4] Running {name}...")
        result = run_tier(name, script)
        results.append(result)
        print(f"   [{i}/4] {name}: {result['status']}")
    
    return results


def run_gold_tiers():
    """Step 2: Run all Gold tiers"""
    print("\n" + ">"*100)
    print("STEP 2: RUNNING GOLD TIERS (4 generators)")
    print(">"*100)
    
    gold_tiers = [
        ("Tier 1: Original A+", "Gold expert/aplus_signal_generator.py"),
        ("Tier 2: Enhanced A+", "Gold expert/enhanced_signal_generator.py"),
        ("Tier 3: Ultra A+", "Gold expert/gold_signal_generator.py"),
        ("Tier 4: ELITE A+", "Gold expert/elite_signal_generator.py"),
    ]
    
    results = []
    for i, (name, script) in enumerate(gold_tiers, 1):
        print(f"\n   [{i}/4] Running {name}...")
        result = run_tier(name, script)
        results.append(result)
        print(f"   [{i}/4] {name}: {result['status']}")
    
    return results


def print_comparison_table(btc_results, gold_results):
    """Print comparison table"""
    print("\n" + "="*100)
    print("COMPARISON RESULTS")
    print("="*100)
    
    print(f"\n{'ASSET':<8} | {'TIER':<20} | {'CRITERIA':<12} | {'WIN RATE':<12} | {'CONFIDENCE':<12} | {'PRICE':<15} | {'STATUS':<15}")
    print("-"*100)
    
    win_rates = {
        'Tier 1: Original A+': '65-70%',
        'Tier 2: Enhanced A+': '75-85%',
        'Tier 3: Ultra A+': '85-90%',
        'Tier 4: ELITE A+': '90-95%'
    }
    
    # BTC rows
    for result in btc_results:
        win_rate = win_rates.get(result['name'], 'N/A')
        print(f"{'BTC':<8} | {result['name']:<20} | {result['criteria']:<12} | {win_rate:<12} | "
              f"{result['confidence']:<12} | {result['price']:<15} | {result['status']:<15}")
    
    print("-"*100)
    
    # Gold rows
    for result in gold_results:
        win_rate = win_rates.get(result['name'], 'N/A')
        print(f"{'GOLD':<8} | {result['name']:<20} | {result['criteria']:<12} | {win_rate:<12} | "
              f"{result['confidence']:<12} | {result['price']:<15} | {result['status']:<15}")
    
    print("-"*100)


def print_summary(btc_results, gold_results):
    """Print summary"""
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    
    btc_signals = sum(1 for r in btc_results if r.get('has_signal', False))
    gold_signals = sum(1 for r in gold_results if r.get('has_signal', False))
    total_signals = btc_signals + gold_signals
    
    print(f"\n[INFO] Total Signals: {total_signals}/8")
    print(f"   - BTC:  {btc_signals}/4")
    print(f"   - GOLD: {gold_signals}/4")
    
    if total_signals > 0:
        print("\n[SIGNALS FOUND]")
        for result in btc_results + gold_results:
            if result.get('has_signal'):
                asset = 'BTC' if result in btc_results else 'GOLD'
                print(f"   [SIGNAL] {asset} - {result['name']}")
    
    if total_signals == 0:
        print("\n[WAIT] No signals available right now.")
        print("   - Both BTC and Gold markets may be too quiet or choppy")
        print("   - Wait for better conditions")
        print("   - Check back in 2-4 hours (best: 14:00 or 20:00 CET)")
    elif btc_signals > 0 and gold_signals > 0:
        print("\n[RARE] Both BTC and Gold have signals!")
        print("   - Consider diversifying across both assets")
        print("   - Use highest tier signals for best win rate")
    elif btc_signals > 0:
        print("\n[BTC ONLY] BTC has signals, Gold does not")
        print("   - Focus on BTC opportunities")
    else:
        print("\n[GOLD ONLY] Gold has signals, BTC does not")
        print("   - Focus on Gold opportunities")
    
    print("\n" + "="*100)


def main():
    """Main function"""
    print_header()
    
    # Step 1: Run BTC tiers
    btc_results = run_btc_tiers()
    
    # Step 2: Run Gold tiers
    gold_results = run_gold_tiers()
    
    # Print comparison
    print_comparison_table(btc_results, gold_results)
    
    # Print summary
    print_summary(btc_results, gold_results)
    
    print("\n[DONE] 2-step comparison complete!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
