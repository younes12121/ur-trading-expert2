"""
Add this to telegram_bot.py to enable /dashboard command with real user data
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open personal trading dashboard with user's real data"""
    chat_id = update.effective_chat.id
    telegram_id = update.effective_user.id
    
    # URL to personal dashboard with user-specific data
    # Make sure personal_dashboard_api.py is running on this URL
    dashboard_url = f"http://localhost:5001/dashboard/{telegram_id}"
    
    keyboard = [[
        InlineKeyboardButton(
            "📊 Open My Dashboard",
            web_app=WebAppInfo(url=dashboard_url)
        )
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 *Personal Trading Dashboard*\n\n"
        "Your comprehensive trading dashboard with:\n\n"
        "*Portfolio:*\n"
        "✅ Real-time balance & P/L\n"
        "✅ Active positions tracking\n"
        "✅ Performance metrics\n\n"
        "*Live Data:*\n"
        "✅ Current open positions\n"
        "✅ Trading signals\n"
        "✅ Complete trade history\n"
        "✅ AI insights & market analysis\n\n"
        "*Features:*\n"
        "✅ Auto-refresh every 30s\n"
        "✅ Export trading records\n"
        "✅ Advanced filtering\n"
        "✅ Performance charts\n\n"
        "_Click below to open your dashboard:_",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Add this where you register command handlers:
application.add_handler(CommandHandler("dashboard", dashboard_command))
application.add_handler(CommandHandler("stats", dashboard_command))
