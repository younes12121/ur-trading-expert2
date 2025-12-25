"""
Financial News Fetcher for Trading System
Fetches important crypto/BTC news to warn before trades
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

class NewsFetcher:
    """
    Fetches BTC news from CoinDesk RSS feed
    100% FREE - No API key needed!
    """
    
    def __init__(self):
        # CoinDesk Bitcoin RSS feed (always free, no key needed)
        self.rss_url = "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml"
        
    def get_crypto_news(self, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get latest BTC news from CoinDesk RSS feed
        100% free, no API key required
        """
        try:
            response = requests.get(self.rss_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # Parse RSS XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            news_items = []
            
            # Find all items in the RSS feed
            for item in root.findall('.//item')[:limit]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pubdate_elem = item.find('pubDate')
                desc_elem = item.find('description')
                
                # Only include Bitcoin-related news
                title = title_elem.text if title_elem is not None else ''
                if 'bitcoin' in title.lower() or 'btc' in title.lower():
                    news_items.append({
                        'title': title,
                        'description': desc_elem.text if desc_elem is not None else '',
                        'published_at': pubdate_elem.text if pubdate_elem is not None else '',
                        'source': 'CoinDesk',
                        'url': link_elem.text if link_elem is not None else ''
                    })
            
            return news_items if news_items else None
                
        except Exception as e:
            # Silently fail - news check is optional
            return None
    
    def check_high_impact_news(self, hours_back: int = 2) -> Dict:
        """
        Check for high-impact news in the last N hours
        Returns warning if important news found
        """
        try:
            news = self.get_crypto_news(limit=20)
            
            # If news API unavailable, assume safe (don't block trades)
            if not news:
                return {
                    'has_high_impact': False,
                    'warning': None,  # No warning if we just can't fetch news
                    'news_count': 0,
                    'recent_news': []
                }
            
            # Filter news from last N hours
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_news = []
            
            for item in news:
                try:
                    # Parse RSS date format: "Mon, 25 Nov 2025 18:30:00 +0000"
                    pub_time_str = item['published_at']
                    pub_time = datetime.strptime(pub_time_str, "%a, %d %b %Y %H:%M:%S %z")
                    pub_time = pub_time.replace(tzinfo=None)  # Remove timezone for comparison
                    
                    if pub_time > cutoff_time:
                        recent_news.append(item)
                except:
                    # If can't parse time, skip it (don't include to avoid false positives)
                    pass
            
            # Determine if high impact
            # Consider it high impact if there are 2+ Bitcoin news items in the timeframe
            has_high_impact = len(recent_news) >= 2
            
            if has_high_impact:
                warning = f"⚠️ {len(recent_news)} BTC news item(s) in last {hours_back} hours!"
            else:
                warning = None
            
            return {
                'has_high_impact': has_high_impact,
                'warning': warning,
                'news_count': len(recent_news),
                'recent_news': recent_news[:5]  # Top 5 most recent
            }
            
        except Exception as e:
            # If error, don't block trades
            return {
                'has_high_impact': False,
                'warning': None,
                'news_count': 0,
                'recent_news': []
            }
    
    def get_news_summary(self) -> str:
        """
        Get a formatted summary of recent important news
        """
        news_check = self.check_high_impact_news(hours_back=4)
        
        if not news_check['recent_news']:
            return "✅ No major BTC news in the last 4 hours - Safe to trade"
        
        summary = f"\n📰 IMPORTANT BTC NEWS (Last 4 hours):\n"
        summary += "=" * 80 + "\n"
        
        for i, item in enumerate(news_check['recent_news'], 1):
            summary += f"\n{i}. {item['title']}\n"
            summary += f"   Source: {item['source']} | Time: {item['published_at']}\n"
            if item.get('description'):
                desc = item['description'][:150] + "..." if len(item['description']) > 150 else item['description']
                # Remove HTML tags if present
                import re
                desc = re.sub('<[^<]+?>', '', desc)
                summary += f"   {desc}\n"
        
        summary += "\n" + "=" * 80
        summary += "\n⚠️ CAUTION: Trade carefully during news events!"
        
        return summary


# Alternative: Using NewsAPI (requires free API key)
class NewsAPIFetcher:
    """
    Alternative news fetcher using NewsAPI.org
    Requires free API key from https://newsapi.org/
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "YOUR_NEWSAPI_KEY_HERE"
        self.base_url = "https://newsapi.org/v2/everything"
    
    def get_btc_news(self, hours_back: int = 4) -> Optional[List[Dict]]:
        """
        Get BTC-related news from NewsAPI
        """
        if self.api_key == "YOUR_NEWSAPI_KEY_HERE":
            print("⚠️ NewsAPI key not configured. Using CryptoPanic instead.")
            return None
        
        try:
            from_date = (datetime.now() - timedelta(hours=hours_back)).isoformat()
            
            params = {
                'q': 'Bitcoin OR BTC',
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                news_items = []
                for article in articles[:10]:
                    news_items.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'url': article.get('url', '')
                    })
                
                return news_items
            else:
                print(f"NewsAPI returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return None


# Test the news fetcher
if __name__ == "__main__":
    print("Testing News Fetcher...")
    print("=" * 80)
    
    fetcher = NewsFetcher()
    
    print("\n1. Getting latest crypto news:")
    news = fetcher.get_crypto_news(limit=5)
    
    if news:
        for i, item in enumerate(news, 1):
            print(f"\n{i}. {item['title']}")
            print(f"   Source: {item['source']}")
            print(f"   Time: {item['published_at']}")
    else:
        print("   Failed to fetch news")
    
    print("\n\n2. Checking for high-impact news:")
    impact_check = fetcher.check_high_impact_news(hours_back=4)
    print(f"   High Impact: {impact_check['has_high_impact']}")
    print(f"   News Count: {impact_check['news_count']}")
    if impact_check['warning']:
        print(f"   Warning: {impact_check['warning']}")
    
    print("\n\n3. News Summary:")
    summary = fetcher.get_news_summary()
    print(summary)
    
    print("\n" + "=" * 80)
    print("News fetcher test complete!")
