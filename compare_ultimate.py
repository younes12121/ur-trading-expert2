"""
ULTIMATE Multi-Asset Multi-Tier Comparison
Checks BTC and Gold across all 4 tiers simultaneously
Total: 8 signal generators (4 BTC + 4 Gold)
"""

import subprocess
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_signal_generator(asset, tier_name, script_path):
    """
    Run a single signal generator and capture output
    Returns: dict with results
    """
    try:
        # Use current directory as working directory for all scripts
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=90,  # Increased timeout
            cwd=os.getcwd()  # Use current directory
        )
        
        output = result.stdout
        error_output = result.stderr
        
        # Check for errors
        if result.returncode != 0:
            return {
                'asset': asset,
                'tier': tier_name,
                'success': False,
                'error': f'Exit code {result.returncode}',
                'has_signal': False,
                'criteria_passed': 'N/A',
                'confidence': 'N/A',
                'price': 'N/A',
                'debug_stderr': error_output[:100] if error_output else 'No stderr'
            }
        
        # Parse key information
        has_signal = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output or "ALL 14 CRITERIA MET" in output
        
        # Extract criteria passed - try multiple patterns
        criteria_passed = "N/A"
        import re
        # Pattern 1: (4/8 criteria passed)
        match = re.search(r'\((\d+)/(\d+) criteria passed\)', output)
        if match:
            criteria_passed = f"{match.group(1)}/{match.group(2)}"
        # Pattern 2: [NOT A+] or [NOT ULTRA A+] etc.
        elif "[NOT" in output:
            # Try to find the criteria count in the output
            match2 = re.search(r'\[NOT .*?\]\s*\((\d+)/(\d+)', output)
            if match2:
                criteria_passed = f"{match2.group(1)}/{match2.group(2)}"
        elif has_signal:
            if "ELITE" in tier_name or "Ultra" in tier_name:
                criteria_passed = "17/17"
            elif "Enhanced" in tier_name:
                criteria_passed = "14/14"
            else:
                criteria_passed = "8/8"
        
        # Extract confidence
        confidence = "N/A"
        conf_match = re.search(r'Confidence: ([\d.]+)%', output)
        if conf_match:
            confidence = f"{conf_match.group(1)}%"
        
        # Extract price
        price = "N/A"
        price_match = re.search(r'Current Price: \$([\d,]+\.[\d]+)', output)
        if price_match:
            price = f"${price_match.group(1)}"
        
        return {
            'asset': asset,
            'tier': tier_name,
            'success': True,
            'has_signal': has_signal,
            'criteria_passed': criteria_passed,
            'confidence': confidence,
            'price': price
        }
        
    except subprocess.TimeoutExpired:
        return {
            'asset': asset,
            'tier': tier_name,
            'success': False,
            'error': 'Timeout',
            'has_signal': False,
            'criteria_passed': 'N/A',
            'confidence': 'N/A',
            'price': 'N/A'
        }
    except Exception as e:
        return {
            'asset': asset,
            'tier': tier_name,
            'success': False,
            'error': str(e)[:30],
            'has_signal': False,
            'criteria_passed': 'N/A',
            'confidence': 'N/A',
            'price': 'N/A'
        }


def print_header():
    """Print comparison header"""
    print("\n" + "=" * 140)
    print("ULTIMATE COMPARISON - BTC vs GOLD - ALL 4 TIERS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 140)


def print_comparison_table(btc_results, gold_results):
    """Print results in a nice table"""
    print("\n" + "=" * 140)
    print("COMPARISON RESULTS")
    print("=" * 140)
    
    # Header
    print(f"\n{'ASSET':<8} | {'TIER':<20} | {'CRITERIA':<12} | {'WIN RATE':<12} | {'CONFIDENCE':<12} | {'PRICE':<15} | {'STATUS':<15}")
    print("-" * 140)
    
    tier_info = {
        'Tier 1: Original A+': {'win_rate': '65-70%'},
        'Tier 2: Enhanced A+': {'win_rate': '75-85%'},
        'Tier 3: Ultra A+': {'win_rate': '85-90%'},
        'Tier 4: ELITE A+': {'win_rate': '90-95%'}
    }
    
    # BTC rows
    for result in btc_results:
        tier = result['tier']
        info = tier_info.get(tier, {'win_rate': '?'})
        
        if result['success']:
            status = "[SIGNAL]" if result['has_signal'] else "[WAIT]"
            print(f"{'BTC':<8} | {tier:<20} | {result['criteria_passed']:<12} | {info['win_rate']:<12} | "
                  f"{result['confidence']:<12} | {result['price']:<15} | {status:<15}")
        else:
            error = result.get('error', 'Error')
            print(f"{'BTC':<8} | {tier:<20} | {'ERROR':<12} | {info['win_rate']:<12} | "
                  f"{'N/A':<12} | {'N/A':<15} | {error:<15}")
    
    print("-" * 140)
    
    # Gold rows
    for result in gold_results:
        tier = result['tier']
        info = tier_info.get(tier, {'win_rate': '?'})
        
        if result['success']:
            status = "[SIGNAL]" if result['has_signal'] else "[WAIT]"
            print(f"{'GOLD':<8} | {tier:<20} | {result['criteria_passed']:<12} | {info['win_rate']:<12} | "
                  f"{result['confidence']:<12} | {result['price']:<15} | {status:<15}")
        else:
            error = result.get('error', 'Error')
            print(f"{'GOLD':<8} | {tier:<20} | {'ERROR':<12} | {info['win_rate']:<12} | "
                  f"{'N/A':<12} | {'N/A':<15} | {error:<15}")
    
    print("-" * 140)


def print_summary(btc_results, gold_results):
    """Print summary"""
    print("\n" + "=" * 140)
    print("SUMMARY")
    print("=" * 140)
    
    btc_signals = sum(1 for r in btc_results if r.get('has_signal', False))
    gold_signals = sum(1 for r in gold_results if r.get('has_signal', False))
    total_signals = btc_signals + gold_signals
    
    print(f"\n[INFO] Total Signals: {total_signals}/8")
    print(f"   - BTC:  {btc_signals}/4")
    print(f"   - Gold: {gold_signals}/4")
    
    if total_signals > 0:
        print("\n[SIGNALS FOUND]")
        for result in btc_results + gold_results:
            if result.get('has_signal'):
                print(f"   [SIGNAL] {result['asset']} - {result['tier']}")
    
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
    
    print("\n" + "=" * 140)


def main():
    """Main comparison function"""
    print_header()
    
    # Define all signal generators
    generators = [
        # BTC generators
        ('BTC', 'Tier 1: Original A+', 'aplus_signal_generator.py'),
        ('BTC', 'Tier 2: Enhanced A+', 'enhanced_signal_generator.py'),
        ('BTC', 'Tier 3: Ultra A+', 'ultra_signal_generator.py'),
        ('BTC', 'Tier 4: ELITE A+', 'elite_signal_generator.py'),
        # Gold generators
        ('GOLD', 'Tier 1: Original A+', 'Gold expert/aplus_signal_generator.py'),
        ('GOLD', 'Tier 2: Enhanced A+', 'Gold expert/enhanced_signal_generator.py'),
        ('GOLD', 'Tier 3: Ultra A+', 'Gold expert/gold_signal_generator.py'),  # Gold uses gold_signal_generator
        ('GOLD', 'Tier 4: ELITE A+', 'Gold expert/elite_signal_generator.py'),
    ]
    
    print("\n[INFO] Running 8 signal generators in parallel (4 BTC + 4 Gold)...")
    print("This will take ~60-90 seconds...\n")
    
    # Run all generators in parallel
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(run_signal_generator, asset, tier, script): (asset, tier) 
                  for asset, tier, script in generators}
        
        for future in as_completed(futures):
            asset, tier = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"   [OK] {asset} - {tier} complete")
            except Exception as e:
                print(f"   [FAIL] {asset} - {tier} failed")
                results.append({
                    'asset': asset,
                    'tier': tier,
                    'success': False,
                    'error': str(e)[:30],
                    'has_signal': False,
                    'criteria_passed': 'N/A',
                    'confidence': 'N/A',
                    'price': 'N/A'
                })
    
    # Separate BTC and Gold results
    btc_results = sorted([r for r in results if r['asset'] == 'BTC'], key=lambda x: x['tier'])
    gold_results = sorted([r for r in results if r['asset'] == 'GOLD'], key=lambda x: x['tier'])
    
    # Print comparison table
    print_comparison_table(btc_results, gold_results)
    
    # Print summary
    print_summary(btc_results, gold_results)
    
    print("\n[DONE] Ultimate comparison complete!")
    print("=" * 140 + "\n")


if __name__ == "__main__":
    main()
