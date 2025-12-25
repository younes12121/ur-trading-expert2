"""
Forex News Fetcher with Sentiment Analysis
Fetches forex-related news and analyzes sentiment
Helps avoid trading during major market-moving news
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re


class ForexNewsFetcher:
    """Fetch and analyze forex news sentiment"""
    
    def __init__(self):
        """Initialize news fetcher with free sources"""
        # Free news sources
        self.sources = {
            'forex_factory': 'https://www.forexfactory.com/news',
            'investing': 'https://www.investing.com/news/forex-news',
        }
        
        self.cache = {}
        self.cache_time = None
        self.cache_duration = 1800  # 30 minutes
        
        # Sentiment keywords
        self.positive_keywords = [
            'surge', 'rally', 'gain', 'rise', 'jump', 'soar', 'climb',
            'strengthen', 'boost', 'positive', 'optimistic', 'bullish',
            'growth', 'recovery', 'improvement', 'strong'
        ]
        
        self.negative_keywords = [
            'plunge', 'crash', 'fall', 'drop', 'decline', 'sink', 'tumble',
            'weaken', 'negative', 'pessimistic', 'bearish', 'recession',
            'crisis', 'concern', 'worry', 'weak', 'poor'
        ]
    
    def get_latest_news(self, currency=None, hours_back=24, limit=10):
        """
        Get latest forex news
        
        Args:
            currency: Filter by currency (e.g., 'USD', 'EUR')
            hours_back: Look back this many hours
            limit: Maximum number of news items
        
        Returns:
            list: News items with sentiment
        """
        # For now, return simulated news
        # In production, implement actual news scraping or API
        
        news_items = self._generate_sample_news(currency, hours_back, limit)
        
        # Analyze sentiment for each item
        for item in news_items:
            item['sentiment'] = self.analyze_sentiment(item['title'] + ' ' + item['content'])
            item['sentiment_score'] = item['sentiment']['score']
            item['sentiment_label'] = item['sentiment']['label']
        
        return news_items
    
    def _generate_sample_news(self, currency, hours_back, limit):
        """Generate sample news for testing"""
        sample_news = [
            {
                'title': 'USD Strengthens on Strong Jobs Data',
                'content': 'The US dollar rallied today following better-than-expected employment figures.',
                'currency': 'USD',
                'time': datetime.now() - timedelta(hours=2),
                'source': 'Forex Factory'
            },
            {
                'title': 'EUR Weakens Amid ECB Rate Concerns',
                'content': 'The euro declined as traders worry about potential ECB rate cuts.',
                'currency': 'EUR',
                'time': datetime.now() - timedelta(hours=5),
                'source': 'Investing.com'
            },
            {
                'title': 'GBP Gains on Positive GDP Growth',
                'content': 'Sterling surged after UK GDP exceeded forecasts.',
                'currency': 'GBP',
                'time': datetime.now() - timedelta(hours=8),
                'source': 'Forex Factory'
            },
            {
                'title': 'JPY Falls as BOJ Maintains Dovish Stance',
                'content': 'The yen weakened following Bank of Japan comments on keeping rates low.',
                'currency': 'JPY',
                'time': datetime.now() - timedelta(hours=12),
                'source': 'Investing.com'
            },
        ]
        
        # Filter by currency if specified
        if currency:
            sample_news = [n for n in sample_news if n['currency'] == currency]
        
        # Filter by time
        cutoff = datetime.now() - timedelta(hours=hours_back)
        sample_news = [n for n in sample_news if n['time'] >= cutoff]
        
        return sample_news[:limit]
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
        
        Returns:
            dict: Sentiment analysis result
        """
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            score = 0
            label = 'Neutral'
        else:
            score = (positive_count - negative_count) / total
            
            if score > 0.3:
                label = 'Positive'
            elif score < -0.3:
                label = 'Negative'
            else:
                label = 'Neutral'
        
        return {
            'score': round(score, 2),
            'label': label,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def get_currency_sentiment(self, currency, hours_back=24):
        """
        Get overall sentiment for a currency
        
        Args:
            currency: Currency code (e.g., 'USD', 'EUR')
            hours_back: Look back this many hours
        
        Returns:
            dict: Overall sentiment analysis
        """
        news = self.get_latest_news(currency, hours_back)
        
        if not news:
            return {
                'currency': currency,
                'sentiment': 'Neutral',
                'score': 0,
                'news_count': 0
            }
        
        # Average sentiment score
        avg_score = sum(item['sentiment_score'] for item in news) / len(news)
        
        if avg_score > 0.2:
            sentiment = 'Positive'
        elif avg_score < -0.2:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return {
            'currency': currency,
            'sentiment': sentiment,
            'score': round(avg_score, 2),
            'news_count': len(news),
            'latest_news': news[0]['title'] if news else None
        }
    
    def get_pair_sentiment(self, pair):
        """
        Get sentiment for a forex pair
        
        Args:
            pair: Forex pair (e.g., 'EURUSD')
        
        Returns:
            dict: Pair sentiment analysis
        """
        base = pair[:3]
        quote = pair[3:]
        
        base_sentiment = self.get_currency_sentiment(base)
        quote_sentiment = self.get_currency_sentiment(quote)
        
        # Calculate pair sentiment
        # If base is positive and quote is negative = bullish for pair
        # If base is negative and quote is positive = bearish for pair
        
        pair_score = base_sentiment['score'] - quote_sentiment['score']
        
        if pair_score > 0.3:
            direction = 'Bullish'
        elif pair_score < -0.3:
            direction = 'Bearish'
        else:
            direction = 'Neutral'
        
        return {
            'pair': pair,
            'direction': direction,
            'score': round(pair_score, 2),
            'base_sentiment': base_sentiment['sentiment'],
            'quote_sentiment': quote_sentiment['sentiment']
        }


# Testing
if __name__ == "__main__":
    print("Testing Forex News Fetcher...")
    print("=" * 60)
    
    fetcher = ForexNewsFetcher()
    
    # Test 1: Get latest USD news
    print("\n1. Latest USD news:")
    usd_news = fetcher.get_latest_news(currency='USD', limit=3)
    for item in usd_news:
        print(f"   - {item['title']}")
        print(f"     Sentiment: {item['sentiment_label']} ({item['sentiment_score']})")
    
    # Test 2: Get EUR sentiment
    print("\n2. EUR overall sentiment:")
    eur_sentiment = fetcher.get_currency_sentiment('EUR')
    print(f"   Sentiment: {eur_sentiment['sentiment']} ({eur_sentiment['score']})")
    print(f"   News count: {eur_sentiment['news_count']}")
    
    # Test 3: Get EUR/USD pair sentiment
    print("\n3. EUR/USD pair sentiment:")
    pair_sentiment = fetcher.get_pair_sentiment('EURUSD')
    print(f"   Direction: {pair_sentiment['direction']} ({pair_sentiment['score']})")
    print(f"   Base (EUR): {pair_sentiment['base_sentiment']}")
    print(f"   Quote (USD): {pair_sentiment['quote_sentiment']}")
    
    # Test 4: Analyze custom text
    print("\n4. Sentiment analysis of custom text:")
    text = "The dollar surged to new highs as markets rally on positive economic data"
    sentiment = fetcher.analyze_sentiment(text)
    print(f"   Text: \"{text}\"")
    print(f"   Sentiment: {sentiment['label']} ({sentiment['score']})")
    
    print("\n" + "=" * 60)
    print("[OK] Forex News Fetcher ready!")
