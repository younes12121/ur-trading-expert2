"""
Onboarding Flow Module
Interactive wizard for new users to set up preferences and get started
"""

import json
import os
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Import user preferences manager and templates
try:
    from user_preferences import user_prefs, UserPreferences
    from bot_templates import get_onboarding_message
except ImportError:
    user_prefs = None
    get_onboarding_message = None

# Onboarding flow states
ONBOARDING_STATES = {
    'WELCOME': 'welcome',
    'LANGUAGE': 'language',
    'TIMEZONE': 'timezone',
    'EXPERIENCE': 'experience',
    'ASSETS': 'assets',
    'RISK': 'risk',
    'NOTIFICATIONS': 'notifications',
    'COMPLETE': 'complete'
}

# Available assets for selection
AVAILABLE_ASSETS = {
    'forex': {
        'EURUSD': '🇪🇺🇺🇸 EUR/USD - Euro vs US Dollar',
        'GBPUSD': '🇬🇧🇺🇸 GBP/USD - British Pound vs US Dollar',
        'USDJPY': '🇺🇸🇯🇵 USD/JPY - US Dollar vs Japanese Yen',
        'AUDUSD': '🇦🇺🇺🇸 AUD/USD - Australian Dollar vs US Dollar',
        'USDCAD': '🇺🇸🇨🇦 USD/CAD - US Dollar vs Canadian Dollar'
    },
    'crypto': {
        'BTC': '₿ Bitcoin (BTC/USD)',
        'ETH': 'Ξ Ethereum (ETH/USD)'
    },
    'commodities': {
        'GOLD': '🥇 Gold (XAU/USD)'
    },
    'futures': {
        'ES': '📊 E-mini S&P 500',
        'NQ': '🚀 E-mini NASDAQ-100'
    }
}

class OnboardingFlow:
    """Manages the interactive onboarding process for new users"""

    def __init__(self):
        self.active_flows = {}  # {user_id: {'state': state, 'data': {}}}

    def start_flow(self, user_id: int) -> Dict[str, Any]:
        """Start a new onboarding flow for a user"""
        flow_data = {
            'state': ONBOARDING_STATES['WELCOME'],
            'data': {
                'language': 'en',
                'timezone': 'UTC',
                'experience_level': 'beginner',
                'preferred_assets': [],
                'risk_tolerance': 'medium',
                'notifications_enabled': True,
                'price_alerts_enabled': False
            },
            'step': 1,
            'total_steps': 6
        }

        self.active_flows[user_id] = flow_data
        return flow_data

    def get_current_step(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current onboarding step for user"""
        return self.active_flows.get(user_id)

    def update_flow_data(self, user_id: int, key: str, value: Any):
        """Update flow data for a user"""
        if user_id in self.active_flows:
            self.active_flows[user_id]['data'][key] = value

    def next_step(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Advance to next step in onboarding flow"""
        if user_id not in self.active_flows:
            return None

        current_state = self.active_flows[user_id]['state']

        # Define flow progression
        flow_progression = {
            ONBOARDING_STATES['WELCOME']: ONBOARDING_STATES['LANGUAGE'],
            ONBOARDING_STATES['LANGUAGE']: ONBOARDING_STATES['TIMEZONE'],
            ONBOARDING_STATES['TIMEZONE']: ONBOARDING_STATES['EXPERIENCE'],
            ONBOARDING_STATES['EXPERIENCE']: ONBOARDING_STATES['ASSETS'],
            ONBOARDING_STATES['ASSETS']: ONBOARDING_STATES['RISK'],
            ONBOARDING_STATES['RISK']: ONBOARDING_STATES['NOTIFICATIONS'],
            ONBOARDING_STATES['NOTIFICATIONS']: ONBOARDING_STATES['COMPLETE']
        }

        if current_state in flow_progression:
            self.active_flows[user_id]['state'] = flow_progression[current_state]
            self.active_flows[user_id]['step'] += 1

        return self.active_flows[user_id]

    def complete_flow(self, user_id: int) -> Dict[str, Any]:
        """Complete onboarding and save preferences"""
        if user_id not in self.active_flows:
            return {}

        flow_data = self.active_flows[user_id]

        # Save to user preferences if available
        if user_prefs:
            try:
                # Get existing preferences or create new ones
                existing_prefs = user_prefs.get_user_preferences(user_id)
                if existing_prefs:
                    # Update existing preferences
                    existing_prefs.language = flow_data['data']['language']
                    existing_prefs.timezone = flow_data['data']['timezone']
                    existing_prefs.risk_tolerance = flow_data['data']['risk_tolerance']
                    existing_prefs.preferred_assets = flow_data['data']['preferred_assets']
                    existing_prefs.notifications_enabled = flow_data['data']['notifications_enabled']
                    existing_prefs.price_alerts_enabled = flow_data['data']['price_alerts_enabled']
                    user_prefs.update_user_preferences(user_id, existing_prefs)
                else:
                    # Create new preferences
                    new_prefs = UserPreferences(
                        telegram_id=user_id,
                        language=flow_data['data']['language'],
                        timezone=flow_data['data']['timezone'],
                        risk_tolerance=flow_data['data']['risk_tolerance'],
                        preferred_assets=flow_data['data']['preferred_assets'],
                        notifications_enabled=flow_data['data']['notifications_enabled'],
                        price_alerts_enabled=flow_data['data']['price_alerts_enabled']
                    )
                    user_prefs.update_user_preferences(user_id, new_prefs)
            except Exception as e:
                print(f"Failed to save onboarding preferences: {e}")

        # Remove from active flows
        del self.active_flows[user_id]

        return flow_data['data']

    def get_step_message(self, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
        """Get message and keyboard for current step"""
        flow = self.get_current_step(user_id)
        if not flow:
            return "Onboarding not found. Please start with /quickstart", None

        state = flow['state']
        step = flow['step']
        total_steps = flow['total_steps']

        if state == ONBOARDING_STATES['WELCOME']:
            if get_onboarding_message:
                message = get_onboarding_message('welcome_step', name="Trader")
            else:
                message = "🎯 <b>QUICK START WIZARD</b>\n\n"
                message += "✨ <b>Welcome, Trader!</b>\n\n"
                message += "This quick setup will personalize your experience and help you get the most out of AI-powered trading signals.\n\n"
                message += "<i>Only takes 2 minutes!</i>\n\n"
                message += "Ready to begin?"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start Setup", callback_data="onboard_start")],
                [InlineKeyboardButton("⏭️ Skip to Main Menu", callback_data="onboard_skip")]
            ])

        elif state == ONBOARDING_STATES['LANGUAGE']:
            message = "🌐 <b>Choose Your Language</b>\n\n"
            message += f"Step {step}/{total_steps}: Select your preferred language\n\n"
            message += "🇺🇸 English (Default)\n"
            message += "🇪🇸 Español\n"
            message += "🇸🇦 العربية\n"
            message += "🇨🇳 中文\n"
            message += "🇷🇺 Русский"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
                 InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")],
                [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
                 InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")],
                [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
                 InlineKeyboardButton("🔙 Back", callback_data="onboard_back")]
            ])

        elif state == ONBOARDING_STATES['TIMEZONE']:
            message = "🕐 <b>Set Your Timezone</b>\n\n"
            message += f"Step {step}/{total_steps}: Choose your timezone for accurate market timing\n\n"
            message += "This affects when you receive signals and market updates."

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🇺🇸 Eastern (EST)", callback_data="tz_Eastern"),
                 InlineKeyboardButton("🇺🇸 Central (CST)", callback_data="tz_Central")],
                [InlineKeyboardButton("🇺🇸 Pacific (PST)", callback_data="tz_Pacific"),
                 InlineKeyboardButton("🇬🇧 London (GMT)", callback_data="tz_GMT")],
                [InlineKeyboardButton("🇩🇪 Berlin (CET)", callback_data="tz_CET"),
                 InlineKeyboardButton("🇯🇵 Tokyo (JST)", callback_data="tz_JST")],
                [InlineKeyboardButton("🌍 UTC", callback_data="tz_UTC"),
                 InlineKeyboardButton("🔙 Back", callback_data="onboard_back")]
            ])

        elif state == ONBOARDING_STATES['EXPERIENCE']:
            message = "📊 <b>Your Trading Experience</b>\n\n"
            message += f"Step {step}/{total_steps}: Tell us about your trading background\n\n"
            message += "This helps us show you the right information and complexity level."

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🆕 Beginner - New to trading", callback_data="exp_beginner")],
                [InlineKeyboardButton("📈 Intermediate - Some experience", callback_data="exp_intermediate")],
                [InlineKeyboardButton("💼 Advanced - Experienced trader", callback_data="exp_advanced")],
                [InlineKeyboardButton("🔙 Back", callback_data="onboard_back")]
            ])

        elif state == ONBOARDING_STATES['ASSETS']:
            message = "💎 <b>Choose Your Assets</b>\n\n"
            message += f"Step {step}/{total_steps}: Select assets you're interested in\n\n"
            message += "You can change this anytime with /preferences\n\n"
            message += "<b>Popular Choices:</b>"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🇪🇺🇺🇸 EUR/USD", callback_data="asset_EURUSD"),
                 InlineKeyboardButton("🇬🇧🇺🇸 GBP/USD", callback_data="asset_GBPUSD")],
                [InlineKeyboardButton("₿ Bitcoin", callback_data="asset_BTC"),
                 InlineKeyboardButton("🥇 Gold", callback_data="asset_GOLD")],
                [InlineKeyboardButton("📊 S&P 500", callback_data="asset_ES"),
                 InlineKeyboardButton("🚀 NASDAQ", callback_data="asset_NQ")],
                [InlineKeyboardButton("✅ Done Selecting", callback_data="onboard_next"),
                 InlineKeyboardButton("🔙 Back", callback_data="onboard_back")]
            ])

        elif state == ONBOARDING_STATES['RISK']:
            message = "⚠️ <b>Risk Tolerance</b>\n\n"
            message += f"Step {step}/{total_steps}: How much risk are you comfortable with?\n\n"
            message += "This affects signal filtering and position sizing recommendations."

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ Conservative - Lower risk", callback_data="risk_low")],
                [InlineKeyboardButton("⚖️ Moderate - Balanced approach", callback_data="risk_medium")],
                [InlineKeyboardButton("📈 Aggressive - Higher risk/reward", callback_data="risk_high")],
                [InlineKeyboardButton("🔙 Back", callback_data="onboard_back")]
            ])

        elif state == ONBOARDING_STATES['NOTIFICATIONS']:
            message = "🔔 <b>Notification Preferences</b>\n\n"
            message += f"Step {step}/{total_steps}: Choose what notifications you want\n\n"
            message += "You can customize this further with /preferences"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 All Notifications", callback_data="notif_all")],
                [InlineKeyboardButton("🔕 Important Only", callback_data="notif_important")],
                [InlineKeyboardButton("🚫 No Notifications", callback_data="notif_none")],
                [InlineKeyboardButton("🔙 Back", callback_data="onboard_back")]
            ])

        elif state == ONBOARDING_STATES['COMPLETE']:
            flow_data = flow['data']
            assets = flow_data.get('preferred_assets', [])
            asset_names = [asset.split(' - ')[0] if ' - ' in asset else asset for asset in assets[:3]]

            message = "🎉 <b>Setup Complete!</b>\n\n"
            message += "You're all set to start trading with AI-powered signals!\n\n"
            message += "📋 <b>Your Preferences:</b>\n"
            message += f"• Language: {flow_data.get('language', 'en').upper()}\n"
            message += f"• Timezone: {flow_data.get('timezone', 'UTC')}\n"
            message += f"• Risk Level: {flow_data.get('risk_tolerance', 'medium').title()}\n"
            if asset_names:
                message += f"• Favorite Assets: {', '.join(asset_names)}\n"
            message += "\n🚀 <b>Ready to explore:</b>\n"
            message += "• `/allsignals` - Check all markets\n"
            message += "• `/help` - See all commands\n"
            message += "• `/dashboard` - Your personal overview\n\n"
            message += "Happy trading! 📈"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start Trading", callback_data="onboard_finish")]
            ])

        else:
            message = "Unknown onboarding state"
            keyboard = None

        return message, keyboard

    def handle_callback(self, user_id: int, callback_data: str) -> tuple[str, InlineKeyboardMarkup, bool]:
        """
        Handle onboarding callback
        Returns: (message, keyboard, flow_complete)
        """
        if callback_data == "onboard_start":
            self.next_step(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        elif callback_data == "onboard_skip":
            # Skip onboarding and go to main menu
            if user_id in self.active_flows:
                del self.active_flows[user_id]
            return "Setup skipped. Use /help to explore features!", None, True

        elif callback_data == "onboard_back":
            # Go back one step (simplified - just restart for now)
            flow = self.start_flow(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        elif callback_data == "onboard_next":
            self.next_step(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        elif callback_data == "onboard_finish":
            self.complete_flow(user_id)
            return "Welcome to your trading journey! Use /help to get started.", None, True

        # Handle language selection
        elif callback_data.startswith("lang_"):
            lang = callback_data.split("_")[1]
            self.update_flow_data(user_id, 'language', lang)
            self.next_step(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        # Handle timezone selection
        elif callback_data.startswith("tz_"):
            tz = callback_data.split("_")[1]
            self.update_flow_data(user_id, 'timezone', tz)
            self.next_step(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        # Handle experience level
        elif callback_data.startswith("exp_"):
            exp = callback_data.split("_")[1]
            self.update_flow_data(user_id, 'experience_level', exp)
            self.next_step(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        # Handle asset selection
        elif callback_data.startswith("asset_"):
            asset = callback_data.split("_")[1]
            current_assets = self.active_flows[user_id]['data'].get('preferred_assets', [])

            if asset in current_assets:
                current_assets.remove(asset)
            else:
                current_assets.append(asset)

            self.update_flow_data(user_id, 'preferred_assets', current_assets)
            # Stay on same step to allow multiple selections
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        # Handle risk tolerance
        elif callback_data.startswith("risk_"):
            risk = callback_data.split("_")[1]
            self.update_flow_data(user_id, 'risk_tolerance', risk)
            self.next_step(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        # Handle notifications
        elif callback_data.startswith("notif_"):
            notif_type = callback_data.split("_")[1]

            if notif_type == "all":
                self.update_flow_data(user_id, 'notifications_enabled', True)
                self.update_flow_data(user_id, 'price_alerts_enabled', True)
            elif notif_type == "important":
                self.update_flow_data(user_id, 'notifications_enabled', True)
                self.update_flow_data(user_id, 'price_alerts_enabled', False)
            elif notif_type == "none":
                self.update_flow_data(user_id, 'notifications_enabled', False)
                self.update_flow_data(user_id, 'price_alerts_enabled', False)

            self.next_step(user_id)
            message, keyboard = self.get_step_message(user_id)
            return message, keyboard, False

        return "Unknown callback", None, False

# Global onboarding manager instance
onboarding_manager = OnboardingFlow()
