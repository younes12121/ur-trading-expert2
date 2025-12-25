"""
Search Handler Module
Provides intelligent search functionality for commands, help topics, and assets
"""

import re
from typing import List, Dict, Any, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Search database - commands, assets, and topics
SEARCH_DATABASE = {
    'commands': {
        # Trading commands
        'btc': {'name': 'Bitcoin Signal', 'desc': 'Get Bitcoin (BTC/USD) trading signal', 'category': 'trading'},
        'gold': {'name': 'Gold Signal', 'desc': 'Get Gold (XAU/USD) trading signal', 'category': 'trading'},
        'eth': {'name': 'Ethereum Signal', 'desc': 'Get Ethereum (ETH/USD) trading signal', 'category': 'trading'},
        'eurusd': {'name': 'EUR/USD Signal', 'desc': 'Get Euro vs US Dollar forex signal', 'category': 'trading'},
        'gbpusd': {'name': 'GBP/USD Signal', 'desc': 'Get British Pound vs US Dollar signal', 'category': 'trading'},
        'usdjpy': {'name': 'USD/JPY Signal', 'desc': 'Get US Dollar vs Japanese Yen signal', 'category': 'trading'},
        'allsignals': {'name': 'All Signals', 'desc': 'Scan all available trading assets', 'category': 'trading'},
        'news': {'name': 'Market News', 'desc': 'Latest market news and updates', 'category': 'trading'},

        # Elite commands
        'ultra_btc': {'name': 'Ultra Elite BTC', 'desc': '95-98% win rate Bitcoin signals', 'category': 'elite'},
        'quantum_btc': {'name': 'Quantum Elite BTC', 'desc': 'AI-powered Bitcoin signals', 'category': 'elite'},
        'quantum': {'name': 'Quantum Signals', 'desc': 'All quantum elite signals', 'category': 'elite'},

        # Analysis commands
        'analytics': {'name': 'Performance Analytics', 'desc': 'Trading performance statistics', 'category': 'analytics'},
        'correlation': {'name': 'Asset Correlations', 'desc': 'Market correlation analysis', 'category': 'analytics'},
        'volatility': {'name': 'Market Volatility', 'desc': 'Volatility analysis and indicators', 'category': 'analytics'},
        'stats': {'name': 'User Statistics', 'desc': 'Your trading statistics', 'category': 'analytics'},

        # Learning commands
        'learn': {'name': 'Trading Tips', 'desc': '100+ trading tips and strategies', 'category': 'learning'},
        'glossary': {'name': 'Trading Glossary', 'desc': '200+ trading terms explained', 'category': 'learning'},
        'strategy': {'name': 'Strategy Guide', 'desc': 'Complete trading strategies', 'category': 'learning'},
        'tutorials': {'name': 'Video Tutorials', 'desc': 'Trading video tutorials', 'category': 'learning'},

        # Settings commands
        'language': {'name': 'Language Settings', 'desc': 'Change bot language', 'category': 'settings'},
        'timezone': {'name': 'Timezone Settings', 'desc': 'Set your timezone', 'category': 'settings'},
        'preferences': {'name': 'User Preferences', 'desc': 'Customize your experience', 'category': 'settings'},
        'notifications': {'name': 'Notification Settings', 'desc': 'Manage alerts and notifications', 'category': 'settings'},

        # Account commands
        'subscribe': {'name': 'Subscription Plans', 'desc': 'View premium plans and pricing', 'category': 'account'},
        'billing': {'name': 'Billing History', 'desc': 'View payment history and invoices', 'category': 'account'},
        'profile': {'name': 'User Profile', 'desc': 'View your profile and statistics', 'category': 'account'},

        # Special commands
        'start': {'name': 'Start Bot', 'desc': 'Welcome message and main menu', 'category': 'general'},
        'help': {'name': 'Help Center', 'desc': 'Command help and navigation', 'category': 'general'},
        'dashboard': {'name': 'Personal Dashboard', 'desc': 'Your personalized trading overview', 'category': 'general'},
        'quickstart': {'name': 'Quick Start Setup', 'desc': 'Interactive onboarding wizard', 'category': 'general'},
    },

    'assets': {
        'bitcoin': {'name': 'Bitcoin (BTC)', 'command': 'btc', 'desc': 'Cryptocurrency trading signals'},
        'btc': {'name': 'Bitcoin (BTC)', 'command': 'btc', 'desc': 'Cryptocurrency trading signals'},
        'gold': {'name': 'Gold (XAU/USD)', 'command': 'gold', 'desc': 'Precious metal trading signals'},
        'ethereum': {'name': 'Ethereum (ETH)', 'command': 'eth', 'desc': 'Cryptocurrency trading signals'},
        'eth': {'name': 'Ethereum (ETH)', 'command': 'eth', 'desc': 'Cryptocurrency trading signals'},
        'eurusd': {'name': 'EUR/USD', 'command': 'eurusd', 'desc': 'Euro vs US Dollar forex'},
        'gbpusd': {'name': 'GBP/USD', 'command': 'gbpusd', 'desc': 'British Pound vs US Dollar forex'},
        'usdjpy': {'name': 'USD/JPY', 'command': 'usdjpy', 'desc': 'US Dollar vs Japanese Yen forex'},
        'audusd': {'name': 'AUD/USD', 'command': 'audusd', 'desc': 'Australian Dollar vs US Dollar'},
        'nzdusd': {'name': 'NZD/USD', 'command': 'nzdusd', 'desc': 'New Zealand Dollar vs US Dollar'},
        'usdchf': {'name': 'USD/CHF', 'command': 'usdchf', 'desc': 'US Dollar vs Swiss Franc'},
        'usdcad': {'name': 'USD/CAD', 'command': 'usdcad', 'desc': 'US Dollar vs Canadian Dollar'},
        'eurjpy': {'name': 'EUR/JPY', 'command': 'eurjpy', 'desc': 'Euro vs Japanese Yen'},
        'eurgbp': {'name': 'EUR/GBP', 'command': 'eurgbp', 'desc': 'Euro vs British Pound'},
        'gbpjpy': {'name': 'GBP/JPY', 'command': 'gbpjpy', 'desc': 'British Pound vs Japanese Yen'},
        'audjpy': {'name': 'AUD/JPY', 'command': 'audjpy', 'desc': 'Australian Dollar vs Japanese Yen'},
        'es': {'name': 'E-mini S&P 500', 'command': 'es', 'desc': 'US futures contract'},
        'nq': {'name': 'E-mini NASDAQ-100', 'command': 'nq', 'desc': 'US futures contract'},
    },

    'topics': {
        'signals': {'name': 'Trading Signals', 'desc': 'How to get and use trading signals', 'category': 'trading'},
        'forex': {'name': 'Forex Trading', 'desc': 'Foreign exchange market information', 'category': 'trading'},
        'crypto': {'name': 'Cryptocurrency', 'desc': 'Bitcoin and crypto trading', 'category': 'trading'},
        'futures': {'name': 'Futures Trading', 'desc': 'US futures contracts (ES, NQ)', 'category': 'trading'},
        'analysis': {'name': 'Technical Analysis', 'desc': 'Chart analysis and indicators', 'category': 'analytics'},
        'risk': {'name': 'Risk Management', 'desc': 'Position sizing and risk control', 'category': 'analytics'},
        'strategy': {'name': 'Trading Strategy', 'desc': 'Trading strategies and approaches', 'category': 'learning'},
        'indicators': {'name': 'Technical Indicators', 'desc': 'Common trading indicators', 'category': 'learning'},
        'psychology': {'name': 'Trading Psychology', 'desc': 'Mental aspects of trading', 'category': 'learning'},
    }
}

class SearchHandler:
    """Handles intelligent search across commands, assets, and topics"""

    def __init__(self):
        self.search_db = SEARCH_DATABASE

    def search(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Search for commands, assets, and topics matching the query
        Returns list of matching items with scores
        """
        query = query.lower().strip()
        if not query:
            return []

        results = []

        # Search commands
        for cmd, info in self.search_db['commands'].items():
            score = self._calculate_match_score(query, cmd, info)
            if score > 0:
                results.append({
                    'type': 'command',
                    'key': cmd,
                    'name': info['name'],
                    'description': info['desc'],
                    'category': info['category'],
                    'score': score,
                    'command': f"/{cmd}"
                })

        # Search assets
        for asset_key, info in self.search_db['assets'].items():
            score = self._calculate_match_score(query, asset_key, info)
            if score > 0:
                results.append({
                    'type': 'asset',
                    'key': asset_key,
                    'name': info['name'],
                    'description': info['desc'],
                    'category': 'trading',
                    'score': score,
                    'command': f"/{info['command']}"
                })

        # Search topics
        for topic_key, info in self.search_db['topics'].items():
            score = self._calculate_match_score(query, topic_key, info)
            if score > 0:
                results.append({
                    'type': 'topic',
                    'key': topic_key,
                    'name': info['name'],
                    'description': info['desc'],
                    'category': info['category'],
                    'score': score,
                    'command': None  # Topics don't have direct commands
                })

        # Sort by score (highest first) and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def _calculate_match_score(self, query: str, key: str, info: Dict) -> float:
        """Calculate how well a query matches an item"""
        score = 0.0

        # Exact command match gets highest score
        if query == key:
            score += 100.0

        # Partial command match
        if query in key:
            score += 50.0

        # Name contains query
        name_lower = info['name'].lower()
        if query in name_lower:
            score += 30.0

        # Description contains query
        desc_lower = info.get('description', '').lower()
        if query in desc_lower:
            score += 20.0

        # Fuzzy matching - query letters appear in order
        if self._fuzzy_match(query, key):
            score += 15.0
        if self._fuzzy_match(query, name_lower):
            score += 10.0

        # Category bonus for relevant searches
        category_keywords = {
            'trading': ['trade', 'signal', 'buy', 'sell', 'market'],
            'analytics': ['analysis', 'chart', 'technical', 'stats', 'performance'],
            'learning': ['learn', 'tutorial', 'guide', 'tip', 'strategy'],
            'settings': ['setting', 'preference', 'language', 'notification']
        }

        item_category = info.get('category', '')
        for cat, keywords in category_keywords.items():
            if any(kw in query for kw in keywords) and item_category == cat:
                score += 5.0

        return score

    def _fuzzy_match(self, query: str, target: str) -> bool:
        """Check if query letters appear in order in target (fuzzy match)"""
        query_idx = 0
        for char in target:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
                if query_idx == len(query):
                    return True
        return query_idx == len(query)

    def format_search_results(self, query: str, results: List[Dict[str, Any]]) -> Tuple[str, InlineKeyboardMarkup]:
        """Format search results into message and keyboard"""
        if not results:
            message = f"🔍 <b>Search Results for '{query}'</b>\n\n"
            message += "❌ No matches found.\n\n"
            message += "💡 <b>Try searching for:</b>\n"
            message += "• Asset names (bitcoin, gold, eurusd)\n"
            message += "• Command names (signals, analytics)\n"
            message += "• Topics (forex, strategy, risk)\n\n"
            message += "📝 <i>Use /help for all available commands</i>"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 Full Help", callback_data="cmd_help")],
                [InlineKeyboardButton("🚀 Quick Start", callback_data="onboard_start")]
            ])
            return message, keyboard

        message = f"🔍 <b>Search Results for '{query}'</b>\n\n"
        message += f"Found {len(results)} matches:\n\n"

        keyboard_buttons = []

        for i, result in enumerate(results, 1):
            emoji_map = {
                'command': '📝',
                'asset': '💎',
                'topic': '📚'
            }

            emoji = emoji_map.get(result['type'], '•')
            message += f"{emoji} <b>{result['name']}</b>\n"
            message += f"   {result['description']}\n"

            if result['command']:
                message += f"   <code>{result['command']}</code>\n"
                # Add button for commands and assets
                button_text = f"{result['name'][:20]}..."
                if result['type'] == 'command':
                    callback_data = f"cmd_{result['key']}"
                else:  # asset
                    callback_data = f"cmd_{result['key']}"

                keyboard_buttons.append(
                    InlineKeyboardButton(button_text, callback_data=callback_data)
                )

            message += "\n"

        # Create keyboard with buttons (max 2 per row)
        keyboard = []
        for i in range(0, len(keyboard_buttons), 2):
            row = keyboard_buttons[i:i+2]
            keyboard.append(row)

        # Add footer buttons
        keyboard.append([
            InlineKeyboardButton("🔍 New Search", callback_data="search_again"),
            InlineKeyboardButton("📚 Full Help", callback_data="cmd_help")
        ])

        return message, InlineKeyboardMarkup(keyboard)

# Global search handler instance
search_handler = SearchHandler()
