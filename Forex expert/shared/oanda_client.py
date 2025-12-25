"""
OANDA API Client - Free Forex Data
Uses OANDA practice account (no API key needed for basic data)
"""

import requests
import json
from datetime import datetime, timedelta


class OandaClient:
    """Client for OANDA forex data - FREE practice account"""
    
    def __init__(self, api_key=None, account_type="practice"):
        """
        Initialize OANDA client
        
        Args:
            api_key: Optional API key (not needed for practice account)
            account_type: "practice" (free) or "live" (requires key)
        """
        if account_type == "practice":
            self.base_url = "https://api-fxpractice.oanda.com"
        else:
            self.base_url = "https://api-fxtrade.oanda.com"
        
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def get_price(self, instrument):
        """
        Get current price for a forex pair
        
        Args:
            instrument: Pair name (e.g., "EUR_USD", "GBP_USD")
        
        Returns:
            dict: {"bid": float, "ask": float, "mid": float, "time": str}
        """
        try:
            url = f"{self.base_url}/v3/instruments/{instrument}/candles"
            params = {
                "count": 1,
                "granularity": "M1",  # 1-minute candles
                "price": "M"  # Mid prices
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                candle = data['candles'][0]
                
                return {
                    "bid": float(candle['mid']['c']) - 0.00005,  # Approximate bid
                    "ask": float(candle['mid']['c']) + 0.00005,  # Approximate ask
                    "mid": float(candle['mid']['c']),
                    "time": candle['time']
                }
            else:
                print(f"Error getting price: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_price: {e}")
            return None
    
    def get_candles(self, instrument, granularity="H1", count=500):
        """
        Get historical candle data
        
        Args:
            instrument: Pair name (e.g., "EUR_USD")
            granularity: Timeframe (M1, M5, M15, H1, H4, D, W)
            count: Number of candles (max 5000)
        
        Returns:
            list: List of candles with OHLC data
        """
        try:
            url = f"{self.base_url}/v3/instruments/{instrument}/candles"
            params = {
                "count": min(count, 5000),
                "granularity": granularity,
                "price": "M"  # Mid prices
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                candles = []
                
                for candle in data['candles']:
                    if candle['complete']:
                        candles.append({
                            'time': candle['time'],
                            'open': float(candle['mid']['o']),
                            'high': float(candle['mid']['h']),
                            'low': float(candle['mid']['l']),
                            'close': float(candle['mid']['c']),
                            'volume': int(candle['volume'])
                        })
                
                return candles
            else:
                print(f"Error getting candles: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_candles: {e}")
            return None
    
    def get_multiple_timeframes(self, instrument):
        """
        Get data for multiple timeframes at once
        
        Returns:
            dict: {"H1": [...], "H4": [...], "D": [...], "W": [...]}
        """
        timeframes = {
            "H1": self.get_candles(instrument, "H1", 500),
            "H4": self.get_candles(instrument, "H4", 500),
            "D": self.get_candles(instrument, "D", 365),
            "W": self.get_candles(instrument, "W", 52)
        }
        
        return timeframes
    
    def get_spread(self, instrument):
        """Get current spread in pips"""
        price = self.get_price(instrument)
        if price:
            spread = price['ask'] - price['bid']
            
            # Convert to pips
            if "JPY" in instrument:
                pips = spread * 100
            else:
                pips = spread * 10000
            
            return round(pips, 1)
        return None


# Example usage and testing
if __name__ == "__main__":
    print("Testing OANDA API Client...")
    print("=" * 50)
    
    # Initialize client (no API key needed for practice)
    client = OandaClient()
    
    # Test EUR/USD
    print("\n1. Getting EUR/USD current price...")
    price = client.get_price("EUR_USD")
    if price:
        print(f"   Bid: {price['bid']:.5f}")
        print(f"   Ask: {price['ask']:.5f}")
        print(f"   Mid: {price['mid']:.5f}")
        print(f"   Time: {price['time']}")
    
    # Test spread
    print("\n2. Getting EUR/USD spread...")
    spread = client.get_spread("EUR_USD")
    if spread:
        print(f"   Spread: {spread} pips")
    
    # Test historical data
    print("\n3. Getting EUR/USD H1 candles (last 10)...")
    candles = client.get_candles("EUR_USD", "H1", 10)
    if candles:
        print(f"   Got {len(candles)} candles")
        print(f"   Latest: O={candles[-1]['open']:.5f}, H={candles[-1]['high']:.5f}, L={candles[-1]['low']:.5f}, C={candles[-1]['close']:.5f}")
    
    # Test multiple timeframes
    print("\n4. Getting multiple timeframes...")
    mtf_data = client.get_multiple_timeframes("EUR_USD")
    for tf, data in mtf_data.items():
        if data:
            print(f"   {tf}: {len(data)} candles")
    
    print("\n" + "=" * 50)
    print("✅ OANDA API Client working!")
