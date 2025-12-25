"""
Bot Templates Module
Centralized user-facing messages for consistency and maintainability
"""

from typing import Dict, Any, Optional

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES = {
    'user_not_found': "❌ <b>Error:</b> Could not identify user. Please try again.",
    'permission_denied': "🚫 <b>Access Denied:</b> You don't have permission to use this command.",
    'command_not_found': "❓ <b>Unknown Command:</b> Use /help to see available commands.",
    'service_unavailable': "⚠️ <b>Service Temporarily Unavailable:</b> Please try again in a few minutes.",
    'rate_limit_exceeded': "⏱️ <b>Rate Limit Exceeded:</b> Please wait a moment before trying again.",
    'invalid_input': "❌ <b>Invalid Input:</b> Please check your command format and try again.",
    'network_error': "🌐 <b>Network Error:</b> Unable to connect to servers. Please try again.",
    'api_error': "🔧 <b>API Error:</b> Trading data temporarily unavailable.",
    'database_error': "💾 <b>Database Error:</b> Unable to access user data.",
    'payment_error': "💳 <b>Payment Error:</b> Transaction could not be processed.",
    'subscription_required': "⭐ <b>Premium Feature:</b> Upgrade to access this feature with /subscribe",
    'trial_expired': "⏰ <b>Trial Expired:</b> Your free trial has ended. Upgrade with /subscribe",
    'feature_disabled': "🚫 <b>Feature Disabled:</b> This feature is currently unavailable.",
}

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_MESSAGES = {
    'command_completed': "✅ <b>Success:</b> Command executed successfully.",
    'settings_updated': "✅ <b>Settings Updated:</b> Your preferences have been saved.",
    'subscription_activated': "🎉 <b>Subscription Activated:</b> Welcome to {tier}!",
    'payment_processed': "💳 <b>Payment Successful:</b> Your transaction has been processed.",
    'data_saved': "💾 <b>Data Saved:</b> Your information has been updated.",
    'notification_sent': "🔔 <b>Notification Sent:</b> Check your messages.",
    'signal_generated': "📊 <b>Signal Generated:</b> Analysis complete.",
    'trade_executed': "🚀 <b>Trade Executed:</b> Position opened successfully.",
    'user_registered': "👋 <b>Welcome!</b> Your account has been created.",
    'onboarding_complete': "🎉 <b>Setup Complete!</b> You're ready to start trading.",
}

# ============================================================================
# CONFIRMATION MESSAGES
# ============================================================================

CONFIRMATION_MESSAGES = {
    'trade_confirmation': "⚠️ <b>Confirm Trade:</b>\n\nAsset: {asset}\nAction: {action}\nAmount: {amount}\n\nProceed?",
    'settings_change': "⚙️ <b>Confirm Changes:</b>\n\n{changes}\n\nSave these settings?",
    'subscription_cancel': "❌ <b>Cancel Subscription:</b>\n\nAre you sure you want to cancel your {tier} subscription?",
    'delete_data': "🗑️ <b>Delete Data:</b>\n\nThis will permanently delete your {data_type}. Continue?",
    'reset_settings': "🔄 <b>Reset Settings:</b>\n\nThis will reset all preferences to defaults. Continue?",
}

# ============================================================================
# STATUS MESSAGES
# ============================================================================

STATUS_MESSAGES = {
    'system_online': "✅ <b>System Status:</b> All services operational",
    'system_maintenance': "🔧 <b>Maintenance:</b> System is undergoing maintenance",
    'market_open': "📈 <b>Markets:</b> Most markets are open for trading",
    'market_closed': "📉 <b>Markets:</b> Many markets are closed (weekend/holidays)",
    'high_volatility': "⚠️ <b>Market Alert:</b> High volatility detected",
    'low_liquidity': "💧 <b>Liquidity:</b> Low liquidity conditions",
    'connection_restored': "🔗 <b>Connection:</b> Service connectivity restored",
    'backup_complete': "💾 <b>Backup:</b> Data backup completed successfully",
}

# ============================================================================
# WELCOME & ONBOARDING MESSAGES
# ============================================================================

WELCOME_MESSAGES = {
    'first_time_user': """🤖 <b>WELCOME TO QUANTUM ELITE TRADING BOT</b>

✨ <b>Hello, {name}!</b>

<i>AI-Powered Trading Signals</i>
📊 20-Criteria Analysis | 🎯 16 Assets
🧠 Real-Time AI Insights

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 <b>What makes this special:</b>
• Ultra A+ quality signals
• 95%+ win rate on premium
• Real-time market analysis
• Professional risk management

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 <b>Ready to start?</b> Use /quickstart for a 2-minute setup wizard!""",

    'returning_user': """🤖 <b>WELCOME BACK, {name}!</b>

📊 Your trading dashboard is ready.
Use /dashboard for a personalized overview.

Quick actions:
• /allsignals - Check all markets
• /btc or /gold - Specific signals
• /analytics - Your performance""",

    'new_user_hint': """🆕 <b>NEW USER?</b>
<i>Take our 2-minute setup to personalize your experience!</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🚀 Choose a command category:</b>""",
}

ONBOARDING_MESSAGES = {
    'welcome_step': """🎯 <b>QUICK START WIZARD</b>

✨ <b>Welcome, {name}!</b>

This quick setup will personalize your experience and help you get the most out of AI-powered trading signals.

<i>Only takes 2 minutes!</i>

Ready to begin?""",

    'language_step': """🌐 <b>Choose Your Language</b>

📋 <b>Step 1/6:</b> Select your preferred language

This affects all bot messages and help content.""",

    'timezone_step': """🕐 <b>Set Your Timezone</b>

📋 <b>Step 2/6:</b> Choose your timezone for accurate market timing

This ensures signals are delivered at optimal times.""",

    'experience_step': """📊 <b>Your Trading Experience</b>

📋 <b>Step 3/6:</b> Tell us about your background

This helps us show information at the right complexity level.""",

    'assets_step': """💎 <b>Choose Your Assets</b>

📋 <b>Step 4/6:</b> Select assets you're interested in

You can change this anytime with /preferences

<b>Popular choices:</b>""",

    'risk_step': """⚠️ <b>Risk Tolerance</b>

📋 <b>Step 5/6:</b> How much risk are you comfortable with?

This affects signal filtering and position sizing.""",

    'notifications_step': """🔔 <b>Notification Preferences</b>

📋 <b>Step 6/6:</b> Choose what notifications you want

You can customize this further with /preferences""",

    'complete': """🎉 <b>SETUP COMPLETE!</b>

<b>📋 Your Preferences:</b>
• Language: {language}
• Timezone: {timezone}
• Risk Level: {risk_tolerance}
• Assets: {assets}

<b>🚀 Ready to explore:</b>
• /allsignals - Check all markets
• /help - See all commands
• /dashboard - Your personal overview

<b>Happy trading! 📈</b>""",
}

# ============================================================================
# HELP & GUIDANCE MESSAGES
# ============================================================================

HELP_MESSAGES = {
    'command_not_found': """❓ <b>Command Not Found</b>

The command '{command}' was not recognized.

<b>💡 Try these instead:</b>
• /help - See all available commands
• /search {term} - Smart search for commands
• /dashboard - Your personal overview

<b>🔍 Popular commands:</b>
• /allsignals - Scan all markets
• /btc - Bitcoin signals
• /gold - Gold signals
• /analytics - Performance stats""",

    'search_usage': """🔍 <b>Smart Search</b>

Search for commands, assets, and topics:

<b>📝 Usage:</b>
<code>/search bitcoin</code> - Find Bitcoin commands
<code>/search forex</code> - Find forex trading
<code>/search analytics</code> - Find analysis tools

<b>💡 Examples:</b>
• /search btc → Bitcoin signals
• /search gold → Gold trading
• /search risk → Risk management
• /search learn → Learning resources

<i>Search is fuzzy - try partial words!</i>""",

    'subscription_upgrade': """⭐ <b>UPGRADE TO PREMIUM</b>

Unlock advanced features with a premium subscription:

<b>🚀 Premium Benefits:</b>
• All 15 trading assets (including futures)
• Unlimited signal requests
• Advanced AI predictions
• Portfolio optimization tools
• Priority support

<b>💰 Pricing:</b>
• $29/month - Premium access
• $99/month - VIP (everything + personal support)

<b>🎁 Free Trial:</b> 7 days free!

Use /subscribe to get started!""",
}

# ============================================================================
# TEMPLATE FUNCTIONS
# ============================================================================

def get_error_message(error_type: str, **kwargs) -> str:
    """Get formatted error message"""
    template = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES['service_unavailable'])
    return template.format(**kwargs)

def get_success_message(success_type: str, **kwargs) -> str:
    """Get formatted success message"""
    template = SUCCESS_MESSAGES.get(success_type, SUCCESS_MESSAGES['command_completed'])
    return template.format(**kwargs)

def get_confirmation_message(confirm_type: str, **kwargs) -> str:
    """Get formatted confirmation message"""
    template = CONFIRMATION_MESSAGES.get(confirm_type, "")
    return template.format(**kwargs) if template else ""

def get_status_message(status_type: str, **kwargs) -> str:
    """Get formatted status message"""
    template = STATUS_MESSAGES.get(status_type, "")
    return template.format(**kwargs) if template else ""

def get_welcome_message(welcome_type: str, **kwargs) -> str:
    """Get formatted welcome message"""
    template = WELCOME_MESSAGES.get(welcome_type, "")
    return template.format(**kwargs) if template else ""

def get_onboarding_message(step: str, **kwargs) -> str:
    """Get formatted onboarding message"""
    template = ONBOARDING_MESSAGES.get(step, "")
    return template.format(**kwargs) if template else ""

def get_help_message(help_type: str, **kwargs) -> str:
    """Get formatted help message"""
    template = HELP_MESSAGES.get(help_type, "")
    return template.format(**kwargs) if template else ""

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_asset_list(assets: list, max_items: int = 3) -> str:
    """Format a list of assets for display"""
    if not assets:
        return "None selected"

    display_assets = assets[:max_items]
    result = ", ".join(display_assets)

    if len(assets) > max_items:
        result += f" +{len(assets) - max_items} more"

    return result

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    return f"${amount:,.2f} {currency}"

def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.1f}%"

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    # This would use proper datetime formatting
    return timestamp
