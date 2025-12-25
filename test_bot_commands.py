"""
Automated Bot Command Tester
Tests all Telegram bot commands without needing actual Telegram interaction
"""

# Fix Windows encoding FIRST
import sys
import io
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("TELEGRAM BOT AUTOMATED TESTING")
print("=" * 70)

# Test results storage
results = {
    'passed': [],
    'failed': [],
    'skipped': []
}

def test_import(module_name, file_path):
    """Test if a module can be imported"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, module
    except Exception as e:
        return False, str(e)

print("\n[1/6] Testing Core Imports...")
print("-" * 70)

# Test signal API
success, result = test_import("signal_api", "signal_api.py")
if success:
    print("✅ signal_api.py - OK")
    results['passed'].append("signal_api import")
else:
    print(f"❌ signal_api.py - FAILED: {result}")
    results['failed'].append(f"signal_api import: {result}")

# Test trade tracker
success, result = test_import("trade_tracker", "trade_tracker.py")
if success:
    print("✅ trade_tracker.py - OK")
    results['passed'].append("trade_tracker import")
else:
    print(f"❌ trade_tracker.py - FAILED: {result}")
    results['failed'].append(f"trade_tracker import: {result}")

# Test multi-timeframe analyzer
success, result = test_import("mtf_analyzer", "multi_timeframe_analyzer.py")
if success:
    print("✅ multi_timeframe_analyzer.py - OK")
    results['passed'].append("MTF analyzer import")
    mtf_analyzer = result
else:
    print(f"❌ multi_timeframe_analyzer.py - FAILED: {result}")
    results['failed'].append(f"MTF analyzer import: {result}")
    mtf_analyzer = None

# Test TradingView data client
success, result = test_import("tv_client", "tradingview_data_client.py")
if success:
    print("✅ tradingview_data_client.py - OK")
    results['passed'].append("TradingView client import")
else:
    print(f"❌ tradingview_data_client.py - FAILED: {result}")
    results['failed'].append(f"TradingView client import: {result}")

print("\n[2/6] Testing Forex Data Client...")
print("-" * 70)

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "forex_client", 
        "Forex expert/shared/forex_data_client.py"
    )
    forex_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(forex_module)
    
    client = forex_module.RealTimeForexClient()
    
    # Test getting single pair
    price = client.get_price('EURUSD')
    if price and 'mid' in price:
        print(f"✅ EURUSD Price Fetch - OK (Price: {price['mid']:.5f})")
        results['passed'].append("Forex price fetch")
    else:
        print("❌ EURUSD Price Fetch - No data")
        results['failed'].append("Forex price fetch: No data returned")
    
    # Test multiple pairs
    pairs = ['EURUSD', 'GBPUSD', 'USDJPY']
    prices = client.get_multiple_pairs(pairs)
    if len(prices) == 3:
        print(f"✅ Multiple Pairs Fetch - OK ({len(prices)} pairs)")
        results['passed'].append("Multiple pairs fetch")
    else:
        print(f"⚠️ Multiple Pairs Fetch - Partial ({len(prices)}/3 pairs)")
        results['failed'].append(f"Multiple pairs fetch: Only {len(prices)}/3")
        
except Exception as e:
    print(f"❌ Forex Client - FAILED: {e}")
    results['failed'].append(f"Forex client: {e}")

print("\n[3/6] Testing Multi-Timeframe Analyzer...")
print("-" * 70)

if mtf_analyzer:
    try:
        analyzer = mtf_analyzer.MultiTimeframeAnalyzer()
        
        # Test analysis
        analysis = analyzer.analyze_pair('EURUSD')
        
        if analysis and 'consensus' in analysis:
            print(f"✅ MTF Analysis - OK")
            print(f"   Consensus: {analysis['consensus']}")
            print(f"   Alignment: {analysis['alignment_pct']}%")
            print(f"   Signal Strength: {analysis['signal_strength']}%")
            results['passed'].append("MTF analysis")
        else:
            print("❌ MTF Analysis - No valid data")
            results['failed'].append("MTF analysis: No data")
            
    except Exception as e:
        print(f"❌ MTF Analysis - FAILED: {e}")
        results['failed'].append(f"MTF analysis: {e}")
else:
    print("⚠️ MTF Analysis - SKIPPED (module not loaded)")
    results['skipped'].append("MTF analysis (module not loaded)")

print("\n[4/6] Testing Economic Calendar...")
print("-" * 70)

try:
    spec = importlib.util.spec_from_file_location(
        "calendar", 
        "Forex expert/shared/economic_calendar.py"
    )
    calendar_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(calendar_module)
    
    calendar = calendar_module.EconomicCalendar()
    events = calendar.get_upcoming_events(hours_ahead=24)  # Fixed: was 'hours'
    
    print(f"✅ Economic Calendar - OK ({len(events)} events in next 24h)")
    results['passed'].append("Economic calendar")
    
except Exception as e:
    print(f"❌ Economic Calendar - FAILED: {e}")
    results['failed'].append(f"Economic calendar: {e}")

print("\n[5/6] Testing Correlation Analyzer...")
print("-" * 70)

try:
    spec = importlib.util.spec_from_file_location(
        "corr_analyzer", 
        "Forex expert/shared/correlation_analyzer.py"
    )
    corr_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(corr_module)
    
    # Get forex client
    spec2 = importlib.util.spec_from_file_location(
        "forex_client", 
        "Forex expert/shared/forex_data_client.py"
    )
    forex_module = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(forex_module)
    
    data_client = forex_module.RealTimeForexClient()
    analyzer = corr_module.CorrelationAnalyzer(data_client)
    
    # Test correlation
    corr = analyzer.calculate_correlation('EURUSD', 'GBPUSD')
    
    print(f"✅ Correlation Analyzer - OK (EUR/USD vs GBP/USD: {corr:.2%})")
    results['passed'].append("Correlation analyzer")
    
except Exception as e:
    print(f"❌ Correlation Analyzer - FAILED: {e}")
    results['failed'].append(f"Correlation analyzer: {e}")

print("\n[6/6] Testing Signal Generators...")
print("-" * 70)

# Test Forex signal generators
forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY']
for pair in forex_pairs:
    try:
        spec = importlib.util.spec_from_file_location(
            f"{pair.lower()}_gen", 
            f"Forex expert/{pair}/elite_signal_generator.py"
        )
        gen_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gen_module)
        
        print(f"✅ {pair} Signal Generator - Module OK")
        results['passed'].append(f"{pair} generator import")
        
    except Exception as e:
        print(f"❌ {pair} Signal Generator - FAILED: {str(e)[:50]}")
        results['failed'].append(f"{pair} generator: {str(e)[:50]}")

# BTC and Gold generators (skip running, just check existence)
for asset, path in [('BTC', 'BTC expert'), ('Gold', 'Gold expert')]:
    if os.path.exists(f"{path}/elite_signal_generator.py"):
        print(f"✅ {asset} Signal Generator - File exists")
        results['passed'].append(f"{asset} file exists")
    else:
        print(f"❌ {asset} Signal Generator - File not found")
        results['failed'].append(f"{asset} file not found")

# Generate summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

print(f"\n✅ PASSED: {len(results['passed'])}")
for test in results['passed'][:10]:  # Show first 10
    print(f"   • {test}")
if len(results['passed']) > 10:
    print(f"   ... and {len(results['passed']) - 10} more")

if results['failed']:
    print(f"\n❌ FAILED: {len(results['failed'])}")
    for test in results['failed']:
        print(f"   • {test}")

if results['skipped']:
    print(f"\n⚠️ SKIPPED: {len(results['skipped'])}")
    for test in results['skipped']:
        print(f"   • {test}")

# Calculate pass rate
total = len(results['passed']) + len(results['failed'])
pass_rate = (len(results['passed']) / total * 100) if total > 0 else 0

print(f"\n📊 OVERALL PASS RATE: {pass_rate:.1f}%")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)

# Exit with appropriate code
sys.exit(0 if len(results['failed']) == 0 else 1)
