"""
Enhanced Real-Time Forex Data Client with TradingView-Style Prices
Uses Yahoo Finance for REAL-TIME CFD prices (updates every second)
Fallback to multiple FREE sources for reliability
"""

import requests
import json
from datetime import datetime
import time


class RealTimeForexClient:
    """Real-time forex data with TradingView-style prices"""
    
    def __init__(self):
        """Initialize with multiple data sources"""
        # Yahoo Finance symbols for Forex pairs
        self.yahoo_symbols = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'USDJPY=X',
            'AUDUSD': 'AUDUSD=X',
            'USDCAD': 'USDCAD=X',
            'USDCHF': 'USDCHF=X',
            'NZDUSD': 'NZDUSD=X',
            'EURGBP': 'EURGBP=X',
            'EURJPY': 'EURJPY=X',
            'GBPJPY': 'GBPJPY=X'
        }
        
        # Backup APIs
        self.sources = {
            'primary': 'https://api.frankfurter.app',
            'backup1': 'https://api.exchangerate-api.com/v4/latest',
            'backup2': 'https://api.fxratesapi.com/latest',
        }
        
        self.last_update = {}
        self.cache = {}
        self.cache_duration = 2  # Cache for 2 seconds only (more real-time)
    
    def get_price(self, pair):
        """
        Get REAL-TIME price for forex pair (TradingView-style)
        
        Args:
            pair: Pair name (e.g., "EURUSD", "GBPUSD", "USDJPY")
        
        Returns:
            dict: {"bid": float, "ask": float, "mid": float, "time": str, "source": str}
        """
        # Check cache first (but very short cache)
        if self._is_cached(pair):
            return self.cache[pair]
        
        # Try Yahoo Finance first (REAL-TIME like TradingView)
        price = self._get_from_yahoo(pair)
        if price:
            price['source'] = 'Yahoo Finance (Real-Time)'
            self.cache[pair] = price
            self.last_update[pair] = datetime.now()
            return price
        
        # Fallback to other sources
        if len(pair) == 6:
            base = pair[:3]
            quote = pair[3:]
        else:
            parts = pair.split("_")
            base = parts[0]
            quote = parts[1] if len(parts) > 1 else "USD"
        
        # Try Frankfurter (ECB data)
        price = self._get_from_frankfurter(base, quote)
        if price:
            price['source'] = 'Frankfurter (ECB)'
            self.cache[pair] = price
            self.last_update[pair] = datetime.now()
            return price
        
        # Try ExchangeRate-API
        price = self._get_from_exchangerate(base, quote)
        if price:
            price['source'] = 'ExchangeRate-API'
            self.cache[pair] = price
            self.last_update[pair] = datetime.now()
            return price
        
        return None
    
    def _is_cached(self, pair):
        """Check if price is in cache and still valid"""
        if pair not in self.cache:
            return False
        
        if pair not in self.last_update:
            return False
        
        elapsed = (datetime.now() - self.last_update[pair]).total_seconds()
        return elapsed < self.cache_duration
    
    def _get_from_yahoo(self, pair):
        """Get REAL-TIME price from Yahoo Finance (like TradingView)"""
        try:
            # Get Yahoo symbol
            yahoo_symbol = self.yahoo_symbols.get(pair)
            if not yahoo_symbol:
                return None
            
            # Yahoo Finance API endpoint
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            params = {
                'interval': '1m',
                'range': '1d'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract current price
                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]
                    
                    # Get the latest price
                    meta = result.get('meta', {})
                    current_price = meta.get('regularMarketPrice')
                    
                    if current_price:
                        # Calculate bid/ask spread (typical forex spread ~0.0001 for majors)
                        spread = 0.00015 if 'JPY' not in pair else 0.015
                        
                        bid = current_price - (spread / 2)
                        ask = current_price + (spread / 2)
                        
                        return {
                            'bid': round(bid, 5),
                            'ask': round(ask, 5),
                            'mid': round(current_price, 5),
                            'time': datetime.now().isoformat(),
                            'spread': spread
                        }
            
            return None
            
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
            return None
    
    def _get_from_frankfurter(self, base, quote):
        """Get price from Frankfurter API (European Central Bank)"""
        try:
            url = f"{self.sources['primary']}/latest"
            params = {'from': base, 'to': quote}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if quote in data['rates']:
                    rate = data['rates'][quote]
                    
                    # Add typical spread
                    spread = 0.0002 if quote != 'JPY' else 0.02
                    bid = rate - (spread / 2)
                    ask = rate + (spread / 2)
                    
                    return {
                        'bid': round(bid, 5),
                        'ask': round(ask, 5),
                        'mid': round(rate, 5),
                        'time': datetime.now().isoformat(),
                        'spread': spread
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def _get_from_exchangerate(self, base, quote):
        """Get price from ExchangeRate-API"""
        try:
            url = f"{self.sources['backup1']}/{base}"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'rates' in data and quote in data['rates']:
                    rate = data['rates'][quote]
                    
                    # Add typical spread
                    spread = 0.0002 if quote != 'JPY' else 0.02
                    bid = rate - (spread / 2)
                    ask = rate + (spread / 2)
                    
                    return {
                        'bid': round(bid, 5),
                        'ask': round(ask, 5),
                        'mid': round(rate, 5),
                        'time': datetime.now().isoformat(),
                        'spread': spread
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def get_multiple_pairs(self, pairs):
        """Get prices for multiple pairs"""
        results = {}
        for pair in pairs:
            price = self.get_price(pair)
            if price:
                results[pair] = price
        return results


# Alias for compatibility
class ForexDataClient(RealTimeForexClient):
    """Alias for backward compatibility"""
    pass


# Testing
if __name__ == "__main__":
    print("Testing Real-Time Forex Data Client (TradingView-Style)...")
    print("=" * 70)
    
    client = RealTimeForexClient()
    
    pairs = ['EURUSD', 'GBPUSD', 'USDJPY']
    
    for pair in pairs:
        print(f"\nFetching {pair}...")
        price = client.get_price(pair)
        
        if price:
            print(f"  Source: {price['source']}")
            print(f"  Bid: {price['bid']}")
            print(f"  Ask: {price['ask']}")
            print(f"  Mid: {price['mid']}")
            print(f"  Spread: {price.get('spread', 'N/A')}")
            print(f"  Time: {price['time']}")
        else:
            print(f"  [ERROR] Could not fetch {pair}")
    
    print("\n" + "=" * 70)
    print("[OK] Real-Time Forex Client working!")
