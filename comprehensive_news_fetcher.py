"""
Comprehensive News Fetcher for All Trading Assets
Covers: Crypto, Commodities, Forex, and Futures
Uses multiple free sources - No API key required!
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except:
    HAS_BS4 = False

try:
    import feedparser
    HAS_FEEDPARSER = True
except:
    HAS_FEEDPARSER = False


class ComprehensiveNewsFetcher:
    """
    Fetches news for all asset types:
    - Crypto (Bitcoin, general crypto)
    - Commodities (Gold, Oil, etc.)
    - Forex (Currency news)
    - Futures (Stock indexes: S&P 500, NASDAQ)
    """
    
    def __init__(self):
        # RSS Feeds (Free, no API key needed)
        self.feeds = {
            'crypto': [
                'https://www.coindesk.com/arc/outboundfeeds/rss/',
                'https://cointelegraph.com/rss',
            ],
            'commodities': [
                'https://www.kitco.com/rss/KitcoNewsAll.xml',
            ],
            'forex': [
                'https://www.forexlive.com/feed/news',
            ],
            'futures': [
                'https://finance.yahoo.com/news/rss/',
            ]
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_crypto_news(self, limit: int = 10) -> List[Dict]:
        """Get latest cryptocurrency news (Bitcoin, Ethereum, etc.)"""
        all_news = []
        
        for feed_url in self.feeds['crypto']:
            try:
                news = self._fetch_rss_feed(feed_url, limit=limit)
                all_news.extend(news)
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        
        # Sort by date and return top items
        all_news = sorted(all_news, key=lambda x: x['published_at'], reverse=True)
        return all_news[:limit]
    
    def get_commodities_news(self, limit: int = 10) -> List[Dict]:
        """Get latest commodities news (Gold, Silver, Oil, etc.)"""
        all_news = []
        
        for feed_url in self.feeds['commodities']:
            try:
                news = self._fetch_rss_feed(feed_url, limit=limit)
                all_news.extend(news)
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        
        # Filter for gold-specific news
        gold_news = [n for n in all_news if any(keyword in n['title'].lower() 
                     for keyword in ['gold', 'xau', 'precious metal'])]
        
        if gold_news:
            return gold_news[:limit]
        
        return all_news[:limit]
    
    def get_forex_news(self, limit: int = 10, pair: Optional[str] = None) -> List[Dict]:
        """Get latest forex/currency news"""
        all_news = []
        
        for feed_url in self.feeds['forex']:
            try:
                news = self._fetch_rss_feed(feed_url, limit=limit * 2)
                all_news.extend(news)
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        
        # If specific pair requested, filter
        if pair:
            pair = pair.upper()
            keywords = [pair, pair[:3], pair[3:]]  # e.g., EURUSD, EUR, USD
            filtered = [n for n in all_news if any(kw in n['title'].upper() for kw in keywords)]
            if filtered:
                return filtered[:limit]
        
        return all_news[:limit]
    
    def get_futures_news(self, limit: int = 10, contract: Optional[str] = None) -> List[Dict]:
        """Get latest futures/stock market news (ES, NQ, etc.)"""
        all_news = []
        
        for feed_url in self.feeds['futures']:
            try:
                news = self._fetch_rss_feed(feed_url, limit=limit * 2)
                all_news.extend(news)
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        
        # Filter for stock market / index news
        if contract:
            contract = contract.upper()
            keywords = {
                'ES': ['s&p 500', 's&p', 'spx', 'stock market', 'dow'],
                'NQ': ['nasdaq', 'tech stocks', 'technology', 'nasdaq-100']
            }
            
            filter_keywords = keywords.get(contract, [contract])
            filtered = [n for n in all_news if any(kw in n['title'].lower() for kw in filter_keywords)]
            if filtered:
                return filtered[:limit]
        
        # Return general market news
        market_news = [n for n in all_news if any(keyword in n['title'].lower() 
                      for keyword in ['stock', 'market', 's&p', 'nasdaq', 'dow', 'fed', 'inflation'])]
        
        return market_news[:limit] if market_news else all_news[:limit]
    
    def get_all_news(self, limit_per_category: int = 5) -> Dict[str, List[Dict]]:
        """Get news for all asset categories"""
        return {
            'crypto': self.get_crypto_news(limit=limit_per_category),
            'commodities': self.get_commodities_news(limit=limit_per_category),
            'forex': self.get_forex_news(limit=limit_per_category),
            'futures': self.get_futures_news(limit=limit_per_category)
        }
    
    def _fetch_rss_feed(self, feed_url: str, limit: int = 10) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            # Try feedparser first if available
            if HAS_FEEDPARSER:
                return self._fetch_with_feedparser(feed_url, limit)
            else:
                return self._fetch_with_xml(feed_url, limit)
            
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
            return []
    
    def _fetch_with_feedparser(self, feed_url: str, limit: int = 10) -> List[Dict]:
        """Fetch using feedparser library"""
        import feedparser
        feed = feedparser.parse(feed_url)
        
        news_items = []
        
        for entry in feed.entries[:limit * 2]:
            try:
                # Parse published date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_time = datetime(*entry.updated_parsed[:6])
                else:
                    pub_time = datetime.now()
                
                # Get description
                description = ''
                if hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'description'):
                    description = entry.description
                
                # Clean HTML from description
                if description and HAS_BS4:
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.get_text()[:200]
                    except:
                        pass
                
                news_items.append({
                    'title': entry.title if hasattr(entry, 'title') else 'No title',
                    'description': description,
                    'published_at': pub_time,
                    'source': feed.feed.title if hasattr(feed.feed, 'title') else 'News',
                    'url': entry.link if hasattr(entry, 'link') else ''
                })
                
            except Exception as e:
                continue
        
        return news_items
    
    def _fetch_with_xml(self, feed_url: str, limit: int = 10) -> List[Dict]:
        """Fallback: Fetch using basic XML parsing"""
        response = self.session.get(feed_url, timeout=10)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        news_items = []
        
        # Try to find items
        for item in root.findall('.//item')[:limit]:
            try:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pubdate_elem = item.find('pubDate')
                desc_elem = item.find('description')
                
                title = title_elem.text if title_elem is not None else 'No title'
                description = desc_elem.text if desc_elem is not None else ''
                url = link_elem.text if link_elem is not None else ''
                
                # Try to parse date
                try:
                    if pubdate_elem is not None and pubdate_elem.text:
                        pub_time = datetime.strptime(pubdate_elem.text, "%a, %d %b %Y %H:%M:%S %z")
                        pub_time = pub_time.replace(tzinfo=None)
                    else:
                        pub_time = datetime.now()
                except:
                    pub_time = datetime.now()
                
                news_items.append({
                    'title': title,
                    'description': description[:200] if description else '',
                    'published_at': pub_time,
                    'source': 'News',
                    'url': url
                })
            except:
                continue
        
        return news_items
    
    def check_high_impact_news(self, asset_type: str, hours_back: int = 2) -> Dict:
        """
        Check for high-impact news in the last N hours for specific asset type
        
        Args:
            asset_type: 'crypto', 'commodities', 'forex', or 'futures'
            hours_back: How many hours to look back
        
        Returns:
            Dict with has_high_impact, warning, and recent news
        """
        try:
            # Get news based on asset type
            if asset_type == 'crypto':
                news = self.get_crypto_news(limit=20)
            elif asset_type == 'commodities':
                news = self.get_commodities_news(limit=20)
            elif asset_type == 'forex':
                news = self.get_forex_news(limit=20)
            elif asset_type == 'futures':
                news = self.get_futures_news(limit=20)
            else:
                return {'has_high_impact': False, 'warning': None, 'news_count': 0, 'recent_news': []}
            
            if not news:
                return {'has_high_impact': False, 'warning': None, 'news_count': 0, 'recent_news': []}
            
            # Filter recent news
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_news = [
                n for n in news 
                if isinstance(n['published_at'], datetime) and n['published_at'] > cutoff_time
            ]
            
            # Determine impact
            has_high_impact = len(recent_news) >= 2
            
            warning = None
            if has_high_impact:
                warning = f"⚠️ {len(recent_news)} recent {asset_type} news items in last {hours_back}h"
            
            return {
                'has_high_impact': has_high_impact,
                'warning': warning,
                'news_count': len(recent_news),
                'recent_news': recent_news[:5]  # Top 5 most recent
            }
            
        except Exception as e:
            print(f"Error checking high impact news: {e}")
            return {'has_high_impact': False, 'warning': None, 'news_count': 0, 'recent_news': []}
    
    def get_news_by_asset(self, asset: str, limit: int = 5) -> List[Dict]:
        """
        Get news for a specific asset
        
        Args:
            asset: BTC, GOLD, EURUSD, ES, NQ, etc.
        
        Returns:
            List of relevant news items
        """
        asset = asset.upper()
        
        # Map asset to category and get news
        if asset in ['BTC', 'BITCOIN', 'ETH', 'ETHEREUM']:
            return self.get_crypto_news(limit=limit)
        elif asset in ['GOLD', 'XAUUSD', 'SILVER', 'OIL']:
            return self.get_commodities_news(limit=limit)
        elif asset in ['ES', 'NQ', 'YM', 'RTY']:
            return self.get_futures_news(limit=limit, contract=asset)
        else:
            # Assume forex
            return self.get_forex_news(limit=limit, pair=asset)


# Testing
if __name__ == "__main__":
    print("=" * 70)
    print("🗞️  COMPREHENSIVE NEWS FETCHER TEST")
    print("=" * 70)
    print()
    
    fetcher = ComprehensiveNewsFetcher()
    
    # Test each category
    categories = [
        ('Crypto', 'crypto'),
        ('Commodities', 'commodities'),
        ('Forex', 'forex'),
        ('Futures', 'futures')
    ]
    
    for name, cat in categories:
        print(f"\n📰 {name} News:")
        print("-" * 70)
        
        if cat == 'crypto':
            news = fetcher.get_crypto_news(limit=3)
        elif cat == 'commodities':
            news = fetcher.get_commodities_news(limit=3)
        elif cat == 'forex':
            news = fetcher.get_forex_news(limit=3)
        else:
            news = fetcher.get_futures_news(limit=3)
        
        if news:
            for i, item in enumerate(news[:3], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   Source: {item['source']}")
                if isinstance(item['published_at'], datetime):
                    print(f"   Time: {item['published_at'].strftime('%Y-%m-%d %H:%M')}")
        else:
            print("   No news available")
    
    print("\n" + "=" * 70)
    print("✅ News fetcher ready!")

