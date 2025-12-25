"""
Quick test to verify Forex imports work
"""

import sys
import os

# Add paths
"""
Quick test to verify Forex imports work
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Forex expert', 'shared'))

print("Testing imports...")

try:
    from forex_data_client import ForexDataClient, RealTimeForexClient
    print("[OK] ForexDataClient imported successfully")
    print("[OK] RealTimeForexClient imported successfully")
    
    # Test instantiation
    client1 = ForexDataClient()
    client2 = RealTimeForexClient()
    print("[OK] Both classes instantiate successfully")
    
    # Test they're the same
    print(f"[OK] ForexDataClient is RealTimeForeexClient: {ForexDataClient is RealTimeForexClient}")
    
    # Test getting price
    price = client1.get_price("EURUSD")
    if price:
        print(f"[OK] EUR/USD price: {price['mid']:.5f}")
    
    print("\n[SUCCESS] ALL IMPORTS WORKING!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
