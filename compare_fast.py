"""
FAST Comparison - Smart Tier Selection
Only runs the tiers you actually need for faster results
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
    
    has_signal = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output or "ALL 14 CRITERIA MET" in output
    
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
    
    conf_match = re.search(r'Confidence: ([\d.]+)%', output)
    if conf_match:
        confidence = f"{conf_match.group(1)}%"
    
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
    print("FAST COMPARISON - SMART TIER SELECTION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)


def main():
    """Main function"""
    print_header()
    
    print("\nWhat would you like to check?")
    print("1. BTC ELITE only (fastest - 30 seconds)")
    print("2. Gold ELITE only (fastest - 30 seconds)")
    print("3. Both ELITE tiers (fast - 60 seconds)")
    print("4. BTC all tiers (90 seconds)")
    print("5. Gold all tiers (90 seconds)")
    print("6. Everything (4-5 minutes)")
    
    choice = input("\nEnter choice (1-6) or press Enter for option 3: ").strip()
    
    if not choice:
        choice = "3"
    
    generators = []
    
    if choice == "1":
        print("\n[FAST] Checking BTC ELITE only...")
        generators = [("BTC ELITE", "elite_signal_generator.py")]
    
    elif choice == "2":
        print("\n[FAST] Checking Gold ELITE only...")
        generators = [("GOLD ELITE", "Gold expert/elite_signal_generator.py")]
    
    elif choice == "3":
        print("\n[FAST] Checking both ELITE tiers...")
        generators = [
            ("BTC ELITE", "elite_signal_generator.py"),
            ("GOLD ELITE", "Gold expert/elite_signal_generator.py")
        ]
    
    elif choice == "4":
        print("\n[MEDIUM] Checking all BTC tiers...")
        generators = [
            ("BTC Tier 1", "aplus_signal_generator.py"),
            ("BTC Tier 2", "enhanced_signal_generator.py"),
            ("BTC Tier 3", "ultra_signal_generator.py"),
            ("BTC Tier 4", "elite_signal_generator.py")
        ]
    
    elif choice == "5":
        print("\n[MEDIUM] Checking all Gold tiers...")
        generators = [
            ("GOLD Tier 1", "Gold expert/aplus_signal_generator.py"),
            ("GOLD Tier 2", "Gold expert/enhanced_signal_generator.py"),
            ("GOLD Tier 3", "Gold expert/gold_signal_generator.py"),
            ("GOLD Tier 4", "Gold expert/elite_signal_generator.py")
        ]
    
    else:  # 6 or invalid
        print("\n[FULL] Checking everything...")
        generators = [
            ("BTC Tier 1", "aplus_signal_generator.py"),
            ("BTC Tier 2", "enhanced_signal_generator.py"),
            ("BTC Tier 3", "ultra_signal_generator.py"),
            ("BTC Tier 4", "elite_signal_generator.py"),
            ("GOLD Tier 1", "Gold expert/aplus_signal_generator.py"),
            ("GOLD Tier 2", "Gold expert/enhanced_signal_generator.py"),
            ("GOLD Tier 3", "Gold expert/gold_signal_generator.py"),
            ("GOLD Tier 4", "Gold expert/elite_signal_generator.py")
        ]
    
    # Run generators
    results = []
    for i, (name, script) in enumerate(generators, 1):
        print(f"\n   [{i}/{len(generators)}] Running {name}...")
        result = run_tier(name, script)
        results.append(result)
        print(f"   [{i}/{len(generators)}] {name}: {result['status']}")
    
    # Print results
    print("\n" + "="*100)
    print("RESULTS")
    print("="*100)
    print(f"\n{'GENERATOR':<25} | {'CRITERIA':<12} | {'CONFIDENCE':<12} | {'PRICE':<15} | {'STATUS':<15}")
    print("-"*100)
    
    for r in results:
        print(f"{r['name']:<25} | {r['criteria']:<12} | {r['confidence']:<12} | {r['price']:<15} | {r['status']:<15}")
    
    # Summary
    signals = sum(1 for r in results if r.get('has_signal', False))
    print("\n" + "="*100)
    print(f"Total Signals: {signals}/{len(results)}")
    
    if signals > 0:
        print("\n[SIGNAL FOUND!]")
        for r in results:
            if r.get('has_signal'):
                print(f"   >>> {r['name']} - READY TO TRADE!")
    else:
        print("\n[WAIT] No signals yet - be patient!")
    
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
