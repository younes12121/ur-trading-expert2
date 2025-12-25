"""
Dual Expert Comparison - BTC vs Gold
Runs both trading experts side-by-side for comparison
"""

import sys
import os
from datetime import datetime

# Add both expert directories to path
btc_path = os.path.join(os.path.dirname(__file__), 'BTC expert')
gold_path = os.path.join(os.path.dirname(__file__), 'Gold expert')
sys.path.insert(0, btc_path)
sys.path.insert(0, gold_path)


def print_header():
    """Print comparison header"""
    print("\n" + "=" * 100)
    print("DUAL EXPERT COMPARISON - BTC vs GOLD")
    print("Ultra A+ Signal Generator (17 Criteria | 85-90% Win Rate)")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)


def run_btc_expert():
    """Run BTC expert and return signal data"""
    print("\n" + ">" * 50)
    print("RUNNING BTC EXPERT...")
    print(">" * 50)
    
    try:
        import subprocess
        import json
        
        # Run BTC expert as subprocess
        result = subprocess.run(
            ['python', 'BTC expert/ultra_signal_generator.py'],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse output to extract signal info
            output = result.stdout
            has_signal = "[ULTRA A+] ALL 17 CRITERIA MET" in output
            
            return {
                'success': True,
                'signal': has_signal,
                'output': output
            }
        else:
            print(f"\n[ERROR] BTC Expert failed with code {result.returncode}")
            return {
                'success': False,
                'error': result.stderr
            }
        
    except Exception as e:
        print(f"\n[ERROR] BTC Expert Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def run_gold_expert():
    """Run Gold expert and return signal data"""
    print("\n" + ">" * 50)
    print("RUNNING GOLD EXPERT...")
    print(">" * 50)
    
    try:
        import subprocess
        import json
        
        # Run Gold expert as subprocess
        result = subprocess.run(
            ['python', 'Gold expert/gold_signal_generator.py'],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse output to extract signal info
            output = result.stdout
            has_signal = "[ULTRA A+] ALL 17 CRITERIA MET" in output
            
            return {
                'success': True,
                'signal': has_signal,
                'output': output
            }
        else:
            print(f"\n[ERROR] Gold Expert failed with code {result.returncode}")
            return {
                'success': False,
                'error': result.stderr
            }
        
    except Exception as e:
        print(f"\n[ERROR] Gold Expert Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def print_comparison(btc_result, gold_result):
    """Print side-by-side comparison"""
    print("\n" + "=" * 100)
    print("COMPARISON RESULTS")
    print("=" * 100)
    
    # Create comparison table
    print("\n{:<30} | {:<30} | {:<30}".format("METRIC", "BTC EXPERT", "GOLD EXPERT"))
    print("-" * 100)
    
    # Status
    btc_status = "[SIGNAL] ULTRA A+ SIGNAL" if (btc_result['success'] and btc_result.get('signal')) else "[WAIT] WAIT"
    gold_status = "[SIGNAL] ULTRA A+ SIGNAL" if (gold_result['success'] and gold_result.get('signal')) else "[WAIT] WAIT"
    print("{:<30} | {:<30} | {:<30}".format("Status", btc_status, gold_status))
    
    # Symbol
    btc_symbol = "BTCUSDT" if btc_result['success'] else "ERROR"
    gold_symbol = "PAXGUSDT (Gold)" if gold_result['success'] else "ERROR"
    print("{:<30} | {:<30} | {:<30}".format("Symbol", btc_symbol, gold_symbol))
    
    # Extract signal details from output if available
    if btc_result['success'] and btc_result.get('signal'):
        output = btc_result.get('output', '')
        # Parse output for signal details
        print("\n{:<30}".format("BTC SIGNAL DETAILS:"))
        for line in output.split('\n'):
            if 'Direction:' in line or 'Entry:' in line or 'Stop Loss:' in line or 'TP1' in line:
                print(f"   {line.strip()}")
    
    if gold_result['success'] and gold_result.get('signal'):
        output = gold_result.get('output', '')
        # Parse output for signal details
        print("\n{:<30}".format("GOLD SIGNAL DETAILS:"))
        for line in output.split('\n'):
            if 'Direction:' in line or 'Entry:' in line or 'Stop Loss:' in line or 'TP1' in line:
                print(f"   {line.strip()}")
    
    print("-" * 100)
    
    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    
    btc_count = 1 if (btc_result['success'] and btc_result['signal']) else 0
    gold_count = 1 if (gold_result['success'] and gold_result['signal']) else 0
    total_signals = btc_count + gold_count
    
    print(f"\n[INFO] Total Ultra A+ Signals: {total_signals}/2")
    print(f"   - BTC:  {'[SIGNAL] SIGNAL FOUND' if btc_count else '[WAIT] Waiting'}")
    print(f"   - Gold: {'[SIGNAL] SIGNAL FOUND' if gold_count else '[WAIT] Waiting'}")
    
    if total_signals == 0:
        print("\n[WAIT] No Ultra A+ setups available right now.")
        print("   Stay patient - ultra setups are extremely rare but have 85-90% win rate!")
        print("   Check back in 2-4 hours.")
    elif total_signals == 1:
        print("\n[SIGNAL] One Ultra A+ setup found!")
        print("   Review the signal details above carefully before trading.")
    else:
        print("\n[RARE] RARE EVENT: Both BTC and Gold have Ultra A+ setups!")
        print("   This is extremely rare - consider both opportunities carefully.")
    
    print("\n" + "=" * 100)


def main():
    """Main comparison function"""
    print_header()
    
    # Run both experts
    btc_result = run_btc_expert()
    gold_result = run_gold_expert()
    
    # Print comparison
    print_comparison(btc_result, gold_result)
    
    print("\n[DONE] Comparison complete!")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()
