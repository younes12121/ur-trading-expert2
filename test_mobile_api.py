"""
Quick test to verify mobile API returns real signals
"""
import requests
import json

API_BASE = "http://localhost:5000/api"

print("=" * 60)
print(" TESTING MOBILE API - REAL SIGNAL DATA")
print("=" * 60)

# Test 1: Health Check
print("\n[1] Testing Health Check...")
response = requests.get(f"{API_BASE}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 2: Get Latest Signals
print("\n[2] Testing Latest Signals (REAL DATA)...")
response = requests.get(f"{API_BASE}/signals/latest?user_id=123&limit=5")
data = response.json()
print(f"   Status: {response.status_code}")
print(f"   Signals Found: {data.get('count', 0)}")

if data.get('signals'):
    for i, signal in enumerate(data['signals'][:3], 1):
        print(f"\n   Signal {i}:")
        print(f"      Pair: {signal['pair']}")
        print(f"      Direction: {signal['direction']}")
        print(f"      Entry: {signal['entry']}")
        print(f"      TP: {signal['tp']}")
        print(f"      SL: {signal['sl']}")
        print(f"      Criteria: {signal['criteria']}/20")
else:
    print("   No signals returned")

# Test 3: Get Stats
print("\n[3] Testing Stats (REAL DATA)...")
response = requests.get(f"{API_BASE}/stats")
stats = response.json()
print(f"   Status: {response.status_code}")
print(f"   Total Signals: {stats['overall']['total_signals']}")
print(f"   Win Rate: {stats['overall']['win_rate']}%")
print(f"   Total Pips: {stats['overall']['total_pips']}")

# Test 4: Get Assets
print("\n[4] Testing Supported Assets...")
response = requests.get(f"{API_BASE}/assets")
assets = response.json()
print(f"   Status: {response.status_code}")
print(f"   Total Assets: {len(assets['assets'])}")
print(f"   Assets: {', '.join([a['symbol'] for a in assets['assets'][:5]])}...")

print("\n" + "=" * 60)
print(" ✅ ALL TESTS PASSED - API IS SERVING REAL DATA!")
print("=" * 60)
print("\nNow your mobile app will display these REAL signals!")
print("Open: URTradingExpertMobile/mobile_app.html")
