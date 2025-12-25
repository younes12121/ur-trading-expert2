"""
🌍 Localization System for UR Trading Expert Bot
Supports multiple languages, timezones, and regional regulations
"""

import json
import os
import pytz
from datetime import datetime, timezone
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

@dataclass
class LocalizedMessage:
    """Container for localized message data"""
    key: str
    language: str
    text: str
    context: Optional[str] = None

class LocalizationManager:
    """Manages localization for the trading bot"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.languages = {
            'en': 'English',
            'es': 'Español',
            'ar': 'العربية',
            'zh': '中文',
            'ru': 'Русский',
            'pt': 'Português',
            'ja': '日本語',
            'de': 'Deutsch',
            'fr': 'Français',
            'hi': 'हिन्दी'
        }

        # Default language
        self.default_language = 'en'

        # Timezone mappings
        self.timezone_groups = {
            'americas': ['US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific',
                        'America/Sao_Paulo', 'America/Mexico_City', 'America/Buenos_Aires'],
            'europe': ['Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome',
                      'Europe/Moscow', 'Europe/Amsterdam'],
            'asia': ['Asia/Tokyo', 'Asia/Shanghai', 'Asia/Hong_Kong', 'Asia/Singapore',
                    'Asia/Dubai', 'Asia/Kolkata'],
            'pacific': ['Australia/Sydney', 'Australia/Melbourne', 'Pacific/Auckland',
                       'Asia/Manila']
        }

        # Load translations
        self.translations = self._load_translations()

        # Regional regulations
        self.regulations = self._load_regulations()

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation files"""
        translations = {}

        # Create default English translations
        translations['en'] = self._get_english_translations()

        # Load other languages
        for lang_code in self.languages.keys():
            if lang_code != 'en':
                translations[lang_code] = self._load_language_translations(lang_code)

        return translations

    def _get_english_translations(self) -> Dict[str, str]:
        """Get comprehensive English translations"""
        return {
            # Core Commands
            'welcome': "🚀 Welcome to UR Trading Expert Bot!\n\nYour AI-powered trading companion with professional signals.",
            'help_menu': "📋 **COMMAND MENU**\n\n🎯 **Trading Signals**\n• /btc - Bitcoin analysis\n• /gold - Gold signals\n• /international - Global markets\n\n📊 **Analytics**\n• /analytics - Performance stats\n• /correlation - Asset correlation\n\n💰 **Account**\n• /subscribe - Plans & pricing\n• /billing - Subscription management\n\n📚 **Education**\n• /learn - Trading tips\n• /glossary - Terms dictionary\n\n🔔 **Notifications**\n• /notifications - Alert preferences",

            # Signal Messages
            'signal_buy': "📈 **BUY SIGNAL**",
            'signal_sell': "📉 **SELL SIGNAL**",
            'signal_hold': "⏸️ **HOLD**",
            'confidence': "🎯 Confidence",
            'entry_price': "💰 Entry Price",
            'stop_loss': "🛡️ Stop Loss",
            'take_profit': "💎 Take Profit",
            'risk_reward': "⚖️ Risk-Reward Ratio",

            # International Markets
            'cny_description': "🇨🇳 **Chinese Yuan (CNY)**\n\nAsia's largest economy currency with low volatility and strong fundamentals.",
            'brl_description': "🇧🇷 **Brazilian Real (BRL)**\n\nEmerging market currency with high volatility and commodity exposure.",
            'eth_description': "₿ **Ethereum Futures (ETH)**\n\nSmart contract platform with extreme volatility and 24/7 trading.",

            # Subscription Messages
            'premium_required': "⭐ **PREMIUM FEATURE**\n\nThis feature requires a Premium subscription.",
            'vip_required': "💎 **VIP FEATURE**\n\nThis feature requires a VIP subscription.",
            'upgrade_prompt': "💳 Use /subscribe to upgrade your plan!",

            # Error Messages
            'no_permission': "❌ You don't have permission to use this feature.",
            'rate_limit': "⏳ Too many requests. Please wait a moment.",
            'service_unavailable': "🔧 Service temporarily unavailable. Please try again later.",
            'invalid_command': "❓ Invalid command. Use /help for available commands.",

            # Time Messages
            'market_open': "🟢 Market is open",
            'market_closed': "🔴 Market is closed",
            'next_session': "Next trading session",
            'current_time': "Current time",

            # Educational Content
            'trading_tips': "💡 **Trading Tips**\n\n• Always use stop losses\n• Never risk more than 2% per trade\n• Follow your trading plan\n• Keep emotions in check",
            'common_mistakes': "❌ **Common Trading Mistakes**\n\n• Overtrading\n• Revenge trading\n• Ignoring risk management\n• Following the crowd",

            # Performance Messages
            'win_rate': "🎯 Win Rate",
            'total_trades': "📊 Total Trades",
            'profit_factor': "💰 Profit Factor",
            'max_drawdown': "📉 Max Drawdown",
            'sharpe_ratio': "📈 Sharpe Ratio",

            # Notification Messages
            'alert_triggered': "🚨 **ALERT TRIGGERED**",
            'signal_ready': "🟢 **SIGNAL READY**",
            'price_alert': "💰 **PRICE ALERT**",
            'session_start': "🔔 **TRADING SESSION START**",

            # Subscription Plans
            'free_plan': "🆓 **FREE PLAN**\n• 2 Forex pairs\n• Basic signals\n• Limited analytics",
            'premium_plan': "⭐ **PREMIUM PLAN - $39/month**\n• All 16 assets + International\n• Unlimited alerts\n• Full analytics\n• AI predictions",
            'vip_plan': "💎 **VIP PLAN - $129/month**\n• Everything in Premium\n• Crypto futures\n• Broker integration\n• Private community",

            # Success Messages
            'subscription_success': "✅ **Subscription Activated!**\n\nWelcome to premium trading features!",
            'payment_success': "💳 **Payment Successful!**\n\nThank you for your subscription.",
            'profile_updated': "👤 **Profile Updated**\n\nYour settings have been saved.",

            # Regional Regulations
            'us_regulation': "🇺🇸 **US Regulation Notice**\n\nThis is not investment advice. Past performance ≠ future results.",
            'eu_regulation': "🇪🇺 **EU Regulation Notice**\n\nThis service is for educational purposes. CFDs are high-risk products.",
            'asia_regulation': "🇨🇳 **Asia Regulation Notice**\n\nTrading involves substantial risk. Not suitable for all investors.",
            'emerging_regulation': "🌍 **Emerging Markets Notice**\n\nHigher volatility and political risk may affect trading.",
            'language_updated': 'Language Updated!',
            'language_set_to': 'Language set to: {lang}',
            'all_responses_in_language': 'All responses will now be in {lang}',
            'timezone_updated': 'Timezone Updated!',
            'timezone_set_to': 'Timezone set to: {tz}',
            'local_time': 'Local Time',
            'signal_timings_adjusted': 'Signal timings will be adjusted for your timezone',
            'region_updated': 'Region Updated!',
            'region_set_to': 'Region set to: {region}',
            'compliance_updated': 'Compliance settings updated for your region'
        }

    def _load_language_translations(self, lang_code: str) -> Dict[str, str]:
        """Load translations for a specific language"""
        # For now, return English as fallback
        # In production, load from JSON files
        try:
            # Try to load from file
            file_path = f"locales/{lang_code}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                return translations
            else:
                # Return English with language markers for development
                english = self._get_english_translations().copy()
                # Add language indicator for untranslated strings
                for key in english:
                    english[key] = f"[{lang_code.upper()}] {english[key]}"
                return english
        except Exception as e:
            self.logger.error(f"Failed to load {lang_code} translations: {e}")
            return self._get_english_translations()

    def _load_regulations(self) -> Dict[str, Dict[str, str]]:
        """Load regional regulations"""
        return {
            'us': {
                'disclaimer': "🇺🇸 This is not investment advice. Trade at your own risk.",
                'cfd_warning': "CFDs are complex instruments with high risk of loss.",
                'past_performance': "Past performance does not guarantee future results."
            },
            'eu': {
                'disclaimer': "🇪🇺 This service is for educational purposes only.",
                'cfd_warning': "CFDs are high-risk products. 74% of retail CFD accounts lose money.",
                'gdpr_compliance': "Your data is protected under GDPR regulations."
            },
            'asia': {
                'disclaimer': "🇨🇳 Trading involves substantial risk and is not suitable for all investors.",
                'cfd_warning': "High volatility may result in significant losses.",
                'regulation_note': "Regulated financial products may be subject to local laws."
            },
            'latin_america': {
                'disclaimer': "🇧🇷 Trading forex and CFDs involves high risk.",
                'emerging_warning': "Emerging market currencies may be subject to political risk.",
                'regulation_note': "Local regulations may apply."
            },
            'middle_east': {
                'disclaimer': "🇸🇦 Trading involves risk. Not all products are available in all regions.",
                'islamic_finance': "Islamic finance compliant products may be available.",
                'regulation_note': "Subject to local regulatory requirements."
            }
        }

    def get_message(self, key: str, language: str = 'en', **kwargs) -> str:
        """Get localized message with formatting"""
        lang_translations = self.translations.get(language, self.translations[self.default_language])
        message = lang_translations.get(key, self.translations[self.default_language].get(key, f"[{key}]"))

        # Format message with kwargs
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return unformatted message if formatting fails

        return message

    def get_timezone_info(self, user_timezone: str = None) -> Dict:
        """Get timezone information and market hours"""
        if not user_timezone:
            user_timezone = 'UTC'

        try:
            tz = pytz.timezone(user_timezone)
            now = datetime.now(tz)

            # Determine market sessions
            market_sessions = self._get_market_sessions(now)

            return {
                'timezone': user_timezone,
                'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'utc_offset': now.strftime('%z'),
                'market_sessions': market_sessions,
                'next_session': self._get_next_session(now)
            }
        except Exception as e:
            self.logger.error(f"Timezone error: {e}")
            return {
                'timezone': 'UTC',
                'current_time': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                'utc_offset': '+0000',
                'market_sessions': {},
                'next_session': None
            }

    def _get_market_sessions(self, current_time: datetime) -> Dict[str, bool]:
        """Determine which market sessions are currently open"""
        sessions = {
            'tokyo': self._is_session_open(current_time, 0, 6),  # 00:00-06:00 UTC
            'london': self._is_session_open(current_time, 8, 16),  # 08:00-16:00 UTC
            'new_york': self._is_session_open(current_time, 14, 21),  # 14:00-21:00 UTC
            'sydney': self._is_session_open(current_time, 22, 6),  # 22:00-06:00 UTC (next day)
            'crypto': True  # Always open
        }
        return sessions

    def _is_session_open(self, current_time: datetime, start_hour: int, end_hour: int) -> bool:
        """Check if a trading session is open"""
        current_hour = current_time.hour

        if start_hour < end_hour:
            # Same day session
            return start_hour <= current_hour < end_hour
        else:
            # Overnight session
            return current_hour >= start_hour or current_hour < end_hour

    def _get_next_session(self, current_time: datetime) -> Optional[str]:
        """Get the next trading session"""
        sessions = [
            ('Tokyo', 0),
            ('London', 8),
            ('New York', 14),
            ('Sydney', 22)
        ]

        current_hour = current_time.hour
        next_sessions = []

        for name, hour in sessions:
            if hour > current_hour:
                hours_until = hour - current_hour
                next_sessions.append((name, hours_until))
            else:
                hours_until = (24 - current_hour) + hour
                next_sessions.append((name, hours_until))

        if next_sessions:
            next_session = min(next_sessions, key=lambda x: x[1])
            return f"{next_session[0]} session in {next_session[1]} hours"

        return None

    def get_regional_regulation(self, region: str) -> Dict[str, str]:
        """Get regional regulatory information"""
        return self.regulations.get(region.lower(), self.regulations.get('us', {}))

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.languages.copy()

    def format_currency(self, amount: float, currency: str = 'USD', language: str = 'en') -> str:
        """Format currency amounts according to locale"""
        try:
            if language == 'es':
                return f"{amount:,.2f} {currency}".replace(',', ' ').replace('.', ',')
            elif language == 'de':
                return f"{amount:,.2f} {currency}".replace(',', ' ').replace('.', ',')
            elif language == 'zh':
                return f"{currency}{amount:,.0f}"
            elif language == 'ar':
                return f"{amount:,.2f} {currency}"  # RTL formatting would be handled by Telegram
            else:
                return f"{currency}{amount:,.2f}"
        except:
            return f"{currency}{amount:.2f}"

    def format_datetime(self, dt: datetime, language: str = 'en') -> str:
        """Format datetime according to locale"""
        try:
            if language == 'zh':
                return dt.strftime('%Y年%m月%d日 %H:%M:%S')
            elif language == 'ar':
                return dt.strftime('%d/%m/%Y %H:%M:%S')  # Arabic date format
            else:
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt.strftime('%Y-%m-%d %H:%M:%S')

# Global instance
localization = LocalizationManager()

# Convenience functions
def get_localized_message(key: str, language: str = 'en', **kwargs) -> str:
    """Get a localized message"""
    return localization.get_message(key, language, **kwargs)

def get_timezone_info(timezone: str = None) -> Dict:
    """Get timezone information"""
    return localization.get_timezone_info(timezone)

def get_regional_regulation(region: str) -> Dict[str, str]:
    """Get regional regulation info"""
    return localization.get_regional_regulation(region)

if __name__ == "__main__":
    # Test the localization system
    print("🌍 Localization System Test")
    print("=" * 50)

    # Test languages
    print(f"Supported languages: {localization.get_supported_languages()}")

    # Test messages
    print(f"\nEnglish welcome: {get_localized_message('welcome', 'en')}")
    print(f"Spanish welcome: {get_localized_message('welcome', 'es')}")

    # Test timezone
    tz_info = get_timezone_info('America/New_York')
    print(f"\nTimezone info: {tz_info}")

    # Test regulations
    us_regulation = get_regional_regulation('us')
    print(f"\nUS regulation: {us_regulation}")

    print("\nLocalization system test completed!")
