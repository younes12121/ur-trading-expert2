"""
User-Friendly Error Messages
Provides clear, actionable error messages for better UX
"""

from typing import Optional, Dict

class ErrorMessages:
    """Centralized error message management"""
    
    # General errors
    GENERIC_ERROR = (
        "❌ Oops! Something went wrong.\n\n"
        "Our team has been notified. Please try again in a moment.\n"
        "If the problem persists, use /support to contact us."
    )
    
    # Command errors
    COMMAND_NOT_FOUND = (
        "❓ Command not recognized.\n\n"
        "Use /help to see all available commands.\n"
        "Make sure you're using the correct command format."
    )
    
    COMMAND_UNAVAILABLE = (
        "⛔ This command is not available for your subscription tier.\n\n"
        "Upgrade to Premium or VIP to unlock this feature.\n"
        "Use /pricing to see subscription options."
    )
    
    # Permission errors
    PERMISSION_DENIED = (
        "🔒 You don't have permission to use this command.\n\n"
        "This feature requires a Premium or VIP subscription.\n"
        "Use /pricing to upgrade your account."
    )
    
    ADMIN_ONLY = (
        "🔒 This command is only available to administrators.\n\n"
        "If you believe this is an error, contact support using /support."
    )
    
    # Data errors
    DATA_NOT_FOUND = (
        "📭 No data found.\n\n"
        "This might be because:\n"
        "• You haven't generated any signals yet\n"
        "• Your filters are too restrictive\n"
        "• The data hasn't been loaded yet\n\n"
        "Try again in a moment or adjust your filters."
    )
    
    INVALID_INPUT = (
        "⚠️ Invalid input provided.\n\n"
        "Please check your input and try again.\n"
        "Use /help [command] to see the correct format."
    )
    
    # API errors
    API_ERROR = (
        "🌐 Connection error.\n\n"
        "We're having trouble connecting to external services.\n"
        "Please try again in a few moments."
    )
    
    RATE_LIMIT_EXCEEDED = (
        "⏱️ Rate limit exceeded.\n\n"
        "You've made too many requests. Please wait a moment before trying again.\n"
        "Free tier: 10 requests/hour\n"
        "Premium: 100 requests/hour\n"
        "VIP: Unlimited"
    )
    
    # Trading errors
    INVALID_ASSET = (
        "❌ Invalid asset specified.\n\n"
        "Available assets:\n"
        "• Crypto: BTC\n"
        "• Commodities: Gold\n"
        "• Forex: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD, EURJPY, EURGBP, GBPJPY, AUDJPY, USDCHF\n"
        "• Futures: ES, NQ\n\n"
        "Use /help to see all available commands."
    )
    
    SIGNAL_GENERATION_FAILED = (
        "⚠️ Unable to generate signal at this time.\n\n"
        "This could be due to:\n"
        "• Market data temporarily unavailable\n"
        "• Insufficient market data for analysis\n"
        "• Market is closed\n\n"
        "Please try again in a few minutes."
    )
    
    # Subscription errors
    SUBSCRIPTION_EXPIRED = (
        "💳 Your subscription has expired.\n\n"
        "Renew your subscription to continue using premium features.\n"
        "Use /pricing to see subscription options and /subscribe to renew."
    )
    
    PAYMENT_FAILED = (
        "💳 Payment processing failed.\n\n"
        "This could be due to:\n"
        "• Insufficient funds\n"
        "• Card declined\n"
        "• Payment system temporarily unavailable\n\n"
        "Please check your payment method and try again.\n"
        "Contact support if the problem persists: /support"
    )
    
    # Database errors
    DATABASE_ERROR = (
        "💾 Database connection error.\n\n"
        "We're experiencing technical difficulties.\n"
        "Your data is safe. Please try again in a moment.\n"
        "If this persists, contact support: /support"
    )
    
    # File errors
    FILE_NOT_FOUND = (
        "📁 File not found.\n\n"
        "The requested file doesn't exist or has been moved.\n"
        "Please check your request and try again."
    )
    
    # Validation errors
    INVALID_USER_ID = (
        "⚠️ Invalid user ID.\n\n"
        "Please provide a valid Telegram user ID."
    )
    
    INVALID_AMOUNT = (
        "⚠️ Invalid amount specified.\n\n"
        "Please provide a valid number greater than 0."
    )
    
    # Feature-specific errors
    BROKER_NOT_CONNECTED = (
        "🔌 Broker not connected.\n\n"
        "To use broker integration:\n"
        "1. Use /connect_broker to set up your broker\n"
        "2. Ensure you have a VIP subscription\n"
        "3. Follow the setup instructions\n\n"
        "Use /help broker for more information."
    )
    
    COPY_TRADING_NOT_AVAILABLE = (
        "👥 Copy trading is not available.\n\n"
        "This feature requires:\n"
        "• VIP subscription\n"
        "• Active traders to follow\n\n"
        "Use /pricing to upgrade or /help copy_trading for more info."
    )
    
    # Success messages (for context)
    @staticmethod
    def success_message(action: str, details: Optional[str] = None) -> str:
        """Generate success message"""
        base = f"✅ {action} successful!"
        if details:
            base += f"\n\n{details}"
        return base
    
    # Helpful suggestions
    @staticmethod
    def get_suggestion(error_type: str) -> str:
        """Get helpful suggestion based on error type"""
        suggestions = {
            'command': "Use /help to see all available commands.",
            'permission': "Upgrade your subscription at /pricing",
            'data': "Try again in a moment or use /help for guidance.",
            'api': "Check your internet connection and try again.",
            'payment': "Contact support at /support if the issue persists."
        }
        return suggestions.get(error_type, "Use /help for assistance.")


def format_error(error: Exception, error_type: str = "generic", 
                context: Optional[Dict] = None) -> str:
    """Format error for user display"""
    error_messages = ErrorMessages()
    
    # Map error types to messages
    error_map = {
        'command_not_found': error_messages.COMMAND_NOT_FOUND,
        'permission_denied': error_messages.PERMISSION_DENIED,
        'subscription_expired': error_messages.SUBSCRIPTION_EXPIRED,
        'rate_limit': error_messages.RATE_LIMIT_EXCEEDED,
        'api_error': error_messages.API_ERROR,
        'database_error': error_messages.DATABASE_ERROR,
        'invalid_input': error_messages.INVALID_INPUT,
        'data_not_found': error_messages.DATA_NOT_FOUND,
    }
    
    message = error_map.get(error_type, error_messages.GENERIC_ERROR)
    
    # Add context if available
    if context:
        if 'command' in context:
            message += f"\n\nCommand: {context['command']}"
        if 'user_tier' in context:
            message += f"\nYour tier: {context['user_tier']}"
    
    return message


def get_user_friendly_error(error: Exception) -> str:
    """Convert exception to user-friendly message"""
    error_name = type(error).__name__
    
    # Map common exceptions
    exception_map = {
        'KeyError': ErrorMessages.INVALID_INPUT,
        'ValueError': ErrorMessages.INVALID_INPUT,
        'TypeError': ErrorMessages.INVALID_INPUT,
        'FileNotFoundError': ErrorMessages.FILE_NOT_FOUND,
        'PermissionError': ErrorMessages.PERMISSION_DENIED,
        'ConnectionError': ErrorMessages.API_ERROR,
        'TimeoutError': ErrorMessages.API_ERROR,
    }
    
    return exception_map.get(error_name, ErrorMessages.GENERIC_ERROR)

