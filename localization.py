"""
International Localization System
Supports multiple languages, timezones, and regional preferences
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any, List
from pathlib import Path
import pytz

class LocalizationManager:
    """Manages localization for multiple languages and regions"""

    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.languages = {}
        self.timezones = {}
        self.currency_symbols = {}
        self.date_formats = {}
        self.user_preferences = {}

        # Load all localization data
        self._load_languages()
        self._load_timezones()
        self._load_currencies()
        self._load_date_formats()

        # Default language
        self.default_language = 'en'

    def _load_languages(self):
        """Load language files"""
        languages_dir = self.current_dir / 'languages'
        languages_dir.mkdir(exist_ok=True)

        # Create default English language file if it doesn't exist
        en_file = languages_dir / 'en.json'
        if not en_file.exists():
            self._create_english_translations(en_file)

        # Load all language files
        for lang_file in languages_dir.glob('*.json'):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.languages[lang_code] = json.load(f)
                print(f"Loaded language: {lang_code}")
            except Exception as e:
                print(f"Error loading language {lang_code}: {e}")

    def _create_english_translations(self, filepath):
        """Create comprehensive English translations"""
        translations = {
            "welcome": {
                "title": "🌟 Welcome to UR Trading Expert Bot!",
                "description": "Your AI-powered trading companion with professional signals",
                "get_started": "Get Started",
                "features": "Features",
                "pricing": "Pricing"
            },
            "commands": {
                "help": "Help & Commands",
                "signals": "Trading Signals",
                "analytics": "Analytics",
                "education": "Education",
                "notifications": "Notifications",
                "account": "My Account",
                "settings": "Settings"
            },
            "signals": {
                "direction_buy": "📈 BUY",
                "direction_sell": "📉 SELL",
                "direction_hold": "⏸️ HOLD",
                "confidence": "Confidence",
                "entry_price": "Entry Price",
                "stop_loss": "Stop Loss",
                "take_profit": "Take Profit",
                "risk_reward": "Risk-Reward Ratio",
                "analysis": "Analysis",
                "generated_at": "Generated",
                "signal_quality": "Signal Quality",
                "trading_hours": "Trading Hours"
            },
            "markets": {
                "forex": "Forex",
                "crypto": "Cryptocurrency",
                "commodities": "Commodities",
                "futures": "Futures",
                "international": "International Markets"
            },
            "subscription": {
                "free_tier": "Free",
                "premium_tier": "Premium",
                "vip_tier": "VIP",
                "upgrade_required": "Upgrade Required",
                "upgrade_now": "Upgrade Now",
                "billing": "Billing & Subscription"
            },
            "errors": {
                "general_error": "An error occurred. Please try again.",
                "permission_denied": "You don't have permission to use this feature.",
                "rate_limit": "Too many requests. Please wait and try again.",
                "service_unavailable": "Service temporarily unavailable.",
                "invalid_command": "Invalid command. Use /help for available commands."
            },
            "time": {
                "just_now": "Just now",
                "minutes_ago": "{} minutes ago",
                "hours_ago": "{} hours ago",
                "days_ago": "{} days ago",
                "yesterday": "Yesterday",
                "today": "Today",
                "tomorrow": "Tomorrow"
            },
            "numbers": {
                "decimal_separator": ".",
                "thousands_separator": ",",
                "currency_format": "${:,.2f}",
                "percentage_format": "{:.1f}%"
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)

    def _load_timezones(self):
        """Load timezone information"""
        self.timezones = {
            'UTC': 'UTC',
            'EST': 'US/Eastern',
            'CST': 'US/Central',
            'MST': 'US/Mountain',
            'PST': 'US/Pacific',
            'GMT': 'GMT',
            'BST': 'Europe/London',
            'CET': 'Europe/Berlin',
            'EET': 'Europe/Athens',
            'MSK': 'Europe/Moscow',
            'JST': 'Asia/Tokyo',
            'CST_ASIA': 'Asia/Shanghai',
            'IST': 'Asia/Kolkata',
            'AEST': 'Australia/Sydney',
            'BRT': 'America/Sao_Paulo',
            'ART': 'America/Argentina/Buenos_Aires'
        }

        # Create timezone display names
        self.timezone_names = {
            'UTC': 'UTC',
            'EST': 'Eastern Time (US)',
            'CST': 'Central Time (US)',
            'MST': 'Mountain Time (US)',
            'PST': 'Pacific Time (US)',
            'GMT': 'Greenwich Mean Time',
            'BST': 'British Summer Time',
            'CET': 'Central European Time',
            'EET': 'Eastern European Time',
            'MSK': 'Moscow Standard Time',
            'JST': 'Japan Standard Time',
            'CST_ASIA': 'China Standard Time',
            'IST': 'India Standard Time',
            'AEST': 'Australian Eastern Time',
            'BRT': 'Brasília Time',
            'ART': 'Argentina Time'
        }

    def _load_currencies(self):
        """Load currency information"""
        self.currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'CNY': '¥',
            'BRL': 'R$',
            'RUB': '₽',
            'SAR': '﷼',
            'AED': 'د.إ'
        }

        self.currency_names = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'CNY': 'Chinese Yuan',
            'BRL': 'Brazilian Real',
            'RUB': 'Russian Ruble',
            'SAR': 'Saudi Riyal',
            'AED': 'UAE Dirham'
        }

    def _load_date_formats(self):
        """Load date format preferences"""
        self.date_formats = {
            'us': '%m/%d/%Y',  # MM/DD/YYYY
            'eu': '%d/%m/%Y',  # DD/MM/YYYY
            'iso': '%Y-%m-%d', # YYYY-MM-DD
            'jp': '%Y年%m月%d日' # Japanese format
        }

        self.time_formats = {
            '12h': '%I:%M %p',  # 12-hour format
            '24h': '%H:%M'      # 24-hour format
        }

    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """Get localized text for a key"""
        if not language:
            language = self.default_language

        # Navigate through nested dictionary
        keys = key.split('.')
        value = self.languages.get(language, self.languages.get(self.default_language, {}))

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, key)  # Return key if not found
            else:
                return key

        # If value is still a dict, return the key
        if isinstance(value, dict):
            return key

        # Format string if kwargs provided
        if kwargs and isinstance(value, str):
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value

        return str(value)

    def format_currency(self, amount: float, currency: str = 'USD', language: str = None) -> str:
        """Format currency amount according to locale"""
        symbol = self.currency_symbols.get(currency, '$')

        if language in ['de', 'fr', 'es', 'pt']:
            # European style: 1.234,56 €
            formatted = f"{amount:,.2f}".replace(',', ' ').replace('.', ',').replace(' ', '.')
        elif language == 'jp':
            # Japanese style: ¥1,234
            formatted = f"{amount:,.0f}"
        elif language == 'zh':
            # Chinese style: ¥1,234.56
            formatted = f"{amount:,.2f}"
        else:
            # US style: $1,234.56
            formatted = f"{amount:,.2f}"

        return f"{symbol}{formatted}"

    def format_datetime(self, dt: datetime, timezone_str: str = 'UTC',
                       date_format: str = 'us', time_format: str = '24h',
                       language: str = None) -> str:
        """Format datetime according to user preferences"""
        try:
            # Convert to user's timezone
            user_tz = pytz.timezone(self.timezones.get(timezone_str, 'UTC'))
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            dt = dt.astimezone(user_tz)

            # Get format strings
            date_fmt = self.date_formats.get(date_format, self.date_formats['us'])
            time_fmt = self.time_formats.get(time_format, self.time_formats['24h'])

            # Combine formats
            datetime_fmt = f"{date_fmt} {time_fmt}"

            return dt.strftime(datetime_fmt)

        except Exception as e:
            # Fallback to ISO format
            return dt.strftime('%Y-%m-%d %H:%M UTC')

    def format_relative_time(self, dt: datetime, language: str = None) -> str:
        """Format relative time (e.g., '2 hours ago')"""
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        diff = now - dt
        minutes = diff.total_seconds() / 60
        hours = minutes / 60
        days = hours / 24

        if minutes < 1:
            return self.get_text('time.just_now', language)
        elif minutes < 60:
            return self.get_text('time.minutes_ago', language, int(minutes))
        elif hours < 24:
            return self.get_text('time.hours_ago', language, int(hours))
        elif days < 2:
            return self.get_text('time.yesterday', language)
        else:
            return self.get_text('time.days_ago', language, int(days))

    def detect_user_language(self, user_id: int) -> str:
        """Detect user's preferred language (from stored preferences or location)"""
        # Check if user has set a preference
        if user_id in self.user_preferences:
            return self.user_preferences[user_id].get('language', self.default_language)

        # Default to English
        return self.default_language

    def set_user_language(self, user_id: int, language: str):
        """Set user's language preference"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}

        self.user_preferences[user_id]['language'] = language

    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return list(self.languages.keys())

    def get_language_name(self, code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            'en': 'English',
            'es': 'Español',
            'pt': 'Português',
            'zh': '中文',
            'ar': 'العربية',
            'ru': 'Русский',
            'de': 'Deutsch',
            'fr': 'Français',
            'ja': '日本語'
        }
        return language_names.get(code, code.upper())

    def create_language_file(self, language_code: str, base_translations: Dict = None):
        """Create a new language file based on English translations"""
        if base_translations is None:
            base_translations = self.languages.get('en', {})

        # Create a copy for translation
        translations = json.loads(json.dumps(base_translations))

        # Mark untranslated strings
        def mark_untranslated(obj, lang_code):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and not value.startswith(f"[{lang_code}]"):
                        obj[key] = f"[{lang_code}] {value}"
                    elif isinstance(value, dict):
                        mark_untranslated(value, lang_code)

        mark_untranslated(translations, language_code)

        # Save the file
        languages_dir = self.current_dir / 'languages'
        languages_dir.mkdir(exist_ok=True)

        filepath = languages_dir / f'{language_code}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)

        # Load the new language
        self.languages[language_code] = translations

        return filepath

# Global instance
localization = LocalizationManager()

# Convenience functions
def get_text(key: str, language: str = None, **kwargs) -> str:
    """Get localized text"""
    return localization.get_text(key, language, **kwargs)

def format_currency(amount: float, currency: str = 'USD', language: str = None) -> str:
    """Format currency"""
    return localization.format_currency(amount, currency, language)

def format_datetime(dt: datetime, timezone_str: str = 'UTC', language: str = None) -> str:
    """Format datetime"""
    return localization.format_datetime(dt, timezone_str, language=language)

def detect_user_language(user_id: int) -> str:
    """Detect user language"""
    return localization.detect_user_language(user_id)

def set_user_language(user_id: int, language: str):
    """Set user language"""
    localization.set_user_language(user_id, language)

# Initialize when module is imported
if __name__ != "__main__":
    print("International Localization System loaded")
    print(f"Available languages: {', '.join(localization.get_available_languages())}")
