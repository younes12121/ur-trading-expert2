"""
Real-time data fetcher for BTC trading system
Fetches live market data from Binance API
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import config

class BinanceDataFetcher:
    """Fetches real-time and historical data from Binance"""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.base_url = config.BINANCE_TESTNET_URL if config.USE_TESTNET else config.BINANCE_BASE_URL
        self.cache = {}
        self.cache_time = {}
        
    def get_current_price(self) -> float:
        """Get current BTC price"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": self.symbol}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"Error fetching current price: {e}")
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
        Get comprehensive market data for trading analysis
        This replaces the hardcoded get_market_data in the original code
        """
        try:
            # Get current price and 24h stats
            ticker = self.get_ticker_24h()
            if not ticker:
                return None
            
            price = ticker['price']
            
            # Calculate volatility
            volatility = self.calculate_volatility()
            if volatility is None:
                volatility = 0.04  # Fallback
            
            # Calculate sentiment (simplified - based on price momentum)
            price_change_pct = ticker['price_change_percent'] / 100
            sentiment = 0.5 + (price_change_pct * 2)  # Scale to 0-1
            sentiment = max(0, min(1, sentiment))  # Clamp to 0-1
            
            # Calculate volume ratio (current vs average)
            volume_ratio = ticker['volume'] / ticker['quote_volume'] * ticker['price'] if ticker['quote_volume'] > 0 else 1.0
            
            # Get Fear & Greed Index
            fear_greed = self.get_fear_greed_index()
            fear_greed_value = int(fear_greed['value']) if fear_greed else 50
            
            return {
                'btc_price': price,
                'btc_volatility': volatility,
                'market_sentiment': sentiment,
                'volume_ratio': volume_ratio,
                'fear_greed_value': fear_greed_value
            }
            
        except Exception as e:
            print(f"Error getting market data: {e}")
            return None
    
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
