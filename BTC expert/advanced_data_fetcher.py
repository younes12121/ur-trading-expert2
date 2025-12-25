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
    - BTC dominance & ETH/BTC ratio (CoinGecko)
    - Social sentiment (Google Trends proxy via Fear & Greed)
    """
    
    def __init__(self):
        self.binance_futures_url = "https://fapi.binance.com"
        self.coingecko_url = "https://api.coingecko.com/api/v3"
    
    def get_funding_rate(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        Get current funding rate for BTC perpetual futures
        
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
    
    def get_open_interest(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        Get total open interest for BTC perpetual futures
        
        Returns:
            {
                'open_interest': float,  # Total open interest in BTC
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
    
    def get_btc_dominance(self) -> Optional[Dict]:
        """
        Get BTC market dominance
        
        Returns:
            {
                'btc_dominance': float,  # BTC dominance % (e.g., 45.5)
                'eth_dominance': float,  # ETH dominance %
                'total_market_cap': float  # Total crypto market cap
            }
        """
        try:
            url = f"{self.coingecko_url}/global"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()['data']
            
            return {
                'btc_dominance': float(data['market_cap_percentage'].get('btc', 0)),
                'eth_dominance': float(data['market_cap_percentage'].get('eth', 0)),
                'total_market_cap': float(data['total_market_cap'].get('usd', 0))
            }
        except Exception as e:
            print(f"Error fetching BTC dominance: {e}")
            return None
    
    def get_eth_btc_ratio(self) -> Optional[float]:
        """
        Get ETH/BTC price ratio
        
        Returns:
            float: ETH price in BTC (e.g., 0.05 means 1 ETH = 0.05 BTC)
        """
        try:
            url = f"{self.coingecko_url}/simple/price"
            params = {
                'ids': 'ethereum',
                'vs_currencies': 'btc'
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return float(data['ethereum']['btc'])
        except Exception as e:
            print(f"Error fetching ETH/BTC ratio: {e}")
            return None
    
    def get_social_sentiment(self) -> Optional[Dict]:
        """
        Get social sentiment proxy using Fear & Greed Index
        (Google Trends requires pytrends library, using F&G as simpler alternative)
        
        Returns:
            {
                'sentiment_score': int,  # 0-100 (0=extreme fear, 100=extreme greed)
                'classification': str,  # 'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'
                'is_extreme': bool  # True if <25 or >75
            }
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
                'btc_dominance': dict,
                'eth_btc_ratio': float,
                'social_sentiment': dict
            }
        """
        return {
            'funding_rate': self.get_funding_rate(),
            'open_interest': self.get_open_interest(),
            'btc_dominance': self.get_btc_dominance(),
            'eth_btc_ratio': self.get_eth_btc_ratio(),
            'social_sentiment': self.get_social_sentiment()
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
        print(f"   Open Interest: {oi['open_interest']:,.2f} BTC")
        print(f"   OI Value: ${oi['open_interest_value']:,.2f}")
    
    # Test BTC dominance
    print("\n3. BTC Dominance:")
    dom = fetcher.get_btc_dominance()
    if dom:
        print(f"   BTC Dominance: {dom['btc_dominance']:.2f}%")
        print(f"   ETH Dominance: {dom['eth_dominance']:.2f}%")
        print(f"   Total Market Cap: ${dom['total_market_cap']:,.0f}")
    
    # Test ETH/BTC ratio
    print("\n4. ETH/BTC Ratio:")
    ratio = fetcher.get_eth_btc_ratio()
    if ratio:
        print(f"   ETH/BTC: {ratio:.6f}")
    
    # Test social sentiment
    print("\n5. Social Sentiment:")
    sentiment = fetcher.get_social_sentiment()
    if sentiment:
        print(f"   Sentiment Score: {sentiment['sentiment_score']}/100")
        print(f"   Classification: {sentiment['classification']}")
        print(f"   Is Extreme: {sentiment['is_extreme']}")
    
    print("\n" + "=" * 80)
    print("Advanced data fetcher test complete!")
