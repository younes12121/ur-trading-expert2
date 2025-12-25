"""
Quick Multi-Tier Comparison
Runs all 4 tiers at once and shows results side-by-side
"""

import subprocess
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_tier(tier_name, script_name):
    """
    Run a single tier and capture output
    Returns: (tier_name, output, success)
    """
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        
        # Parse key information
        has_signal = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output or "ALL 14 CRITERIA MET" in output
        
        # Extract criteria passed
        criteria_passed = "N/A"
        if "NOT A+]" in output:
            # Look for pattern like "(3/8 criteria passed)"
            import re
            match = re.search(r'\((\d+)/(\d+) criteria passed\)', output)
            if match:
                criteria_passed = f"{match.group(1)}/{match.group(2)}"
        elif has_signal:
            # If signal found, all criteria passed
            if "ELITE" in tier_name or "Ultra" in tier_name:
                criteria_passed = "17/17"
            elif "Enhanced" in tier_name:
                criteria_passed = "14/14"
            else:
                criteria_passed = "8/8"
        
        # Extract confidence
        confidence = "N/A"
        import re
        conf_match = re.search(r'Confidence: ([\d.]+)%', output)
        if conf_match:
            confidence = f"{conf_match.group(1)}%"
        
        # Extract price
        price = "N/A"
        price_match = re.search(r'Current Price: \$([\d,]+\.[\d]+)', output)
        if price_match:
            price = f"${price_match.group(1)}"
        
        return {
            'tier': tier_name,
            'success': True,
            'has_signal': has_signal,
            'criteria_passed': criteria_passed,
            'confidence': confidence,
            'price': price,
            'output': output
        }
        
    except subprocess.TimeoutExpired:
        return {
            'tier': tier_name,
            'success': False,
            'error': 'Timeout (>60s)',
            'has_signal': False,
            'criteria_passed': 'N/A',
            'confidence': 'N/A',
            'price': 'N/A'
        }
    except Exception as e:
        return {
            'tier': tier_name,
            'success': False,
            'error': str(e),
            'has_signal': False,
            'criteria_passed': 'N/A',
            'confidence': 'N/A',
            'price': 'N/A'
        }


def print_header():
    """Print comparison header"""
    print("\n" + "=" * 120)
    print("MULTI-TIER COMPARISON - ALL 4 SYSTEMS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)


def print_comparison_table(results):
    """Print results in a nice table"""
    print("\n" + "=" * 120)
    print("COMPARISON RESULTS")
    print("=" * 120)
    
    # Header
    print(f"\n{'TIER':<25} | {'CRITERIA':<12} | {'WIN RATE':<12} | {'CONFIDENCE':<12} | {'PRICE':<15} | {'STATUS':<20}")
    print("-" * 120)
    
    # Rows
    tier_info = {
        'Tier 1: Original A+': {'criteria_total': 8, 'win_rate': '65-70%'},
        'Tier 2: Enhanced A+': {'criteria_total': 14, 'win_rate': '75-85%'},
        'Tier 3: Ultra A+': {'criteria_total': 17, 'win_rate': '85-90%'},
        'Tier 4: ELITE A+': {'criteria_total': '17+5', 'win_rate': '90-95%'}
    }
    
    for result in results:
        tier = result['tier']
        info = tier_info.get(tier, {'criteria_total': '?', 'win_rate': '?'})
        
        if result['success']:
            status = "[SIGNAL]" if result['has_signal'] else "[WAIT]"
            status_color = status
            
            print(f"{tier:<25} | {result['criteria_passed']:<12} | {info['win_rate']:<12} | "
                  f"{result['confidence']:<12} | {result['price']:<15} | {status_color:<20}")
        else:
            error = result.get('error', 'Unknown error')
            print(f"{tier:<25} | {'ERROR':<12} | {info['win_rate']:<12} | "
                  f"{'N/A':<12} | {'N/A':<15} | {error:<20}")
    
    print("-" * 120)


def print_summary(results):
    """Print summary"""
    print("\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    
    signal_count = sum(1 for r in results if r.get('has_signal', False))
    total_tiers = len(results)
    
    print(f"\n[INFO] Signals Found: {signal_count}/{total_tiers}")
    
    for result in results:
        if result.get('has_signal'):
            print(f"   [SIGNAL] {result['tier']}: SIGNAL FOUND!")
    
    if signal_count == 0:
        print("\n[WAIT] No signals available right now.")
        print("   - Market may be too quiet or choppy")
        print("   - Wait for better conditions")
        print("   - Check back in 2-4 hours (best: 14:00 or 20:00 CET)")
    elif signal_count == 1:
        print("\n[SIGNAL] One tier has a signal!")
        print("   - Review the signal details carefully")
        print("   - Higher tier = higher win rate")
    else:
        print(f"\n[MULTIPLE] {signal_count} tiers have signals!")
        print("   - Use the highest tier signal for best win rate")
        print("   - ELITE > Ultra > Enhanced > Original")
    
    print("\n" + "=" * 120)


def main():
    """Main comparison function"""
    print_header()
    
    # Define tiers to test
    tiers = [
        ('Tier 1: Original A+', 'aplus_signal_generator.py'),
        ('Tier 2: Enhanced A+', 'enhanced_signal_generator.py'),
        ('Tier 3: Ultra A+', 'ultra_signal_generator.py'),
        ('Tier 4: ELITE A+', 'elite_signal_generator.py')
    ]
    
    print("\n[INFO] Running all 4 tiers in parallel...")
    print("This will take ~30-60 seconds...\n")
    
    # Run all tiers in parallel
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(run_tier, tier_name, script): tier_name 
                  for tier_name, script in tiers}
        
        for future in as_completed(futures):
            tier_name = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"   [OK] {tier_name} complete")
            except Exception as e:
                print(f"   [FAIL] {tier_name} failed: {str(e)}")
                results.append({
                    'tier': tier_name,
                    'success': False,
                    'error': str(e),
                    'has_signal': False,
                    'criteria_passed': 'N/A',
                    'confidence': 'N/A',
                    'price': 'N/A'
                })
    
    # Sort results by tier number
    results.sort(key=lambda x: x['tier'])
    
    # Print comparison table
    print_comparison_table(results)
    
    # Print summary
    print_summary(results)
    
    print("\n[DONE] Multi-tier comparison complete!")
    print("=" * 120 + "\n")


if __name__ == "__main__":
    main()
