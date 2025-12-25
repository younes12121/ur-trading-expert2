"""
Real-time data fetcher for BTC trading system
Fetches live market data from Binance API
PERFORMANCE OPTIMIZED VERSION
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import config
from functools import lru_cache
from global_error_learning import global_error_manager, record_error

logger = logging.getLogger(__name__)

class BinanceDataFetcher:
    """Fetches real-time and historical data from Binance with rate limiting and caching - OPTIMIZED"""

    def __init__(self, symbol: str = "BTCUSDT", performance_mode: bool = False):
        self.symbol = symbol
        self.base_url = config.BINANCE_TESTNET_URL if config.USE_TESTNET else config.BINANCE_BASE_URL
        self.performance_mode = performance_mode

        # Enhanced caching system
        self.cache = {}
        self.cache_time = {}
        self.computed_cache = {}  # Cache for expensive computations
        self.session = None

        # Rate limiting (optimized)
        self.rate_limit_delay = 0.05 if performance_mode else 0.1  # Faster in performance mode
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        self.max_requests_per_minute = 1200

        # Thread pool for concurrent requests
        self.executor = ThreadPoolExecutor(max_workers=3) if performance_mode else None

        # Cache TTL settings (longer in performance mode)
        self.cache_ttl = {
            'price': 2 if performance_mode else 5,  # seconds
            'ticker': 3 if performance_mode else 10,
            'volatility': 30 if performance_mode else 60,  # seconds
            'fear_greed': 300 if performance_mode else 600,  # 5-10 minutes
        }
        
    def _rate_limit_check(self):
        """Enforce rate limiting"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Check if we're at the limit
        if self.request_count >= self.max_requests_per_minute:
            sleep_time = 60 - (current_time - self.request_window_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Enforce minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1

    async def _concurrent_api_calls(self, endpoints: List[Dict]) -> Dict:
        """Make concurrent API calls for better performance"""
        if not self.performance_mode:
            # Fallback to sequential calls
            results = {}
            for endpoint in endpoints:
                results[endpoint['name']] = endpoint['func']()
            return results

        async with aiohttp.ClientSession() as session:
            self.session = session
            tasks = []

            for endpoint in endpoints:
                task = asyncio.create_task(self._make_async_request(endpoint))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            result_dict = {}
            for i, endpoint in enumerate(endpoints):
                name = endpoint['name']
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(f"Error in {name}: {result}")
                    result_dict[name] = None
                else:
                    result_dict[name] = result

            return result_dict

    async def _make_async_request(self, endpoint: Dict):
        """Make async HTTP request"""
        try:
            self._rate_limit_check()
            async with self.session.get(endpoint['url'], params=endpoint.get('params', {}),
                                      timeout=aiohttp.ClientTimeout(total=5)) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            raise e

    @lru_cache(maxsize=128)
    def _cached_calculation(self, calc_type: str, data_hash: int) -> Dict:
        """Cache expensive calculations"""
        # This will be populated by actual calculations
        return {}

    def get_current_price(self, use_cache: bool = True, cache_ttl: int = None) -> float:
        """Get current BTC price with caching"""
        cache_key = f"price_{self.symbol}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            cache_age = time.time() - self.cache_time.get(cache_key, 0)
            if cache_age < cache_ttl:
                return self.cache[cache_key]
        
        try:
            self._rate_limit_check()
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": self.symbol}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            price = float(data['price'])
            
            # Cache the result
            if use_cache:
                self.cache[cache_key] = price
                self.cache_time[cache_key] = time.time()
            
            return price
        except Exception as e:
            print(f"Error fetching current price: {e}")
            # Return cached value if available, even if expired
            if cache_key in self.cache:
                return self.cache[cache_key]
            return None
    
    def get_ticker_24h(self) -> Dict:
        """Get 24-hour ticker statistics"""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {"symbol": self.symbol}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return {
                'price': float(data['lastPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'high': float(data['highPrice']),
                'low': float(data['lowPrice']),
                'open': float(data['openPrice']),
                'trades': int(data['count'])
            }
        except Exception as e:
            print(f"Error fetching 24h ticker: {e}")
            return None
    
    def get_klines(self, interval: str = "5m", limit: int = 100) -> pd.DataFrame:
        """
        Get historical candlestick data
        
        Args:
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch (max 1000)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                "symbol": self.symbol,
                "interval": interval,
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df.set_index('timestamp', inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"Error fetching klines: {e}")
            return None
    
    def calculate_atr(self, period: int = 14) -> float:
        """Calculate Average True Range (volatility indicator)"""
        try:
            df = self.get_klines(interval="1h", limit=period + 1)
            if df is None or len(df) < period:
                return None
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean().iloc[-1]
            
            return float(atr)
        except Exception as e:
            print(f"Error calculating ATR: {e}")
            return None
    
    def calculate_volatility(self, period: int = 24) -> float:
        """Calculate historical volatility (annualized)"""
        try:
            df = self.get_klines(interval="1h", limit=period + 1)
            if df is None or len(df) < period:
                return None
            
            returns = np.log(df['close'] / df['close'].shift(1))
            volatility = returns.std() * np.sqrt(365 * 24)  # Annualized
            
            return float(volatility)
        except Exception as e:
            print(f"Error calculating volatility: {e}")
            return None
    
    def get_order_book(self, limit: int = 20) -> Dict:
        """Get current order book depth"""
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {
                "symbol": self.symbol,
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            bids = [[float(price), float(qty)] for price, qty in data['bids']]
            asks = [[float(price), float(qty)] for price, qty in data['asks']]
            
            return {
                'bids': bids,
                'asks': asks,
                'bid_price': bids[0][0] if bids else None,
                'ask_price': asks[0][0] if asks else None,
                'spread': asks[0][0] - bids[0][0] if bids and asks else None
            }
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None
    
    def get_market_data(self) -> Dict:
        """
        Get comprehensive market data for trading analysis with error learning
        This replaces the hardcoded get_market_data in the original code
        """
        start_time = time.time()
        operation_context = {
            'operation_type': 'get_market_data',
            'symbol': self.symbol,
            'timeframe': 'current',
            'api_endpoint': 'multiple',
            'rate_limit_status': self.request_count / self.max_requests_per_minute if self.max_requests_per_minute > 0 else 0.1,
            'network_latency': 100,  # Placeholder - could measure actual latency
            'cache_hit_rate': 0.8,   # Placeholder - could calculate actual cache hit rate
            'system_load': 0.5,
            'memory_usage': 0.5
        }

        # Predict error likelihood
        error_prediction = global_error_manager.predict_error_likelihood('data_fetcher', operation_context)

        if not error_prediction['should_attempt']:
            logger.warning(f"[DATA_FETCHER] Avoiding market data fetch due to high error risk: {error_prediction['error_probability']:.1%}")
            logger.info(f"[DATA_FETCHER] Alternatives: {error_prediction['alternative_suggestions']}")

            # Record avoidance and return cached data if available
            record_error('data_fetcher', operation_context, had_error=False,
                        error_details="Proactively avoided due to error prediction",
                        success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']},
                        execution_time=time.time() - start_time)

            # Return cached data or minimal fallback
            if hasattr(self, 'cache') and 'market_data' in self.cache:
                return self.cache['market_data']

            return {
                'btc_price': 50000,
                'error': f'High error risk detected ({error_prediction["error_probability"]:.1%})',
                'fallback': True
            }

        success = False
        error_details = None

        try:
            if self.performance_mode:
                # Concurrent API calls for better performance
                endpoints = [
                    {
                        'name': 'ticker',
                        'url': f"{self.base_url}/api/v3/ticker/24hr",
                        'params': {"symbol": self.symbol},
                        'func': lambda: self._make_request(f"{self.base_url}/api/v3/ticker/24hr", {"symbol": self.symbol})
                    },
                    {
                        'name': 'fear_greed',
                        'url': "https://api.alternative.me/fng/",
                        'params': {},
                        'func': lambda: self._make_request("https://api.alternative.me/fng/")
                    }
                ]

                # Run concurrent calls
                concurrent_results = asyncio.run(self._concurrent_api_calls(endpoints))

                ticker_data = concurrent_results.get('ticker')
                fear_greed_data = concurrent_results.get('fear_greed')

                if ticker_data:
                    ticker = self._parse_ticker_data(ticker_data)
                else:
                    # Fallback to cached/synchronous call
                    ticker = self.get_ticker_24h()

                if fear_greed_data:
                    fear_greed = self._parse_fear_greed_data(fear_greed_data)
                else:
                    fear_greed = self.get_fear_greed_index()
            else:
                # Original sequential approach
                ticker = self.get_ticker_24h()
                fear_greed = self.get_fear_greed_index()

            if not ticker:
                return None

            price = ticker['price']

            # Calculate volatility (with caching)
            volatility = self._get_cached_volatility()

            # Calculate sentiment (simplified - based on price momentum)
            price_change_pct = ticker['price_change_percent'] / 100
            sentiment = 0.5 + (price_change_pct * 2)  # Scale to 0-1
            sentiment = max(0, min(1, sentiment))  # Clamp to 0-1

            # Calculate volume ratio (current vs average)
            volume_ratio = ticker['volume'] / ticker['quote_volume'] * ticker['price'] if ticker['quote_volume'] > 0 else 1.0

            fear_greed_value = int(fear_greed['value']) if fear_greed else 50
            
            success = True
            record_error('data_fetcher', operation_context, had_error=False,
                        success_metrics={
                            'data_fetched': True,
                            'price': price,
                            'volatility': volatility,
                            'sentiment': sentiment
                        },
                        execution_time=time.time() - start_time)

            return {
                'btc_price': price,
                'btc_volatility': volatility,
                'market_sentiment': sentiment,
                'volume_ratio': volume_ratio,
                'fear_greed_value': fear_greed_value
            }

        except Exception as e:
            error_details = str(e)
            record_error('data_fetcher', operation_context, had_error=True,
                        error_details=error_details,
                        execution_time=time.time() - start_time)
            print(f"Error getting market data: {e}")
            return None

    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Synchronous request helper"""
        try:
            self._rate_limit_check()
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

    def _parse_ticker_data(self, data: Dict) -> Dict:
        """Parse ticker data from API response"""
        try:
            return {
                'price': float(data['lastPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'high': float(data['highPrice']),
                'low': float(data['lowPrice']),
                'open': float(data['openPrice']),
                'trades': int(data['count'])
            }
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing ticker data: {e}")
            return None

    def _parse_fear_greed_data(self, data: Dict) -> Optional[Dict]:
        """Parse Fear & Greed Index data"""
        try:
            if data['data']:
                fng = data['data'][0]
                return {
                    'value': int(fng['value']),
                    'classification': fng['value_classification'],
                    'timestamp': datetime.fromtimestamp(int(fng['timestamp']))
                }
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing Fear & Greed data: {e}")
        return None

    def _get_cached_volatility(self) -> float:
        """Get cached volatility calculation"""
        cache_key = f"volatility_{self.symbol}"
        current_time = time.time()

        # Check cache
        if cache_key in self.cache_time:
            cache_age = current_time - self.cache_time[cache_key]
            if cache_age < self.cache_ttl['volatility']:
                return self.cache[cache_key]

        # Calculate and cache
        volatility = self.calculate_volatility()
        if volatility is None:
            volatility = 0.04  # Fallback

        self.cache[cache_key] = volatility
        self.cache_time[cache_key] = current_time

        return volatility

    def get_fear_greed_index(self) -> Optional[Dict]:
        """
        Get Crypto Fear & Greed Index
        Source: Alternative.me API
        """
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data['data']:
                fng = data['data'][0]
                return {
                    'value': int(fng['value']),
                    'classification': fng['value_classification'],
                    'timestamp': datetime.fromtimestamp(int(fng['timestamp']))
                }
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
            return None

    def get_historical_data(self, limit: int = 100, interval: str = "1h") -> Optional[List]:
        """
        Fetch historical OHLCV data from Binance
        Args:
            limit: Number of candles to fetch (max 1000)
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
        Returns:
            List of OHLCV data or None if failed
        """
        try:
            self._rate_limit_check()

            # Binance klines endpoint
            endpoint = "/api/v3/klines"
            params = {
                'symbol': self.symbol,
                'interval': interval,
                'limit': min(limit, 1000)  # Binance max is 1000
            }

            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Convert to OHLCV format
            historical_data = []
            for candle in data:
                historical_data.append({
                    'timestamp': int(candle[0]),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5]),
                    'close_time': int(candle[6]),
                    'quote_volume': float(candle[7]),
                    'trades': int(candle[8])
                })

            return historical_data

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None


# Test the data fetcher
if __name__ == "__main__":
    print("Testing Binance Data Fetcher...")
    print("=" * 60)
    
    fetcher = BinanceDataFetcher()
    
    # Test current price
    print("\n1. Current Price:")
    price = fetcher.get_current_price()
    print(f"   BTC Price: ${price:,.2f}" if price else "   Failed to fetch")
    
    # Test 24h ticker
    print("\n2. 24-Hour Statistics:")
    ticker = fetcher.get_ticker_24h()
    if ticker:
        print(f"   Price: ${ticker['price']:,.2f}")
        print(f"   24h Change: {ticker['price_change_percent']:.2f}%")
        print(f"   24h High: ${ticker['high']:,.2f}")
        print(f"   24h Low: ${ticker['low']:,.2f}")
        print(f"   24h Volume: {ticker['volume']:,.2f} BTC")
    
    # Test volatility
    print("\n3. Volatility:")
    vol = fetcher.calculate_volatility()
    print(f"   Annualized Volatility: {vol*100:.2f}%" if vol else "   Failed to calculate")
    
    # Test ATR
    print("\n4. ATR (Average True Range):")
    atr = fetcher.calculate_atr()
    print(f"   ATR: ${atr:,.2f}" if atr else "   Failed to calculate")
    
    # Test order book
    print("\n5. Order Book:")
    ob = fetcher.get_order_book(limit=5)
    if ob:
        print(f"   Best Bid: ${ob['bid_price']:,.2f}")
        print(f"   Best Ask: ${ob['ask_price']:,.2f}")
        print(f"   Spread: ${ob['spread']:.2f}")
    
    # Test comprehensive market data
    print("\n6. Comprehensive Market Data:")
    market_data = fetcher.get_market_data()
    if market_data:
        print(f"   Price: ${market_data['btc_price']:,.2f}")
        print(f"   Volatility: {market_data['btc_volatility']*100:.2f}%")
        print(f"   Sentiment: {market_data['market_sentiment']:.2f}")
        print(f"   Volume Ratio: {market_data['volume_ratio']:.2f}")
    
    # Test Fear & Greed Index
    print("\n7. Fear & Greed Index:")
    fng = fetcher.get_fear_greed_index()
    if fng:
        print(f"   Value: {fng['value']}/100")
        print(f"   Classification: {fng['classification']}")
    
    print("\n" + "=" * 60)
    print("Data fetcher test complete!")
