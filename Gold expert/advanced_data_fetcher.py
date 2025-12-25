"""
Advanced Data Fetcher for Ultra A+ Filter
Fetches funding rate, BTC dominance, and social sentiment data
"""

import requests
from datetime import datetime
from typing import Dict, Optional


class AdvancedDataFetcher:
    """
    Fetches advanced market data for ultra-strict filtering
    - Funding rate & open interest (Binance Futures)
    - DXY Strength (USD Index)
    - Gold Sentiment (Proxy)
    """
    
    def __init__(self):
        self.binance_futures_url = "https://fapi.binance.com"
        self.coingecko_url = "https://api.coingecko.com/api/v3"
    
    def get_funding_rate(self, symbol: str = "XAUUSDT") -> Optional[Dict]:
        """
        Get current funding rate for Gold perpetual futures
        
        Returns:
            {
                'funding_rate': float,  # Current funding rate (e.g., 0.0001 = 0.01%)
                'next_funding_time': datetime,
                'mark_price': float
            }
        """
        try:
            url = f"{self.binance_futures_url}/fapi/v1/premiumIndex"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return {
                'funding_rate': float(data['lastFundingRate']),
                'next_funding_time': datetime.fromtimestamp(int(data['nextFundingTime']) / 1000),
                'mark_price': float(data['markPrice'])
            }
        except Exception as e:
            print(f"Error fetching funding rate: {e}")
            return None
    
    def get_open_interest(self, symbol: str = "XAUUSDT") -> Optional[Dict]:
        """
        Get total open interest for Gold perpetual futures
        
        Returns:
            {
                'open_interest': float,  # Total open interest in Gold
                'open_interest_value': float,  # Total value in USDT
                'timestamp': datetime
            }
        """
        try:
            url = f"{self.binance_futures_url}/fapi/v1/openInterest"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return {
                'open_interest': float(data['openInterest']),
                'open_interest_value': float(data['openInterest']) * float(data.get('markPrice', 0)),
                'timestamp': datetime.fromtimestamp(int(data['time']) / 1000)
            }
        except Exception as e:
            print(f"Error fetching open interest: {e}")
            return None
    
    def get_dxy_strength(self) -> Optional[Dict]:
        """
        Get DXY (US Dollar Index) Strength
        """
        # Mocking DXY data as no free API is easily available without key
        # In production, connect to a financial data provider
        return {
            'dxy_value': 103.5,
            'trend': 'NEUTRAL'
        }
    
    def get_gold_sentiment(self) -> Optional[Dict]:
        """
        Get Gold sentiment proxy
        """
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data['data']:
                fng = data['data'][0]
                score = int(fng['value'])
                
                return {
                    'sentiment_score': score,
                    'classification': fng['value_classification'],
                    'is_extreme': score < 25 or score > 75,
                    'timestamp': datetime.fromtimestamp(int(fng['timestamp']))
                }
        except Exception as e:
            print(f"Error fetching social sentiment: {e}")
            return None
    
    def get_all_advanced_data(self) -> Dict:
        """
        Get all advanced data in one call
        
        Returns:
            {
                'funding_rate': dict,
                'open_interest': dict,
                'dxy_strength': dict,
                'gold_sentiment': dict
            }
        """
        return {
            'funding_rate': self.get_funding_rate(),
            'open_interest': self.get_open_interest(),
            'dxy_strength': self.get_dxy_strength(),
            'gold_sentiment': self.get_gold_sentiment()
        }


# Test the advanced data fetcher
if __name__ == "__main__":
    print("Testing Advanced Data Fetcher...")
    print("=" * 80)
    
    fetcher = AdvancedDataFetcher()
    
    # Test funding rate
    print("\n1. Funding Rate:")
    funding = fetcher.get_funding_rate()
    if funding:
        print(f"   Funding Rate: {funding['funding_rate']*100:.4f}%")
        print(f"   Mark Price: ${funding['mark_price']:,.2f}")
        print(f"   Next Funding: {funding['next_funding_time']}")
    
    # Test open interest
    print("\n2. Open Interest:")
    oi = fetcher.get_open_interest()
    if oi:
        print(f"   Open Interest: {oi['open_interest']:,.2f} Gold")
        print(f"   OI Value: ${oi['open_interest_value']:,.2f}")
    
    # Test DXY Strength
    print("\n3. DXY Strength:")
    dxy = fetcher.get_dxy_strength()
    if dxy:
        print(f"   DXY Value: {dxy['dxy_value']}")
        print(f"   Trend: {dxy['trend']}")
    
    # Test Gold sentiment
    print("\n4. Gold Sentiment:")
    sentiment = fetcher.get_gold_sentiment()
    if sentiment:
        print(f"   Sentiment Score: {sentiment['sentiment_score']}/100")
        print(f"   Classification: {sentiment['classification']}")
        print(f"   Is Extreme: {sentiment['is_extreme']}")
    
    print("\n" + "=" * 80)
    print("Advanced data fetcher test complete!")
