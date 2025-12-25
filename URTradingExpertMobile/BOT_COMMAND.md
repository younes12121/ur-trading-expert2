# Telegram Bot Command for Mobile App

Add this code to your telegram_bot.py to enable /mobile command:

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

async def mobile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open mobile trading dashboard"""
    chat_id = update.effective_chat.id
    
    # REPLACE THIS URL with your GitHub Pages URL after deployment
    mobile_app_url = "https://YOUR_USERNAME.github.io/ur-trading-expert-mobile/mobile_app.html"
    
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

# Add this line where you register other command handlers in main():
application.add_handler(CommandHandler("mobile", mobile_command))
application.add_handler(CommandHandler("app", mobile_command))
```

## Where to Add This

Find the section in telegram_bot.py where you have other command handlers, around where you see:

```python
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
# Add your new lines here:
application.add_handler(CommandHandler("mobile", mobile_command))
application.add_handler(CommandHandler("app", mobile_command))
```

## After Adding

1. Save telegram_bot.py
2. Restart your bot
3. Send `/mobile` in Telegram
4. Click the button - mobile app opens!
