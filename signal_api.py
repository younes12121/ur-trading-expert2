"""
ULTIMATE SIGNAL API - Claude AI Compatible
Standalone version that returns JSON for easy integration
Can be called from Claude AI or any application
"""

import subprocess
import sys
import re
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib
import time

# Try to import Redis for caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available - caching disabled. Install with: pip install redis")


class UltimateSignalAPI:
    """API-ready signal analyzer for Claude AI integration with caching"""

    def __init__(self, redis_client=None, cache_ttl=300, performance_mode=False):
        self.btc_script = "BTC expert/elite_signal_generator.py"
        self.gold_script = "Gold expert/elite_signal_generator.py"
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl  # 5 minutes default
        self.memory_cache = {}  # Fallback in-memory cache
        self.performance_mode = performance_mode
    
    def run_generator(self, script):
        """Run signal generator and get output"""
        try:
            print(f"[API] Running {script}...")
            # Set performance mode environment variable
            env = os.environ.copy()
            env['PERFORMANCE_MODE'] = 'true' if self.performance_mode else 'false'

            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                timeout=120,  # Increased from 90 to 120 seconds
                env=env
            )
            if result.returncode == 0:
                print(f"[API] {script} completed successfully")
                return result.stdout
            else:
                print(f"[API] {script} failed with code {result.returncode}")
                print(f"[API] Error: {result.stderr[:200]}")
                return None
        except subprocess.TimeoutExpired:
            print(f"[API] {script} timed out after 120 seconds")
            return None
        except Exception as e:
            print(f"[API] {script} error: {e}")
            return None
    
    def extract_signal_info(self, output, asset):
        """Extract all signal information"""
        info = {
            'asset': asset,
            'has_signal': False,
            'direction': 'N/A',
            'confidence': 'N/A',
            'price': 'N/A',
            'entry': 'N/A',
            'stop_loss': 'N/A',
            'tp1': 'N/A',
            'tp2': 'N/A',
            'criteria_passed': 'N/A',
            'criteria_total': 'N/A',
            'key_failures': []
        }
        
        if not output:
            return info
        
        info['has_signal'] = "[SUCCESS]" in output or "ALL 17 CRITERIA MET" in output
        
        dir_match = re.search(r'Direction: (BUY|SELL|HOLD)', output)
        if dir_match:
            info['direction'] = dir_match.group(1)
        
        conf_match = re.search(r'Confidence: ([\d.]+)%', output)
        if conf_match:
            info['confidence'] = conf_match.group(1)
        
        price_match = re.search(r'Current Price: \$([\d,]+\.[\d]+)', output)
        if price_match:
            info['price'] = price_match.group(1).replace(',', '')
        
        entry_match = re.search(r'Entry: \$([\d,]+\.[\d]+)', output)
        if entry_match:
            info['entry'] = entry_match.group(1).replace(',', '')
        
        sl_match = re.search(r'Stop Loss: \$([\d,]+\.[\d]+)', output)
        if sl_match:
            info['stop_loss'] = sl_match.group(1).replace(',', '')
        
        tp1_match = re.search(r'TP1.*?: \$([\d,]+\.[\d]+)', output)
        if tp1_match:
            info['tp1'] = tp1_match.group(1).replace(',', '')
        
        tp2_match = re.search(r'TP2.*?: \$([\d,]+\.[\d]+)', output)
        if tp2_match:
            info['tp2'] = tp2_match.group(1).replace(',', '')
        
        criteria_match = re.search(r'\[NOT .*?\]\s*\((\d+)/(\d+)', output)
        if criteria_match:
            info['criteria_passed'] = criteria_match.group(1)
            info['criteria_total'] = criteria_match.group(2)
        elif info['has_signal']:
            info['criteria_passed'] = "17"
            info['criteria_total'] = "17"
        
        fail_lines = re.findall(r'\[FAIL\] (.+)', output)
        info['key_failures'] = fail_lines[:5]
        
        return info
    
    def get_order_book_data(self, symbol):
        """Get order book analysis"""
        try:
            url = "https://api.binance.com/api/v3/depth"
            response = requests.get(url, params={'symbol': symbol, 'limit': 100}, timeout=10)
            data = response.json()
            
            bids = data.get('bids', [])
            asks = data.get('asks', [])
            
            total_bid = sum(float(b[1]) for b in bids)
            total_ask = sum(float(a[1]) for a in asks)
            
            imbalance = (total_bid - total_ask) / (total_bid + total_ask) * 100 if (total_bid + total_ask) > 0 else 0
            
            return {
                'bid_volume': round(total_bid, 4),
                'ask_volume': round(total_ask, 4),
                'imbalance': round(imbalance, 2),
                'pressure': 'BUY' if imbalance > 0 else 'SELL'
            }
        except:
            return None
    
    def _get_cache_key(self, asset: str) -> str:
        """Generate cache key for asset"""
        # Cache by asset and current 5-minute window
        current_window = int(time.time() / self.cache_ttl)
        key = f"signal:{asset}:{current_window}"
        return key
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache (Redis or memory)"""
        # Try Redis first
        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                print(f"[CACHE] Redis error: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            cached_data, timestamp = self.memory_cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Set data in cache (Redis or memory)"""
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(key, self.cache_ttl, json.dumps(data))
                return
            except Exception as e:
                print(f"[CACHE] Redis error: {e}")
        
        # Fallback to memory cache
        self.memory_cache[key] = (data, time.time())
        # Clean old entries (keep last 100)
        if len(self.memory_cache) > 100:
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k][1])
            del self.memory_cache[oldest_key]
    
    def get_complete_analysis(self, use_cache: bool = True):
        """Get complete analysis and return as JSON with caching"""
        
        cache_key = "complete_analysis"
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                print("[CACHE] Returning cached analysis")
                return cached
        
        # Get signals
        btc_output = self.run_generator(self.btc_script)
        gold_output = self.run_generator(self.gold_script)
        
        btc_signal = self.extract_signal_info(btc_output, "BTC")
        gold_signal = self.extract_signal_info(gold_output, "GOLD")
        
        # Get order book
        btc_orderbook = self.get_order_book_data('BTCUSDT')
        gold_orderbook = self.get_order_book_data('PAXGUSDT')
        
        # Calculate progress
        btc_pct = 0
        gold_pct = 0
        
        if btc_signal and btc_signal['criteria_passed'] != 'N/A':
            btc_pct = (int(btc_signal['criteria_passed']) / int(btc_signal['criteria_total'])) * 100
        
        if gold_signal and gold_signal['criteria_passed'] != 'N/A':
            gold_pct = (int(gold_signal['criteria_passed']) / int(gold_signal['criteria_total'])) * 100
        
        # Determine recommendation
        if btc_signal and btc_signal['has_signal']:
            recommendation = "BTC_SIGNAL_READY"
        elif gold_signal and gold_signal['has_signal']:
            recommendation = "GOLD_SIGNAL_READY"
        elif gold_pct > btc_pct:
            recommendation = "WATCH_GOLD"
        elif btc_pct > gold_pct:
            recommendation = "WATCH_BTC"
        else:
            recommendation = "WATCH_BOTH"
        
        # Build response
        response = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'btc': {
                'signal': btc_signal,
                'orderbook': btc_orderbook,
                'progress_pct': round(btc_pct, 1)
            },
            'gold': {
                'signal': gold_signal,
                'orderbook': gold_orderbook,
                'progress_pct': round(gold_pct, 1)
            },
            'recommendation': recommendation,
            'summary': {
                'any_signals': (btc_signal and btc_signal['has_signal']) or (gold_signal and gold_signal['has_signal']),
                'btc_improving': btc_orderbook and btc_orderbook['imbalance'] > 10,
                'gold_improving': gold_orderbook and gold_orderbook['imbalance'] > 10
            },
            'cached': False
        }
        
        # Cache the response
        if use_cache:
            self._set_cache(cache_key, response)
        
        return response


def main():
    """Main function - returns JSON"""
    api = UltimateSignalAPI()
    result = api.get_complete_analysis()
    
    # Print as formatted JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
