"""
Historical Data Manager
Downloads and manages historical OHLCV data from Binance
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from typing import Optional
import config

class HistoricalDataManager:
    """Manages historical price data from Binance"""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.base_url = config.BINANCE_BASE_URL
        self.cache_dir = "data_cache"
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def download_klines(self, interval: str = "5m", limit: int = 1000, 
                       start_time: Optional[int] = None, 
                       end_time: Optional[int] = None) -> pd.DataFrame:
        """
        Download historical kline/candlestick data from Binance
        
        Args:
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles (max 1000 per request)
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        
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
            
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time
            
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
            print(f"Error downloading klines: {e}")
            return None
    
    def download_historical_data(self, interval: str = "5m", days: int = 30) -> pd.DataFrame:
        """
        Download multiple days of historical data
        
        Args:
            interval: Kline interval
            days: Number of days to download
        
        Returns:
            DataFrame with complete historical data
        """
        print(f"📊 Downloading {days} days of {interval} data for {self.symbol}...")
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Convert to milliseconds
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        # Binance allows max 1000 candles per request
        # Calculate how many requests we need
        interval_ms = self._interval_to_milliseconds(interval)
        total_candles = (end_ms - start_ms) // interval_ms
        
        all_data = []
        current_start = start_ms
        
        request_count = 0
        while current_start < end_ms:
            # Download batch
            df = self.download_klines(
                interval=interval,
                limit=1000,
                start_time=current_start,
                end_time=end_ms
            )
            
            if df is None or len(df) == 0:
                break
            
            all_data.append(df)
            request_count += 1
            
            # Update start time for next batch
            current_start = int(df.index[-1].timestamp() * 1000) + interval_ms
            
            print(f"   Downloaded batch {request_count}: {len(df)} candles")
            
            # Small delay to avoid rate limits
            import time
            time.sleep(0.1)
        
        if not all_data:
            print("❌ Failed to download data")
            return None
        
        # Combine all batches
        combined_df = pd.concat(all_data)
        combined_df = combined_df[~combined_df.index.duplicated(keep='first')]
        combined_df.sort_index(inplace=True)
        
        print(f"✅ Downloaded {len(combined_df)} candles from {combined_df.index[0]} to {combined_df.index[-1]}")
        
        return combined_df
    
    def _interval_to_milliseconds(self, interval: str) -> int:
        """Convert interval string to milliseconds"""
        intervals = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
        }
        return intervals.get(interval, 5 * 60 * 1000)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = None):
        """Save data to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.symbol}_{timestamp}.csv"
        
        filepath = os.path.join(self.cache_dir, filename)
        df.to_csv(filepath)
        print(f"💾 Saved data to {filepath}")
        return filepath
    
    def load_from_csv(self, filename: str) -> pd.DataFrame:
        """Load data from CSV file"""
        filepath = os.path.join(self.cache_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return None
        
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        print(f"📂 Loaded {len(df)} candles from {filepath}")
        return df
    
    def get_cached_data(self, interval: str = "5m", max_age_hours: int = 24) -> Optional[pd.DataFrame]:
        """Get cached data if available and recent"""
        cache_file = f"{self.symbol}_{interval}_cache.csv"
        cache_path = os.path.join(self.cache_dir, cache_file)
        
        if not os.path.exists(cache_path):
            return None
        
        # Check file age
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age_hours = (datetime.now() - file_time).total_seconds() / 3600
        
        if age_hours > max_age_hours:
            print(f"⚠️  Cache is {age_hours:.1f} hours old, downloading fresh data...")
            return None
        
        print(f"✅ Using cached data ({age_hours:.1f} hours old)")
        return self.load_from_csv(cache_file)
    
    def get_data(self, interval: str = "5m", days: int = 30, use_cache: bool = True) -> pd.DataFrame:
        """
        Get historical data (from cache or download)
        
        Args:
            interval: Kline interval
            days: Number of days
            use_cache: Whether to use cached data
        
        Returns:
            DataFrame with OHLCV data
        """
        # Try cache first
        if use_cache:
            cached = self.get_cached_data(interval)
            if cached is not None:
                return cached
        
        # Download fresh data
        df = self.download_historical_data(interval, days)
        
        if df is not None:
            # Save to cache
            cache_file = f"{self.symbol}_{interval}_cache.csv"
            self.save_to_csv(df, cache_file)
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> dict:
        """Validate data quality"""
        issues = []
        
        # Check for missing values
        if df.isnull().any().any():
            issues.append("Contains missing values")
        
        # Check for duplicates
        if df.index.duplicated().any():
            issues.append("Contains duplicate timestamps")
        
        # Check for gaps
        expected_freq = pd.infer_freq(df.index)
        if expected_freq is None:
            issues.append("Irregular time intervals detected")
        
        # Check for outliers (price changes > 20%)
        returns = df['close'].pct_change()
        if (abs(returns) > 0.2).any():
            issues.append("Extreme price changes detected (>20%)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'rows': len(df),
            'start': df.index[0],
            'end': df.index[-1],
            'columns': list(df.columns)
        }


# Test the historical data manager
if __name__ == "__main__":
    print("=" * 70)
    print("Testing Historical Data Manager")
    print("=" * 70)
    
    manager = HistoricalDataManager()
    
    # Download 7 days of 5-minute data
    print("\n1. Downloading 7 days of 5-minute data...")
    df = manager.get_data(interval="5m", days=7, use_cache=False)
    
    if df is not None:
        print(f"\n📊 Data Summary:")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Start: {df.index[0]}")
        print(f"   End: {df.index[-1]}")
        print(f"\n   First few rows:")
        print(df.head())
        print(f"\n   Last few rows:")
        print(df.tail())
        
        # Validate data
        print(f"\n2. Validating data...")
        validation = manager.validate_data(df)
        print(f"   Valid: {validation['valid']}")
        if validation['issues']:
            print(f"   Issues: {', '.join(validation['issues'])}")
        
        # Calculate some basic stats
        print(f"\n3. Basic Statistics:")
        print(f"   Price Range: ${df['low'].min():,.2f} - ${df['high'].max():,.2f}")
        print(f"   Average Close: ${df['close'].mean():,.2f}")
        print(f"   Total Volume: {df['volume'].sum():,.2f} BTC")
        
        print("\n" + "=" * 70)
        print("✅ Historical data manager working!")
        print("=" * 70)
