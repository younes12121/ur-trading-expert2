"""
Quick BTC + Gold Comparison (Sequential)
Runs all 8 generators one at a time for reliability
"""

import subprocess
import sys
from datetime import datetime


def run_generator(name, script):
    """Run a single generator and return results"""
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        
        # Extract key info
        import re
        criteria = "N/A"
        confidence = "N/A"
        price = "N/A"
        
        # Try to find criteria
        match = re.search(r'\[NOT .*?\]\s*\((\d+)/(\d+)', output)
        if match:
            criteria = f"{match.group(1)}/{match.group(2)}"
        
        # Find confidence
        conf_match = re.search(r'Confidence: ([\d.]+)%', output)
        if conf_match:
            confidence = f"{conf_match.group(1)}%"
        
        # Find price
        price_match = re.search(r'Current Price: \$([\d,]+\.[\d]+)', output)
        if price_match:
            price = f"${price_match.group(1)}"
        
        has_signal = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output
        
        return {
            'name': name,
            'criteria': criteria,
            'confidence': confidence,
            'price': price,
            'has_signal': has_signal,
            'success': True
        }
    except Exception as e:
        return {
            'name': name,
            'criteria': 'ERROR',
            'confidence': 'N/A',
            'price': 'N/A',
            'has_signal': False,
            'success': False,
            'error': str(e)[:50]
        }


def main():
    print("\n" + "="*100)
    print("QUICK COMPARISON - BTC vs GOLD - ALL 4 TIERS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # Define all generators
    generators = [
        ("BTC Tier 1 (Original)", "aplus_signal_generator.py"),
        ("BTC Tier 2 (Enhanced)", "enhanced_signal_generator.py"),
        ("BTC Tier 3 (Ultra)", "ultra_signal_generator.py"),
        ("BTC Tier 4 (ELITE)", "elite_signal_generator.py"),
        ("GOLD Tier 1 (Original)", "Gold expert/aplus_signal_generator.py"),
        ("GOLD Tier 2 (Enhanced)", "Gold expert/enhanced_signal_generator.py"),
        ("GOLD Tier 3 (Ultra)", "Gold expert/gold_signal_generator.py"),
        ("GOLD Tier 4 (ELITE)", "Gold expert/elite_signal_generator.py"),
    ]
    
    results = []
    for name, script in generators:
        result = run_generator(name, script)
        results.append(result)
    
    # Print summary table
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    print(f"\n{'GENERATOR':<30} | {'CRITERIA':<12} | {'CONFIDENCE':<12} | {'PRICE':<15} | {'STATUS':<15}")
    print("-"*100)
    
    for r in results:
        status = "[SIGNAL]" if r['has_signal'] else "[WAIT]"
        if not r['success']:
            status = f"ERROR: {r.get('error', 'Unknown')}"
        print(f"{r['name']:<30} | {r['criteria']:<12} | {r['confidence']:<12} | {r['price']:<15} | {status:<15}")
    
    # Count signals
    btc_signals = sum(1 for r in results[:4] if r['has_signal'])
    gold_signals = sum(1 for r in results[4:] if r['has_signal'])
    
    print("\n" + "="*100)
    print(f"Total Signals: {btc_signals + gold_signals}/8")
    print(f"  - BTC:  {btc_signals}/4")
    print(f"  - GOLD: {gold_signals}/4")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
