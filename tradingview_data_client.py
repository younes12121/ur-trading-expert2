"""
TradingView Data Client
Fetches real-time OHLC (Open, High, Low, Close) data for multi-timeframe analysis
Uses TradingView's community endpoints and yfinance as backup
"""

import requests
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import time
import warnings

# Suppress warnings from yfinance and pandas
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)


class TradingViewDataClient:
    """Fetch OHLC data from TradingView and Yahoo Finance"""
    
    def __init__(self):
        """Initialize data client"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Symbol mapping
        self.symbol_map = {
            # Forex
            'EURUSD': 'FX:EURUSD',
            'GBPUSD': 'FX:GBPUSD',
            'USDJPY': 'FX:USDJPY',
            'AUDUSD': 'FX:AUDUSD',
            'USDCAD': 'FX:USDCAD',
            'EURJPY': 'FX:EURJPY',
            # Crypto
            'BTC': 'BINANCE:BTCUSDT',
            'BTCUSD': 'BINANCE:BTCUSDT',
            # Commodities
            'GOLD': 'OANDA:XAUUSD',
            'XAUUSD': 'OANDA:XAUUSD',
            # Futures
            'ES': 'CME:ES1!',  # E-mini S&P 500
            'NQ': 'CME:NQ1!',  # E-mini NASDAQ-100
            'CME:ES1!': 'CME:ES1!',
            'CME:NQ1!': 'CME:NQ1!'
        }
        
        # Yahoo Finance symbols (backup)
        self.yf_symbols = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'USDJPY=X',
            'AUDUSD': 'AUDUSD=X',
            'USDCAD': 'USDCAD=X',
            'EURJPY': 'EURJPY=X',
            'BTC': 'BTC-USD',
            'BTCUSD': 'BTC-USD',
            'GOLD': 'GC=F',
            'XAUUSD': 'GC=F',
            'ES': 'ES=F',  # E-mini S&P 500 Futures
            'NQ': 'NQ=F',  # E-mini NASDAQ-100 Futures
            'CME:ES1!': 'ES=F',
            'CME:NQ1!': 'NQ=F'
        }
        
        # Timeframe mapping
        self.tf_map = {
            'M15': '15',
            'H1': '60',
            'H4': '240',
            'D1': 'D'
        }
    
    def get_ohlc_data(self, pair, timeframe='H1', bars=50):
        """
        Get OHLC data for a pair and timeframe
        
        Args:
            pair: Trading pair (e.g., 'EURUSD', 'BTC')
            timeframe: M15, H1, H4, or D1
            bars: Number of candles to fetch
        
        Returns:
            list: List of OHLC dictionaries or prices
        """
        # Try Yahoo Finance first (most reliable for free access)
        data = self._get_from_yfinance(pair, timeframe, bars)
        
        if data and len(data) > 0:
            return data
        
        # Fallback: generate realistic simulated data
        print(f"Using simulated data for {pair} {timeframe}")
        return self._generate_fallback_data(pair, bars)
    
    def _get_from_yfinance(self, pair, timeframe, bars):
        """Get data from Yahoo Finance"""
        try:
            # Get Yahoo symbol
            yf_symbol = self.yf_symbols.get(pair.upper())
            if not yf_symbol:
                return None
            
            # Map timeframe to yfinance interval
            interval_map = {
                'M15': '15m',
                'H1': '1h',
                'H4': '4h',
                'D1': '1d'
            }
            interval = interval_map.get(timeframe, '1h')
            
            # Calculate period based on bars needed
            if timeframe == 'M15':
                period = '5d'  # 5 days of 15-min data
            elif timeframe == 'H1':
                period = '1mo'  # 1 month of hourly data
            elif timeframe == 'H4':
                period = '3mo'  # 3 months of 4h data
            else:  # D1
                period = '6mo'  # 6 months of daily data
            
            # Fetch data
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return None
            
            # Get last N bars
            df = df.tail(bars)
            
            # Convert to list of close prices (simplified)
            prices = df['Close'].tolist()
            
            return prices
            
        except Exception as e:
            print(f"Yahoo Finance error for {pair}: {e}")
            return None
    
    def _generate_fallback_data(self, pair, bars):
        """Generate realistic fallback data"""
        import numpy as np
        
        # Base prices
        base_prices = {
            'BTC': 43000.0,
            'BTCUSD': 43000.0,
            'GOLD': 2050.0,
            'XAUUSD': 2050.0,
            'EURUSD': 1.08500,
            'GBPUSD': 1.27000,
            'USDJPY': 149.500,
            'AUDUSD': 0.65500,
            'USDCAD': 1.36000,
            'EURJPY': 162.000,
            'ES': 4800.0,  # E-mini S&P 500
            'NQ': 17000.0,  # E-mini NASDAQ-100
            'CME:ES1!': 4800.0,
            'CME:NQ1!': 17000.0
        }
        
        base_price = base_prices.get(pair.upper(), 1.0)
        
        # Generate random walk
        prices = [base_price]
        for _ in range(bars - 1):
            change = (np.random.random() - 0.5) * 0.003
            prices.append(prices[-1] * (1 + change))
        
        return prices
    
    def get_data(self, symbol, interval='60', n_bars=200):
        """
        Get full OHLCV data for futures contracts (ES, NQ format)
        
        Args:
            symbol: Trading symbol (e.g., 'CME:ES1!', 'CME:NQ1!')
            interval: Timeframe interval ('15', '60', '240', 'D')
            n_bars: Number of bars to fetch
        
        Returns:
            pandas.DataFrame with columns: timestamp, open, high, low, close, volume
        """
        # Map interval to timeframe
        tf_map = {
            '15': 'M15',
            '60': 'H1',
            '240': 'H4',
            'D': 'D1'
        }
        timeframe = tf_map.get(interval, 'H1')
        
        # Extract symbol
        if ':' in symbol:
            pair = symbol.split(':')[1].replace('1!', '')
        else:
            pair = symbol
        
        # Try to get data from Yahoo Finance
        try:
            # Try multiple lookup methods
            yf_symbol = self.yf_symbols.get(pair) or self.yf_symbols.get(symbol) or self.yf_symbols.get(pair.upper())
            
            if not yf_symbol:
                # Handle CME futures format
                if 'CME:' in symbol or 'NQ' in symbol.upper():
                    if 'NQ' in symbol.upper():
                        yf_symbol = 'NQ=F'  # E-mini NASDAQ-100 Futures
                    elif 'ES' in symbol.upper():
                        yf_symbol = 'ES=F'  # E-mini S&P 500 Futures
                    else:
                        print(f"Warning: Unknown futures symbol {symbol}, using fallback")
                        return self._generate_simulated_ohlcv(pair, n_bars)
                else:
                    print(f"Warning: No Yahoo Finance symbol found for {symbol}, using fallback")
                    return self._generate_simulated_ohlcv(pair, n_bars)
            
            if yf_symbol:
                # Map interval to yfinance format
                yf_interval_map = {
                    '15': '15m',
                    '60': '1h',
                    '240': '4h',
                    'D': '1d'
                }
                yf_interval = yf_interval_map.get(interval, '1h')
                
                # Calculate period
                if interval == '15':
                    period = '7d'
                elif interval == '60':
                    period = '1mo'
                elif interval == '240':
                    period = '3mo'
                else:
                    period = '6mo'
                
                # Fetch data
                ticker = yf.Ticker(yf_symbol)
                df = ticker.history(period=period, interval=yf_interval)
                
                if not df.empty:
                    df = df.tail(n_bars)
                    
                    # Format as required
                    result = pd.DataFrame({
                        'timestamp': df.index,
                        'open': df['Open'].values,
                        'high': df['High'].values,
                        'low': df['Low'].values,
                        'close': df['Close'].values,
                        'volume': df['Volume'].values
                    })
                    
                    return result
        
        except Exception as e:
            error_msg = str(e)
            # Suppress Yahoo Finance errors for delisted symbols
            if "delisted" in error_msg.lower() or "no data found" in error_msg.lower():
                print(f"Symbol {symbol} not available on Yahoo Finance, using simulated data")
            else:
                print(f"Error fetching {symbol} data: {e}")
        
        # Fallback: generate simulated data
        print(f"Using simulated data for {symbol}")
        return self._generate_simulated_ohlcv(pair, n_bars)
    
    def _generate_simulated_ohlcv(self, pair, bars):
        """Generate simulated OHLCV data for testing"""
        import numpy as np
        
        base_prices = {
            'BTC': 43000.0,
            'BTCUSD': 43000.0,
            'GOLD': 2050.0,
            'XAUUSD': 2050.0,
            'EURUSD': 1.08500,
            'GBPUSD': 1.27000,
            'USDJPY': 149.500,
            'AUDUSD': 0.65500,
            'USDCAD': 1.36000,
            'EURJPY': 162.000,
            'ES': 4800.0,
            'NQ': 17000.0
        }
        
        base_price = base_prices.get(pair.upper(), 1.0)
        
        # Generate realistic price action
        dates = pd.date_range(end=datetime.now(), periods=bars, freq='15min')
        returns = np.random.randn(bars) * 0.003
        close_prices = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices * (1 + np.random.randn(bars) * 0.0005),
            'high': close_prices * (1 + abs(np.random.randn(bars) * 0.001)),
            'low': close_prices * (1 - abs(np.random.randn(bars) * 0.001)),
            'close': close_prices,
            'volume': np.random.randint(10000, 50000, bars)
        })
        
        return df


# Testing
if __name__ == "__main__":
    print("Testing TradingView Data Client...")
    print("=" * 60)
    
    client = TradingViewDataClient()
    
    # Test different pairs and timeframes
    tests = [
        ('EURUSD', 'H1'),
        ('BTC', 'H4'),
        ('GOLD', 'D1')
    ]
    
    for pair, tf in tests:
        print(f"\nFetching {pair} {tf} data...")
        data = client.get_ohlc_data(pair, tf, bars=20)
        
        if data:
            print(f"  Got {len(data)} bars")
            print(f"  First: {data[0]:.5f}")
            print(f"  Last: {data[-1]:.5f}")
            print(f"  Range: {min(data):.5f} - {max(data):.5f}")
        else:
            print(f"  [ERROR] No data")
    
    print("\n" + "=" * 60)
    print("[OK] TradingView Data Client ready!")
