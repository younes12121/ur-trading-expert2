#!/usr/bin/env python3
"""
Comprehensive Test - ALL 15 Trading Assets
Tests BTC, Gold, ES, NQ, and all 11 Forex pairs
"""

import sys
import os
from importlib import util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 TESTING ALL 15 TRADING ASSETS")
print("=" * 80)
print()

results = {
    'success': [],
    'no_signal': [],
    'error': []
}

# Test assets
assets_to_test = [
    # Crypto & Commodities
    ('BTC', 'BTC expert/btc_elite_signal_generator.py', 'BTCEliteSignalGenerator', '🪙 Bitcoin'),
    ('Gold', 'Gold expert/gold_elite_signal_generator.py', 'GoldEliteSignalGenerator', '🥇 Gold'),
    
    # US Futures
    ('ES', 'Futures expert/ES/elite_signal_generator.py', 'ESEliteSignalGenerator', '📊 E-mini S&P 500'),
    ('NQ', 'Futures expert/NQ/elite_signal_generator.py', 'NQEliteSignalGenerator', '🚀 E-mini NASDAQ-100'),
    
    # Forex Pairs
    ('EURUSD', 'Forex expert/EURUSD/elite_signal_generator.py', 'EURUSDEliteSignalGenerator', '🇪🇺🇺🇸 EUR/USD'),
    ('GBPUSD', 'Forex expert/GBPUSD/elite_signal_generator.py', 'GBPUSDEliteSignalGenerator', '🇬🇧🇺🇸 GBP/USD'),
    ('USDJPY', 'Forex expert/USDJPY/elite_signal_generator.py', 'USDJPYEliteSignalGenerator', '🇺🇸🇯🇵 USD/JPY'),
    ('AUDUSD', 'Forex expert/AUDUSD/elite_signal_generator.py', 'AUDUSDEliteSignalGenerator', '🇦🇺🇺🇸 AUD/USD'),
    ('USDCAD', 'Forex expert/USDCAD/elite_signal_generator.py', 'USDCADEliteSignalGenerator', '🇺🇸🇨🇦 USD/CAD'),
    ('EURJPY', 'Forex expert/EURJPY/elite_signal_generator.py', 'EURJPYEliteSignalGenerator', '🇪🇺🇯🇵 EUR/JPY'),
]

# Additional forex pairs that may exist
additional_forex = [
    ('USDCHF', 'Forex expert/USDCHF/elite_signal_generator.py', 'USDCHFEliteSignalGenerator', '🇺🇸🇨🇭 USD/CHF'),
    ('NZDUSD', 'Forex expert/NZDUSD/elite_signal_generator.py', 'NZDUSDEliteSignalGenerator', '🥝 NZD/USD'),
    ('EURGBP', 'Forex expert/EURGBP/elite_signal_generator.py', 'EURGBPEliteSignalGenerator', '🇪🇺🇬🇧 EUR/GBP'),
    ('GBPJPY', 'Forex expert/GBPJPY/elite_signal_generator.py', 'GBPJPYEliteSignalGenerator', '🐉 GBP/JPY'),
    ('AUDJPY', 'Forex expert/AUDJPY/elite_signal_generator.py', 'AUDJPYEliteSignalGenerator', '🇦🇺🇯🇵 AUD/JPY'),
]

assets_to_test.extend(additional_forex)

# Test each asset
for i, (symbol, path, class_name, display_name) in enumerate(assets_to_test, 1):
    print(f"{i:2d}. Testing {display_name}...")
    
    # Check if file exists
    if not os.path.exists(path):
        print(f"    ⚠️  File not found: {path}")
        results['error'].append(symbol)
        continue
    
    try:
        # Import module
        spec = util.spec_from_file_location(f"{symbol}_gen", path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get generator class
        generator_class = getattr(module, class_name)
        generator = generator_class()
        
        # Generate signal
        signal = generator.generate_signal()
        
        if signal:
            # Check for NaN values
            has_nan = False
            for key, value in signal.items():
                if isinstance(value, float) and (value != value):  # NaN check
                    has_nan = True
                    break
            
            if has_nan:
                print(f"    ❌ Signal has NaN values!")
                results['error'].append(symbol)
            else:
                print(f"    ✅ Signal generated! ({signal['direction']}, {signal['confidence']}% confidence)")
                results['success'].append(symbol)
        else:
            print(f"    ℹ️  No signal (criteria not met - normal)")
            results['no_signal'].append(symbol)
    
    except Exception as e:
        error_msg = str(e)[:60]
        print(f"    ❌ Error: {error_msg}")
        results['error'].append(symbol)

# Summary
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print()

print(f"✅ Working with Signal: {len(results['success'])}")
if results['success']:
    for asset in results['success']:
        print(f"   • {asset}")

print(f"\nℹ️  Working (No Signal): {len(results['no_signal'])}")
if results['no_signal']:
    for asset in results['no_signal']:
        print(f"   • {asset}")

print(f"\n❌ Errors: {len(results['error'])}")
if results['error']:
    for asset in results['error']:
        print(f"   • {asset}")

total_working = len(results['success']) + len(results['no_signal'])
total_assets = len(assets_to_test)

print(f"\n{'=' * 80}")
print(f"RESULT: {total_working}/{total_assets} assets working correctly")

if results['error']:
    print(f"\n⚠️  {len(results['error'])} assets need attention")
else:
    print(f"\n🎉 ALL ASSETS WORKING PERFECTLY!")

print("=" * 80)
print()
print("🚀 Next: Restart your bot and test in Telegram!")
print()





