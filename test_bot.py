"""
Simple Telegram Bot Test
Tests if the bot can connect and respond to commands
"""

from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
import asyncio

# Bot token
BOT_TOKEN = "8437677554:AAHUZJf0R1gYHdsAvVEm3u5pOJq50CHXTiY"

print("=" * 60)
print("TELEGRAM BOT TEST")
print("=" * 60)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    print(f"[RECEIVED] /start from {update.effective_user.first_name}")
    await update.message.reply_text("[OK] Bot is working! Connection successful!")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /test command"""
    print(f"[RECEIVED] /test from {update.effective_user.first_name}")
    await update.message.reply_text("[SUCCESS] Test successful! Bot is responding!")

async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any message"""
    print(f"[RECEIVED] Message: {update.message.text}")
    await update.message.reply_text(f"I received: {update.message.text}")

def main():
    """Start the bot"""
    print("\n[1] Creating application...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    print("[2] Adding handlers...")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, any_message))
    
    print("[3] Starting bot...")
    print("\n[OK] BOT IS NOW RUNNING!")
    print("=" * 60)
    print("Try these commands on Telegram:")
    print("  /start")
    print("  /test")
    print("=" * 60)
    print("\nWaiting for messages...\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
