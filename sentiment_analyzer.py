"""
Sentiment Analysis Module
Analyzes market sentiment from social media, news, and forums
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class SentimentSource(Enum):
    """Sentiment data sources"""
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    TRADINGVIEW = "tradingview"

class Sentiment(Enum):
    """Sentiment values"""
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"

class SentimentAnalyzer:
    """Analyze market sentiment from multiple sources"""
    
    def __init__(self, data_file="sentiment_data.json"):
        self.data_file = data_file
        self.sentiment_data = {
            'assets': {},  # {asset: {source: sentiment_scores}}
            'keywords': self._init_keywords(),
            'last_updated': {}
        }
        self.load_data()
    
    def load_data(self):
        """Load sentiment data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with keywords
                    self.sentiment_data['assets'] = loaded.get('assets', {})
                    self.sentiment_data['last_updated'] = loaded.get('last_updated', {})
            except:
                pass
    
    def save_data(self):
        """Save sentiment data"""
        with open(self.data_file, 'w') as f:
            json.dump({
                'assets': self.sentiment_data['assets'],
                'last_updated': self.sentiment_data['last_updated']
            }, f, indent=2)
    
    def _init_keywords(self) -> Dict:
        """Initialize sentiment keywords"""
        return {
            'bullish': ['bullish', 'buy', 'long', 'moon', 'pump', 'surge', 'rally', 'breakout', 'support', 'uptrend'],
            'bearish': ['bearish', 'sell', 'short', 'dump', 'crash', 'drop', 'fall', 'resistance', 'downtrend'],
            'strong_bullish': ['very bullish', 'extremely bullish', 'rocket', 'to the moon', 'massive rally'],
            'strong_bearish': ['very bearish', 'extremely bearish', 'plummet', 'collapse', 'massive selloff']
        }
    
    # ============================================================================
    # SENTIMENT COLLECTION (Placeholder - would use real APIs)
    # ============================================================================
    
    def collect_twitter_sentiment(self, asset: str, timeframe_hours: int = 24) -> Dict:
        """Collect sentiment from Twitter
        
        Args:
            asset: Asset symbol (e.g., 'BTC', 'EURUSD')
            timeframe_hours: Hours to look back
        
        Returns:
            Dict with sentiment metrics
        """
        # Placeholder - would use Twitter API (tweepy)
        # Search for tweets mentioning asset
        # Analyze sentiment using NLP
        
        # Simulated data
        return {
            'source': 'twitter',
            'asset': asset,
            'total_mentions': 1250,
            'sentiment_score': 0.65,  # -1 to +1
            'bullish_ratio': 0.68,
            'bearish_ratio': 0.32,
            'volume_trend': 'increasing',
            'top_keywords': ['breakout', 'bullish', 'support'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def collect_reddit_sentiment(self, asset: str, subreddits: List[str] = None) -> Dict:
        """Collect sentiment from Reddit
        
        Args:
            asset: Asset symbol
            subreddits: List of subreddits to search (default: auto-detect)
        
        Returns:
            Dict with sentiment metrics
        """
        if not subreddits:
            # Auto-detect relevant subreddits
            if asset == 'BTC':
                subreddits = ['cryptocurrency', 'bitcoin', 'cryptomarkets']
            else:
                subreddits = ['forex', 'trading', 'wallstreetbets']
        
        # Placeholder - would use Reddit API (PRAW)
        # Search posts and comments
        # Analyze sentiment
        
        # Simulated data
        return {
            'source': 'reddit',
            'asset': asset,
            'total_posts': 85,
            'total_comments': 420,
            'sentiment_score': 0.55,
            'upvote_ratio': 0.78,
            'top_posts': [
                {'title': 'BTC looking strong at support', 'score': 125, 'sentiment': 'bullish'},
                {'title': 'Analysis: Bullish continuation pattern', 'score': 98, 'sentiment': 'bullish'}
            ],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def collect_news_sentiment(self, asset: str, sources: List[str] = None) -> Dict:
        """Collect sentiment from news articles
        
        Args:
            asset: Asset symbol
            sources: List of news sources (default: major financial news)
        
        Returns:
            Dict with sentiment metrics
        """
        # Placeholder - would use News API, Alpha Vantage, etc.
        # Scrape headlines and articles
        # Analyze sentiment using NLP
        
        # Simulated data
        return {
            'source': 'news',
            'asset': asset,
            'article_count': 15,
            'sentiment_score': 0.45,
            'headline_sentiment': 'neutral to bullish',
            'top_headlines': [
                {'title': 'Bitcoin shows resilience amid market volatility', 'sentiment': 0.6},
                {'title': 'Analysts predict continued strength', 'sentiment': 0.7}
            ],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # ============================================================================
    # SENTIMENT AGGREGATION
    # ============================================================================
    
    def get_aggregate_sentiment(self, asset: str, refresh: bool = False) -> Dict:
        """Get aggregated sentiment from all sources
        
        Args:
            asset: Asset symbol
            refresh: Force refresh data
        
        Returns:
            Dict with aggregated sentiment
        """
        asset_key = asset.upper()
        
        # Check if data needs refresh (older than 1 hour)
        needs_refresh = refresh
        if not refresh and asset_key in self.sentiment_data['last_updated']:
            last_update = datetime.fromisoformat(self.sentiment_data['last_updated'][asset_key])
            if datetime.now() - last_update > timedelta(hours=1):
                needs_refresh = True
        
        # Collect fresh data if needed
        if needs_refresh or asset_key not in self.sentiment_data['assets']:
            twitter_data = self.collect_twitter_sentiment(asset)
            reddit_data = self.collect_reddit_sentiment(asset)
            news_data = self.collect_news_sentiment(asset)
            
            self.sentiment_data['assets'][asset_key] = {
                'twitter': twitter_data,
                'reddit': reddit_data,
                'news': news_data
            }
            self.sentiment_data['last_updated'][asset_key] = datetime.now().isoformat()
            self.save_data()
        
        # Aggregate sentiments
        asset_data = self.sentiment_data['assets'][asset_key]
        
        twitter_score = asset_data['twitter']['sentiment_score']
        reddit_score = asset_data['reddit']['sentiment_score']
        news_score = asset_data['news']['sentiment_score']
        
        # Weighted average (Twitter 40%, Reddit 30%, News 30%)
        aggregate_score = (twitter_score * 0.4) + (reddit_score * 0.3) + (news_score * 0.3)
        
        # Classify sentiment
        sentiment_label = self._classify_sentiment(aggregate_score)
        
        return {
            'asset': asset,
            'aggregate_score': round(aggregate_score, 2),
            'sentiment': sentiment_label,
            'sources': {
                'twitter': {'score': twitter_score, 'mentions': asset_data['twitter']['total_mentions']},
                'reddit': {'score': reddit_score, 'posts': asset_data['reddit']['total_posts']},
                'news': {'score': news_score, 'articles': asset_data['news']['article_count']}
            },
            'confidence': self._calculate_confidence(asset_data),
            'trend': self._determine_trend(asset_key),
            'last_updated': self.sentiment_data['last_updated'][asset_key]
        }
    
    def _classify_sentiment(self, score: float) -> str:
        """Classify sentiment score into label"""
        if score >= 0.7:
            return "VERY BULLISH"
        elif score >= 0.4:
            return "BULLISH"
        elif score >= -0.4:
            return "NEUTRAL"
        elif score >= -0.7:
            return "BEARISH"
        else:
            return "VERY BEARISH"
    
    def _calculate_confidence(self, asset_data: Dict) -> float:
        """Calculate confidence in sentiment reading"""
        # Confidence based on data volume and agreement
        twitter_mentions = asset_data['twitter']['total_mentions']
        reddit_activity = asset_data['reddit']['total_posts'] + asset_data['reddit']['total_comments']
        news_articles = asset_data['news']['article_count']
        
        # Volume score (0-1)
        volume_score = min(1.0, (twitter_mentions / 1000 + reddit_activity / 500 + news_articles / 20) / 3)
        
        # Agreement score (how aligned are the sources?)
        scores = [
            asset_data['twitter']['sentiment_score'],
            asset_data['reddit']['sentiment_score'],
            asset_data['news']['sentiment_score']
        ]
        std_dev = np.std(scores) if len(scores) > 1 else 0
        agreement_score = max(0, 1 - (std_dev * 2))  # Lower std dev = higher agreement
        
        # Combined confidence
        confidence = (volume_score * 0.4) + (agreement_score * 0.6)
        return round(confidence, 2)
    
    def _determine_trend(self, asset_key: str) -> str:
        """Determine sentiment trend (improving/declining)"""
        # Would compare current sentiment to historical
        # Placeholder: return neutral
        return "stable"
    
    # ============================================================================
    # BATCH ANALYSIS
    # ============================================================================
    
    def analyze_multiple_assets(self, assets: List[str]) -> Dict:
        """Analyze sentiment for multiple assets
        
        Args:
            assets: List of asset symbols
        
        Returns:
            Dict with sentiments sorted by score
        """
        results = []
        
        for asset in assets:
            sentiment = self.get_aggregate_sentiment(asset)
            results.append(sentiment)
        
        # Sort by aggregate score (most bullish first)
        results.sort(key=lambda x: x['aggregate_score'], reverse=True)
        
        return {
            'assets': results,
            'most_bullish': results[0] if results else None,
            'most_bearish': results[-1] if results else None,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # ============================================================================
    # DISPLAY
    # ============================================================================
    
    def format_sentiment_message(self, asset: str) -> str:
        """Format sentiment analysis message"""
        sentiment = self.get_aggregate_sentiment(asset)
        
        score = sentiment['aggregate_score']
        label = sentiment['sentiment']
        confidence = sentiment['confidence']
        
        # Emoji based on sentiment
        emoji_map = {
            'VERY BULLISH': '🚀📈',
            'BULLISH': '📈✅',
            'NEUTRAL': '➡️',
            'BEARISH': '📉⚠️',
            'VERY BEARISH': '💥📉'
        }
        emoji = emoji_map.get(label, '➡️')
        
        msg = f"{emoji} **{asset} SENTIMENT ANALYSIS**\n\n"
        msg += f"*Overall Sentiment:* {label}\n"
        msg += f"*Score:* {score} / 1.0\n"
        msg += f"*Confidence:* {confidence * 100:.0f}%\n\n"
        
        msg += "*Source Breakdown:*\n"
        sources = sentiment['sources']
        msg += f"🐦 Twitter: {sources['twitter']['score']:.2f} ({sources['twitter']['mentions']} mentions)\n"
        msg += f"👽 Reddit: {sources['reddit']['score']:.2f} ({sources['reddit']['posts']} posts)\n"
        msg += f"📰 News: {sources['news']['score']:.2f} ({sources['news']['articles']} articles)\n\n"
        
        # Trading insight
        msg += "*Trading Insight:*\n"
        if label in ['VERY BULLISH', 'BULLISH']:
            msg += "✅ Positive sentiment supports long positions\n"
        elif label in ['VERY BEARISH', 'BEARISH']:
            msg += "⚠️ Negative sentiment - consider shorts or caution on longs\n"
        else:
            msg += "➡️ Neutral sentiment - rely on technical analysis\n"
        
        msg += f"\n🔄 Last Updated: {sentiment['last_updated'][:16]}"
        
        return msg
    
    def format_multi_asset_message(self, assets: List[str]) -> str:
        """Format multi-asset sentiment comparison"""
        analysis = self.analyze_multiple_assets(assets)
        
        msg = "📊 **MULTI-ASSET SENTIMENT**\n\n"
        
        for sentiment in analysis['assets']:
            asset = sentiment['asset']
            label = sentiment['sentiment']
            score = sentiment['aggregate_score']
            
            emoji = '🚀' if score > 0.5 else '📉' if score < -0.5 else '➡️'
            msg += f"{emoji} *{asset}*: {label} ({score:+.2f})\n"
        
        msg += "\n"
        
        if analysis['most_bullish']:
            mb = analysis['most_bullish']
            msg += f"*Most Bullish:* {mb['asset']} ({mb['aggregate_score']:+.2f})\n"
        
        if analysis['most_bearish']:
            mb = analysis['most_bearish']
            msg += f"*Most Bearish:* {mb['asset']} ({mb['aggregate_score']:+.2f})\n"
        
        return msg


# Import numpy if available (for std calculation)
try:
    import numpy as np
except ImportError:
    # Fallback if numpy not available
    class np:
        @staticmethod
        def std(arr):
            mean = sum(arr) / len(arr)
            variance = sum((x - mean) ** 2 for x in arr) / len(arr)
            return variance ** 0.5


if __name__ == "__main__":
    # Test sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    # Analyze BTC
    print(analyzer.format_sentiment_message('BTC'))
    print("\n" + "="*50 + "\n")
    
    # Multi-asset analysis
    print(analyzer.format_multi_asset_message(['BTC', 'EURUSD', 'GOLD']))


















