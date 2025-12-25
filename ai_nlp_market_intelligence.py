"""
NLP Market Intelligence System - Quantum Elite AI Enhancement
Implements natural language processing for market sentiment analysis and conversational AI trading assistant
Features: BERT-based sentiment analysis, news analysis, social media monitoring, conversational AI
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from transformers import (
    TFBertModel, BertTokenizer, pipeline,
    GPT2LMHeadModel, GPT2Tokenizer, AutoTokenizer, AutoModelForCausalLM
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
import re
import requests
import json
import os
import threading
import time
from collections import deque
import warnings

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSentimentAnalyzer:
    """Advanced sentiment analysis for market-related text"""

    def __init__(self, model_path: str = "market_sentiment_model"):
        self.model_path = model_path
        self.sentiment_model = None
        self.tokenizer = None
        self.label_encoder = LabelEncoder()

        # Sentiment categories
        self.sentiment_labels = ['very_negative', 'negative', 'neutral', 'positive', 'very_positive']
        self.label_encoder.fit(self.sentiment_labels)

        # Financial lexicon
        self.financial_lexicon = self._load_financial_lexicon()

        # Aspect-based sentiment tracking
        self.aspect_sentiments = {
            'price': [], 'volume': [], 'market': [], 'company': [], 'economy': [],
            'earnings': [], 'regulatory': [], 'technical': [], 'fundamental': []
        }

        self._initialize_model()

    def _load_financial_lexicon(self) -> Dict[str, float]:
        """Load financial sentiment lexicon"""
        # Basic financial sentiment words with polarity scores
        lexicon = {
            # Positive words
            'bullish': 1.0, 'rally': 0.8, 'surge': 0.9, 'gain': 0.7, 'profit': 0.8,
            'breakout': 0.8, 'momentum': 0.6, 'optimism': 0.7, 'recovery': 0.8,
            'upgrade': 0.7, 'beat': 0.6, 'growth': 0.7, 'expansion': 0.6,

            # Negative words
            'bearish': -1.0, 'crash': -1.0, 'decline': -0.8, 'loss': -0.8,
            'drop': -0.7, 'fall': -0.7, 'slump': -0.8, 'plunge': -0.9,
            'downgrade': -0.7, 'miss': -0.6, 'contraction': -0.6, 'recession': -0.8,

            # Uncertainty words
            'volatile': -0.3, 'uncertain': -0.4, 'risk': -0.3, 'caution': -0.3,
            'concern': -0.4, 'worry': -0.5, 'fear': -0.6, 'panic': -0.7
        }
        return lexicon

    def _initialize_model(self):
        """Initialize BERT-based sentiment model"""
        try:
            # Use pre-trained BERT model for sentiment analysis
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.sentiment_model = TFBertModel.from_pretrained('bert-base-uncased')

            # Build sentiment classification head
            input_ids = tf.keras.layers.Input(shape=(512,), dtype=tf.int32, name='input_ids')
            attention_mask = tf.keras.layers.Input(shape=(512,), dtype=tf.int32, name='attention_mask')

            bert_output = self.sentiment_model(input_ids, attention_mask=attention_mask)[1]
            dense = tf.keras.layers.Dense(256, activation='relu')(bert_output)
            dropout = tf.keras.layers.Dropout(0.3)(dense)
            output = tf.keras.layers.Dense(len(self.sentiment_labels), activation='softmax')(dropout)

            self.classification_model = tf.keras.Model(
                inputs=[input_ids, attention_mask],
                outputs=output
            )

            self.classification_model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=2e-5),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )

            logger.info("Market sentiment analyzer initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize BERT model: {e}. Using rule-based fallback.")
            self.sentiment_model = None

    def analyze_sentiment(self, text: str, aspects: List[str] = None) -> Dict[str, Any]:
        """Analyze sentiment of market-related text"""
        if not text or not text.strip():
            return {'sentiment': 'neutral', 'confidence': 0.5, 'score': 0.0}

        # Preprocess text
        cleaned_text = self._preprocess_text(text)

        # Rule-based sentiment analysis as fallback/primary method
        rule_based_sentiment = self._rule_based_sentiment(cleaned_text)

        # BERT-based sentiment if model is available
        bert_sentiment = None
        if self.sentiment_model is not None:
            try:
                bert_sentiment = self._bert_sentiment_analysis(cleaned_text)
            except Exception as e:
                logger.warning(f"BERT sentiment analysis failed: {e}")

        # Combine sentiments
        final_sentiment = self._combine_sentiments(rule_based_sentiment, bert_sentiment)

        # Aspect-based analysis
        aspect_sentiments = {}
        if aspects:
            for aspect in aspects:
                aspect_sentiments[aspect] = self._analyze_aspect_sentiment(cleaned_text, aspect)

        # Store for trend analysis
        self._store_sentiment_history(final_sentiment)

        result = {
            'sentiment': final_sentiment['label'],
            'confidence': final_sentiment['confidence'],
            'score': final_sentiment['score'],
            'magnitude': abs(final_sentiment['score']),
            'aspects': aspect_sentiments,
            'text_length': len(cleaned_text),
            'financial_terms_detected': self._count_financial_terms(cleaned_text),
            'timestamp': datetime.now()
        }

        return result

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)

        # Remove mentions and hashtags (keep for social media analysis)
        text = re.sub(r'@\w+', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove special characters but keep financial symbols
        text = re.sub(r'[^\w\s\$€£¥%+-]', '', text)

        return text

    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Rule-based sentiment analysis using financial lexicon"""
        words = text.split()
        sentiment_score = 0.0
        matched_words = []

        for word in words:
            word = word.strip('.,!?')
            if word in self.financial_lexicon:
                sentiment_score += self.financial_lexicon[word]
                matched_words.append((word, self.financial_lexicon[word]))

        # Normalize score
        if matched_words:
            sentiment_score = sentiment_score / len(matched_words)
        else:
            sentiment_score = 0.0

        # Convert to label
        if sentiment_score >= 0.6:
            label = 'very_positive'
        elif sentiment_score >= 0.2:
            label = 'positive'
        elif sentiment_score <= -0.6:
            label = 'very_negative'
        elif sentiment_score <= -0.2:
            label = 'negative'
        else:
            label = 'neutral'

        confidence = min(abs(sentiment_score) * 2, 1.0) if matched_words else 0.3

        return {
            'label': label,
            'score': sentiment_score,
            'confidence': confidence,
            'matched_words': matched_words
        }

    def _bert_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """BERT-based sentiment analysis"""
        # Tokenize text
        inputs = self.tokenizer(
            text,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='tf'
        )

        # Get prediction
        predictions = self.classification_model.predict({
            'input_ids': inputs['input_ids'],
            'attention_mask': inputs['attention_mask']
        }, verbose=0)

        # Get predicted class and confidence
        predicted_class_idx = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        predicted_label = self.sentiment_labels[predicted_class_idx]

        # Convert to score (-1 to 1)
        score_mapping = {'very_negative': -1.0, 'negative': -0.5, 'neutral': 0.0, 'positive': 0.5, 'very_positive': 1.0}
        score = score_mapping[predicted_label]

        return {
            'label': predicted_label,
            'score': score,
            'confidence': float(confidence)
        }

    def _combine_sentiments(self, rule_based: Dict, bert: Dict = None) -> Dict[str, Any]:
        """Combine rule-based and BERT sentiments"""
        if bert is None:
            return rule_based

        # Weighted combination
        rule_weight = 0.6
        bert_weight = 0.4

        combined_score = rule_weight * rule_based['score'] + bert_weight * bert['score']
        combined_confidence = rule_weight * rule_based['confidence'] + bert_weight * bert['confidence']

        # Convert score to label
        if combined_score >= 0.6:
            label = 'very_positive'
        elif combined_score >= 0.2:
            label = 'positive'
        elif combined_score <= -0.6:
            label = 'very_negative'
        elif combined_score <= -0.2:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'label': label,
            'score': combined_score,
            'confidence': combined_confidence
        }

    def _analyze_aspect_sentiment(self, text: str, aspect: str) -> Dict[str, Any]:
        """Analyze sentiment for specific aspect"""
        # Define aspect keywords
        aspect_keywords = {
            'price': ['price', 'pricing', 'cost', 'value', 'valuation'],
            'volume': ['volume', 'trading', 'liquidity', 'flow'],
            'market': ['market', 'index', 'sector', 'industry'],
            'company': ['company', 'firm', 'corporation', 'business'],
            'economy': ['economy', 'economic', 'GDP', 'growth', 'inflation'],
            'earnings': ['earnings', 'revenue', 'profit', 'income', 'EPS'],
            'regulatory': ['regulation', 'regulator', 'compliance', 'SEC', 'FDA'],
            'technical': ['technical', 'chart', 'pattern', 'support', 'resistance'],
            'fundamental': ['fundamental', 'valuation', 'PE', 'dividend', 'growth']
        }

        keywords = aspect_keywords.get(aspect, [aspect])
        aspect_text = []

        # Extract sentences containing aspect keywords
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                aspect_text.append(sentence)

        if not aspect_text:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'mentions': 0}

        # Analyze combined aspect text
        combined_text = ' '.join(aspect_text)
        sentiment = self._rule_based_sentiment(combined_text)

        return {
            'sentiment': sentiment['label'],
            'confidence': sentiment['confidence'],
            'mentions': len(aspect_text),
            'score': sentiment['score']
        }

    def _count_financial_terms(self, text: str) -> int:
        """Count financial terms in text"""
        financial_terms = [
            'bull', 'bear', 'rally', 'crash', 'surge', 'plunge', 'volatile',
            'profit', 'loss', 'gain', 'decline', 'momentum', 'breakout',
            'resistance', 'support', 'trend', 'correction', 'reversal'
        ]

        count = 0
        for term in financial_terms:
            count += text.lower().count(term)

        return count

    def _store_sentiment_history(self, sentiment: Dict):
        """Store sentiment for trend analysis"""
        # This would store in a database for trend analysis
        pass

class NewsAggregator:
    """Aggregates and analyzes financial news from multiple sources"""

    def __init__(self):
        self.news_sources = {
            'yahoo_finance': 'https://finance.yahoo.com/news',
            'marketwatch': 'https://www.marketwatch.com/news',
            'bloomberg': 'https://www.bloomberg.com/markets',
            'reuters': 'https://www.reuters.com/finance/',
            'cnbc': 'https://www.cnbc.com/world/?region=world'
        }

        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.news_cache = deque(maxlen=1000)  # Cache recent news

        # News filtering
        self.relevant_keywords = [
            'trading', 'stocks', 'market', 'economy', 'federal reserve',
            'earnings', 'revenue', 'profit', 'loss', 'forecast', 'guidance',
            'bitcoin', 'crypto', 'forex', 'commodities', 'gold', 'oil'
        ]

    def fetch_latest_news(self, max_articles: int = 50) -> List[Dict[str, Any]]:
        """Fetch latest financial news"""
        all_news = []

        for source_name, source_url in self.news_sources.items():
            try:
                # In a real implementation, this would scrape or use APIs
                # For demo, we'll simulate news fetching
                news_items = self._simulate_news_fetch(source_name, max_articles // len(self.news_sources))
                all_news.extend(news_items)

            except Exception as e:
                logger.warning(f"Failed to fetch news from {source_name}: {e}")

        # Filter and analyze news
        filtered_news = []
        for news_item in all_news:
            if self._is_relevant_news(news_item):
                analyzed_news = self._analyze_news_item(news_item)
                filtered_news.append(analyzed_news)

        # Sort by recency and relevance
        filtered_news.sort(key=lambda x: (x['relevance_score'], x['timestamp']), reverse=True)

        return filtered_news[:max_articles]

    def _simulate_news_fetch(self, source: str, count: int) -> List[Dict[str, Any]]:
        """Simulate news fetching (would be replaced with real API calls)"""
        news_items = []

        # Sample news headlines and content
        sample_news = [
            {
                'title': 'Fed Signals Potential Rate Cuts as Inflation Cools',
                'content': 'The Federal Reserve indicated that interest rate cuts may be coming as inflation shows signs of cooling. Markets reacted positively to the news.',
                'source': source,
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            },
            {
                'title': 'Tech Stocks Rally on Strong Earnings Reports',
                'content': 'Major technology companies reported better-than-expected earnings, driving stock prices higher across the sector.',
                'source': source,
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            },
            {
                'title': 'Oil Prices Surge on Supply Concerns',
                'content': 'Crude oil prices increased significantly due to concerns about global supply disruptions.',
                'source': source,
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            },
            {
                'title': 'Cryptocurrency Market Shows Signs of Recovery',
                'content': 'Bitcoin and other cryptocurrencies have shown strong upward momentum in recent trading sessions.',
                'source': source,
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            }
        ]

        for i in range(min(count, len(sample_news))):
            news_items.append(sample_news[i].copy())

        return news_items

    def _is_relevant_news(self, news_item: Dict) -> bool:
        """Check if news is relevant to trading"""
        title = news_item.get('title', '').lower()
        content = news_item.get('content', '').lower()

        # Check for relevant keywords
        for keyword in self.relevant_keywords:
            if keyword in title or keyword in content:
                return True

        return False

    def _analyze_news_item(self, news_item: Dict) -> Dict[str, Any]:
        """Analyze a news item with sentiment and relevance"""
        title = news_item.get('title', '')
        content = news_item.get('content', '')

        # Combine title and content for analysis
        full_text = f"{title}. {content}"

        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze_sentiment(full_text)

        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(news_item)

        # Extract key entities and topics
        entities = self._extract_entities(full_text)

        analyzed_item = {
            **news_item,
            'sentiment': sentiment,
            'relevance_score': relevance_score,
            'entities': entities,
            'analyzed_at': datetime.now()
        }

        return analyzed_item

    def _calculate_relevance_score(self, news_item: Dict) -> float:
        """Calculate relevance score for news item"""
        score = 0.0

        title = news_item.get('title', '').lower()
        content = news_item.get('content', '')

        # Keyword matching
        keyword_matches = 0
        for keyword in self.relevant_keywords:
            if keyword in title:
                keyword_matches += 2  # Title matches weight more
            elif keyword in content:
                keyword_matches += 1

        score += min(keyword_matches * 0.1, 1.0)

        # Recency bonus
        hours_old = (datetime.now() - news_item['timestamp']).total_seconds() / 3600
        recency_score = max(0, 1 - (hours_old / 24))  # Decay over 24 hours
        score += recency_score * 0.3

        # Sentiment magnitude bonus
        sentiment_magnitude = abs(news_item.get('sentiment', {}).get('score', 0))
        score += sentiment_magnitude * 0.2

        return min(score, 1.0)

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities from text"""
        entities = {
            'companies': [],
            'currencies': [],
            'commodities': [],
            'indices': [],
            'sectors': []
        }

        # Simple entity extraction (would use NER model in production)
        company_indicators = ['corp', 'inc', 'ltd', 'plc', 'company', 'group']
        currencies = ['usd', 'eur', 'gbp', 'jpy', 'btc', 'eth']
        commodities = ['gold', 'oil', 'silver', 'copper', 'wheat', 'corn']
        indices = ['spx', 'ndx', 'dji', 'ftse', 'dax', 'nikkei']
        sectors = ['tech', 'technology', 'healthcare', 'finance', 'energy', 'consumer']

        words = text.lower().split()

        for i, word in enumerate(words):
            # Company detection
            if any(indicator in word for indicator in company_indicators):
                # Get company name (previous words)
                company_name = []
                for j in range(max(0, i-2), i+1):
                    if words[j] not in company_indicators:
                        company_name.append(words[j].title())
                if company_name:
                    entities['companies'].append(' '.join(company_name))

            # Currency detection
            if word in currencies:
                entities['currencies'].append(word.upper())

            # Commodity detection
            if word in commodities:
                entities['commodities'].append(word.title())

            # Index detection
            if word in indices:
                entities['indices'].append(word.upper())

            # Sector detection
            if word in sectors:
                entities['sectors'].append(word.title())

        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def get_market_sentiment_summary(self) -> Dict[str, Any]:
        """Get summary of current market sentiment from news"""
        recent_news = list(self.news_cache)[-100:]  # Last 100 news items

        if not recent_news:
            return {'error': 'No recent news available'}

        # Aggregate sentiment
        sentiments = [news.get('sentiment', {}).get('score', 0) for news in recent_news]
        avg_sentiment = np.mean(sentiments) if sentiments else 0

        # Sentiment distribution
        sentiment_labels = [news.get('sentiment', {}).get('label', 'neutral') for news in recent_news]
        sentiment_dist = pd.Series(sentiment_labels).value_counts().to_dict()

        # Top entities
        all_entities = {}
        for news in recent_news:
            entities = news.get('entities', {})
            for entity_type, entity_list in entities.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = []
                all_entities[entity_type].extend(entity_list)

        # Get most mentioned entities
        top_entities = {}
        for entity_type, entities in all_entities.items():
            if entities:
                entity_counts = pd.Series(entities).value_counts().head(5).to_dict()
                top_entities[entity_type] = entity_counts

        summary = {
            'overall_sentiment': {
                'average_score': float(avg_sentiment),
                'sentiment_label': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral',
                'sentiment_distribution': sentiment_dist
            },
            'news_volume': len(recent_news),
            'time_period': f"{recent_news[0]['timestamp']} to {recent_news[-1]['timestamp']}" if recent_news else None,
            'top_entities': top_entities,
            'key_insights': self._generate_key_insights(sentiments, top_entities),
            'generated_at': datetime.now()
        }

        return summary

    def _generate_key_insights(self, sentiments: List[float], top_entities: Dict) -> List[str]:
        """Generate key insights from sentiment and entity analysis"""
        insights = []

        avg_sentiment = np.mean(sentiments)

        # Overall market sentiment
        if avg_sentiment > 0.2:
            insights.append("Market sentiment is predominantly positive based on recent news coverage.")
        elif avg_sentiment < -0.2:
            insights.append("Market sentiment is predominantly negative with concerns highlighted in news.")
        else:
            insights.append("Market sentiment appears neutral with mixed news coverage.")

        # Entity-specific insights
        if 'companies' in top_entities and top_entities['companies']:
            top_company = list(top_entities['companies'].keys())[0]
            insights.append(f"{top_company} is receiving significant news coverage.")

        if 'sectors' in top_entities and top_entities['sectors']:
            top_sector = list(top_entities['sectors'].keys())[0]
            insights.append(f"{top_sector} sector is a major focus in current market news.")

        # Sentiment volatility
        sentiment_std = np.std(sentiments)
        if sentiment_std > 0.5:
            insights.append("Market sentiment shows high volatility with conflicting news signals.")
        elif sentiment_std < 0.2:
            insights.append("Market sentiment is relatively stable with consistent news coverage.")

        return insights

class ConversationalAITradingAssistant:
    """AI-powered conversational assistant for trading advice"""

    def __init__(self):
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.news_aggregator = NewsAggregator()

        # Conversation memory
        self.conversation_history = deque(maxlen=50)
        self.user_preferences = {}
        self.market_context = {}

        # Response templates
        self.response_templates = self._load_response_templates()

        # Initialize language model for conversational responses
        self._initialize_language_model()

    def _initialize_language_model(self):
        """Initialize conversational language model"""
        try:
            # Use a smaller model for demo (would use GPT-3.5/4 in production)
            self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            self.language_model = GPT2LMHeadModel.from_pretrained('gpt2')

            # Add special tokens for trading domain
            special_tokens = ['[MARKET_DATA]', '[SENTIMENT]', '[NEWS]', '[ADVICE]', '[RISK]']
            self.tokenizer.add_special_tokens({'additional_special_tokens': special_tokens})
            self.language_model.resize_token_embeddings(len(self.tokenizer))

            logger.info("Conversational AI assistant initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize language model: {e}")
            self.language_model = None

    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different scenarios"""
        return {
            'greeting': [
                "Hello! I'm your AI trading assistant. How can I help you with your trading decisions today?",
                "Hi there! I'm here to provide insights and analysis to support your trading. What would you like to know?",
                "Welcome! I can help you analyze market sentiment, get news updates, and provide trading insights. What's on your mind?"
            ],
            'market_sentiment': [
                "Based on recent news and social media analysis, the market sentiment is {sentiment}. {explanation}",
                "Current market sentiment appears {sentiment}. This is driven by {factors}.",
                "The overall market mood is {sentiment}, influenced by recent {events}."
            ],
            'trading_advice': [
                "Considering the current market conditions, I suggest {action}. This is based on {analysis}.",
                "Given the {sentiment} sentiment and {technical_factors}, a {strategy} approach might be appropriate.",
                "Based on my analysis, {recommendation}. Always remember to manage your risk appropriately."
            ],
            'risk_warning': [
                "Please remember that all trading involves risk. Never invest more than you can afford to lose.",
                "Market conditions can change rapidly. Always use proper risk management techniques.",
                "This is not financial advice. Please consult with a qualified financial advisor for personalized recommendations."
            ]
        }

    def process_user_message(self, user_message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user message and generate response"""
        # Store conversation history
        self.conversation_history.append({
            'user': user_message,
            'timestamp': datetime.now(),
            'user_id': user_id
        })

        # Analyze user intent
        intent = self._analyze_intent(user_message)

        # Generate response based on intent
        response = self._generate_response(intent, user_message, user_id)

        # Store response in history
        self.conversation_history.append({
            'assistant': response['message'],
            'timestamp': datetime.now(),
            'user_id': user_id,
            'intent': intent
        })

        return response

    def _analyze_intent(self, message: str) -> str:
        """Analyze user intent from message"""
        message_lower = message.lower()

        # Define intent patterns
        intent_patterns = {
            'market_sentiment': ['sentiment', 'mood', 'feeling', 'outlook', 'bullish', 'bearish', 'market mood'],
            'news_request': ['news', 'latest', 'updates', 'headlines', 'what\'s happening'],
            'trading_advice': ['should i', 'recommend', 'advice', 'strategy', 'trade', 'buy', 'sell'],
            'price_analysis': ['price', 'value', 'worth', 'level', 'target'],
            'risk_assessment': ['risk', 'safe', 'dangerous', 'volatile', 'uncertain'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
            'thanks': ['thank', 'thanks', 'appreciate', 'grateful']
        }

        for intent, patterns in intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent

        return 'general_inquiry'

    def _generate_response(self, intent: str, message: str, user_id: str = None) -> Dict[str, Any]:
        """Generate response based on intent"""
        response_data = {
            'message': '',
            'intent': intent,
            'confidence': 0.8,
            'data': {},
            'timestamp': datetime.now()
        }

        if intent == 'greeting':
            response_data['message'] = np.random.choice(self.response_templates['greeting'])

        elif intent == 'market_sentiment':
            sentiment_summary = self.news_aggregator.get_market_sentiment_summary()
            sentiment = sentiment_summary.get('overall_sentiment', {}).get('sentiment_label', 'neutral')

            explanation = "recent news analysis and market indicators"
            response_data['message'] = np.random.choice(self.response_templates['market_sentiment']).format(
                sentiment=sentiment, explanation=explanation
            )
            response_data['data'] = sentiment_summary

        elif intent == 'news_request':
            latest_news = self.news_aggregator.fetch_latest_news(max_articles=5)
            if latest_news:
                top_news = latest_news[0]
                response_data['message'] = f"Latest market news: {top_news['title']} - Sentiment: {top_news['sentiment']['sentiment']}"
                response_data['data'] = {'news': latest_news[:3]}
            else:
                response_data['message'] = "I'm currently fetching the latest market news. Please check back in a moment."

        elif intent == 'trading_advice':
            # Get market context
            sentiment_summary = self.news_aggregator.get_market_sentiment_summary()
            sentiment = sentiment_summary.get('overall_sentiment', {}).get('sentiment_label', 'neutral')

            # Generate contextual advice
            if sentiment == 'positive':
                advice = "considering a long position with proper risk management"
            elif sentiment == 'negative':
                advice = "being cautious and considering defensive positions"
            else:
                advice = "waiting for clearer market direction"

            analysis = f"{sentiment} market sentiment and current news flow"
            response_data['message'] = np.random.choice(self.response_templates['trading_advice']).format(
                action=advice, analysis=analysis
            )
            response_data['message'] += " " + np.random.choice(self.response_templates['risk_warning'])

        elif intent == 'thanks':
            response_data['message'] = "You're welcome! I'm here whenever you need trading insights or market analysis."

        else:
            # Use language model for general responses
            if self.language_model:
                response_data['message'] = self._generate_with_language_model(message)
            else:
                response_data['message'] = "I understand you're asking about trading. Could you please provide more specific details about what you'd like to know?"

        return response_data

    def _generate_with_language_model(self, context: str) -> str:
        """Generate response using language model"""
        try:
            # Prepare input
            prompt = f"User: {context}\nAI Trading Assistant:"

            inputs = self.tokenizer(prompt, return_tensors='pt', max_length=512, truncation=True)

            # Generate response
            outputs = self.language_model.generate(
                inputs['input_ids'],
                max_length=150,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.split('AI Trading Assistant:')[-1].strip()

            return response

        except Exception as e:
            logger.warning(f"Language model generation failed: {e}")
            return "I'm analyzing your question. Could you please rephrase or provide more details?"

    def get_conversation_summary(self, user_id: str = None) -> Dict[str, Any]:
        """Get summary of conversation"""
        user_messages = [msg for msg in self.conversation_history
                        if msg.get('user_id') == user_id or user_id is None]

        if not user_messages:
            return {'error': 'No conversation history found'}

        intents = [msg.get('intent') for msg in user_messages if msg.get('assistant')]
        intent_counts = pd.Series(intents).value_counts().to_dict()

        summary = {
            'total_messages': len(user_messages),
            'conversation_length': len([msg for msg in user_messages if 'assistant' in msg]),
            'top_intents': intent_counts,
            'most_recent_topic': intents[-1] if intents else None,
            'conversation_start': user_messages[0]['timestamp'],
            'last_activity': user_messages[-1]['timestamp']
        }

        return summary

    def update_market_context(self, market_data: Dict):
        """Update market context for more informed responses"""
        self.market_context.update(market_data)

    def get_assistant_capabilities(self) -> Dict[str, Any]:
        """Get assistant capabilities and features"""
        return {
            'features': [
                'Real-time market sentiment analysis',
                'Latest financial news aggregation',
                'Trading strategy recommendations',
                'Risk assessment and warnings',
                'Conversational AI responses',
                'Market trend analysis',
                'Entity and topic extraction'
            ],
            'supported_intents': [
                'market_sentiment', 'news_request', 'trading_advice',
                'price_analysis', 'risk_assessment', 'general_inquiry'
            ],
            'data_sources': [
                'Financial news APIs',
                'Social media sentiment',
                'Market data feeds',
                'Economic indicators'
            ],
            'languages_supported': ['English'],
            'last_updated': datetime.now()
        }

class QuantumEliteNLPMarketIntelligence:
    """Complete NLP-powered market intelligence system"""

    def __init__(self):
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.news_aggregator = NewsAggregator()
        self.trading_assistant = ConversationalAITradingAssistant()

        # Real-time processing
        self.is_running = False
        self.monitoring_thread = None

        # Analytics storage
        self.sentiment_history = deque(maxlen=5000)
        self.news_history = deque(maxlen=2000)

        logger.info("Quantum Elite NLP Market Intelligence system initialized")

    def start_real_time_monitoring(self):
        """Start real-time market monitoring"""
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        logger.info("Real-time market monitoring started")

    def stop_real_time_monitoring(self):
        """Stop real-time market monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Real-time market monitoring stopped")

    def _monitoring_worker(self):
        """Background monitoring worker"""
        while self.is_running:
            try:
                # Fetch latest news
                latest_news = self.news_aggregator.fetch_latest_news(max_articles=10)

                # Store news
                for news_item in latest_news:
                    self.news_history.append(news_item)
                    self.sentiment_history.append({
                        'timestamp': news_item['timestamp'],
                        'sentiment': news_item['sentiment']['score'],
                        'source': news_item['source']
                    })

                # Update assistant context
                sentiment_summary = self.news_aggregator.get_market_sentiment_summary()
                self.trading_assistant.update_market_context(sentiment_summary)

                # Sleep for next monitoring cycle
                time.sleep(300)  # 5 minutes

            except Exception as e:
                logger.error(f"Monitoring cycle failed: {e}")
                time.sleep(60)

    def analyze_text_sentiment(self, text: str, aspects: List[str] = None) -> Dict[str, Any]:
        """Analyze sentiment of any market-related text"""
        return self.sentiment_analyzer.analyze_sentiment(text, aspects)

    def get_market_news_analysis(self, max_news: int = 20) -> Dict[str, Any]:
        """Get comprehensive market news analysis"""
        latest_news = self.news_aggregator.fetch_latest_news(max_news)
        sentiment_summary = self.news_aggregator.get_market_sentiment_summary()

        analysis = {
            'latest_news': latest_news,
            'sentiment_summary': sentiment_summary,
            'news_volume_trend': self._analyze_news_volume_trend(),
            'sentiment_trend': self._analyze_sentiment_trend(),
            'key_insights': self._generate_market_insights(latest_news, sentiment_summary),
            'generated_at': datetime.now()
        }

        return analysis

    def _analyze_news_volume_trend(self) -> Dict[str, Any]:
        """Analyze news volume trends"""
        if len(self.news_history) < 10:
            return {'trend': 'insufficient_data'}

        # Group by hour
        recent_news = list(self.news_history)[-100:]
        news_df = pd.DataFrame(recent_news)
        news_df['hour'] = news_df['timestamp'].dt.hour

        hourly_volume = news_df.groupby('hour').size()

        current_hour = datetime.now().hour
        avg_volume = hourly_volume.mean()
        current_volume = hourly_volume.get(current_hour, 0)

        trend = 'high' if current_volume > avg_volume * 1.2 else 'low' if current_volume < avg_volume * 0.8 else 'normal'

        return {
            'trend': trend,
            'current_volume': int(current_volume),
            'average_volume': float(avg_volume),
            'volume_ratio': float(current_volume / avg_volume) if avg_volume > 0 else 0
        }

    def _analyze_sentiment_trend(self) -> Dict[str, Any]:
        """Analyze sentiment trends over time"""
        if len(self.sentiment_history) < 20:
            return {'trend': 'insufficient_data'}

        recent_sentiments = list(self.sentiment_history)[-50:]
        sentiment_df = pd.DataFrame(recent_sentiments)

        # Calculate rolling averages
        sentiment_df['rolling_avg'] = sentiment_df['sentiment'].rolling(10).mean()

        current_avg = sentiment_df['rolling_avg'].iloc[-1]
        previous_avg = sentiment_df['rolling_avg'].iloc[-11] if len(sentiment_df) > 11 else current_avg

        change = current_avg - previous_avg

        if change > 0.1:
            trend = 'improving'
        elif change < -0.1:
            trend = 'worsening'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'current_sentiment': float(current_avg),
            'change': float(change),
            'volatility': float(sentiment_df['sentiment'].std())
        }

    def _generate_market_insights(self, news: List[Dict], sentiment_summary: Dict) -> List[str]:
        """Generate key market insights"""
        insights = []

        # Overall sentiment insight
        overall_sentiment = sentiment_summary.get('overall_sentiment', {})
        sentiment_label = overall_sentiment.get('sentiment_label', 'neutral')
        insights.append(f"Market sentiment is {sentiment_label} based on recent news analysis.")

        # News volume insight
        volume_trend = self._analyze_news_volume_trend()
        if volume_trend['trend'] == 'high':
            insights.append("News volume is unusually high, indicating increased market attention.")
        elif volume_trend['trend'] == 'low':
            insights.append("News volume is lower than usual, suggesting calmer market conditions.")

        # Sentiment trend insight
        sentiment_trend = self._analyze_sentiment_trend()
        if sentiment_trend['trend'] == 'improving':
            insights.append("Market sentiment is showing signs of improvement.")
        elif sentiment_trend['trend'] == 'worsening':
            insights.append("Market sentiment appears to be deteriorating.")

        # Key entities insight
        top_entities = sentiment_summary.get('top_entities', {})
        if 'companies' in top_entities and top_entities['companies']:
            top_company = list(top_entities['companies'].keys())[0]
            insights.append(f"{top_company} is receiving significant market attention.")

        return insights

    def chat_with_assistant(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Chat with the AI trading assistant"""
        return self.trading_assistant.process_user_message(message, user_id)

    def get_conversation_analytics(self, user_id: str = None) -> Dict[str, Any]:
        """Get conversation analytics"""
        return self.trading_assistant.get_conversation_summary(user_id)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        sentiment_trend = self._analyze_sentiment_trend()
        volume_trend = self._analyze_news_volume_trend()

        status = {
            'system_active': self.is_running,
            'sentiment_analyzer': {
                'status': 'active',
                'model_loaded': self.sentiment_analyzer.sentiment_model is not None
            },
            'news_aggregator': {
                'status': 'active',
                'sources_count': len(self.news_aggregator.news_sources),
                'cached_news': len(self.news_history)
            },
            'trading_assistant': {
                'status': 'active',
                'language_model_loaded': self.trading_assistant.language_model is not None,
                'capabilities': self.trading_assistant.get_assistant_capabilities()
            },
            'market_metrics': {
                'sentiment_trend': sentiment_trend,
                'news_volume_trend': volume_trend,
                'sentiment_history_size': len(self.sentiment_history),
                'news_history_size': len(self.news_history)
            },
            'last_update': datetime.now()
        }

        return status

# Integration class for the trading platform
class NLPMarketIntelligencePlatform:
    """Platform integration for NLP market intelligence"""

    def __init__(self):
        self.nlp_system = QuantumEliteNLPMarketIntelligence()
        self.nlp_system.start_real_time_monitoring()

    def get_market_intelligence_report(self) -> Dict[str, Any]:
        """Generate comprehensive market intelligence report"""
        news_analysis = self.nlp_system.get_market_news_analysis()
        system_status = self.nlp_system.get_system_status()

        report = {
            'market_overview': {
                'sentiment_summary': news_analysis['sentiment_summary'],
                'key_insights': news_analysis['key_insights'],
                'sentiment_trend': news_analysis['sentiment_trend'],
                'news_volume_trend': news_analysis['news_volume_trend']
            },
            'latest_news': news_analysis['latest_news'][:10],
            'ai_assistant_status': {
                'active': system_status['trading_assistant']['status'] == 'active',
                'capabilities': system_status['trading_assistant']['capabilities']['features']
            },
            'system_health': {
                'monitoring_active': system_status['system_active'],
                'data_sources': len(system_status['news_aggregator']['sources_count']),
                'sentiment_model': system_status['sentiment_analyzer']['model_loaded'],
                'language_model': system_status['trading_assistant']['language_model_loaded']
            },
            'generated_at': datetime.now()
        }

        return report

    def analyze_trading_signal(self, signal_description: str) -> Dict[str, Any]:
        """Analyze a trading signal using NLP"""
        sentiment = self.nlp_system.analyze_text_sentiment(signal_description)

        # Generate AI analysis
        assistant_response = self.nlp_system.chat_with_assistant(
            f"Analyze this trading signal: {signal_description}",
            user_id='signal_analysis'
        )

        analysis = {
            'signal_description': signal_description,
            'sentiment_analysis': sentiment,
            'ai_insights': assistant_response['message'],
            'confidence_score': sentiment['confidence'],
            'recommendation_confidence': assistant_response['confidence'],
            'analyzed_at': datetime.now()
        }

        return analysis
