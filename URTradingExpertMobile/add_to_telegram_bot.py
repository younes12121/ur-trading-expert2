"""
Add this code to telegram_bot.py to enable /mobile command
with your GitHub Pages URL
"""

# Add this import at the top if not already there
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Add this function with your other command handlers
async def mobile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open mobile trading dashboard"""
    chat_id = update.effective_chat.id
    
    # Your actual GitHub Pages URL
    mobile_app_url = "https://younes12121.github.io/ur-trading-expert-mobile/mobile_app.html"
    
    keyboard = [[
        InlineKeyboardButton(
            "📱 Open Mobile Dashboard",
            web_app=WebAppInfo(url=mobile_app_url)
        )
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📱 *UR Trading Expert Mobile*\n\n"
        "Access your trading dashboard on any device!\n\n"
        "*Features:*\n"
        "✅ Live trading signals\n"
        "✅ Real-time stats & analytics\n"
        "✅ Win rate tracking\n"
        "✅ Performance metrics\n"
        "✅ Beautiful mobile interface\n\n"
        "_Tap the button below to launch:_",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Add these lines where you register command handlers in main():
# (Look for where you have other application.add_handler() calls)
application.add_handler(CommandHandler("mobile", mobile_command))
application.add_handler(CommandHandler("app", mobile_command))
