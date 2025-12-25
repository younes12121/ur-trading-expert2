#!/usr/bin/env python3
"""
Wrapper script to run the bot with full error capture
"""
import sys
import os
import traceback
from datetime import datetime

# Create log file
log_file = f"bot_startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(message):
    """Log to both console and file"""
    print(message, flush=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

log("="*60)
log("BOT STARTUP WRAPPER")
log("="*60)
log(f"Log file: {log_file}")
log(f"Python: {sys.executable}")
log(f"Python version: {sys.version}")
log("="*60)
log("")

try:
    log("[1] Attempting to import telegram_bot module...")
    import telegram_bot
    log("[✓] Module imported successfully")
    
    log("[2] Checking if main function exists...")
    if hasattr(telegram_bot, 'main'):
        log("[✓] main() function found")
    else:
        log("[✗] main() function not found!")
        sys.exit(1)
    
    log("[3] Calling main() function...")
    log("="*60)
    log("")
    
    # Call main
    telegram_bot.main()
    
    log("")
    log("="*60)
    log("Bot exited normally")
    log("="*60)
    
except KeyboardInterrupt:
    log("")
    log("="*60)
    log("Bot stopped by user (Ctrl+C)")
    log("="*60)
    
except SystemExit as e:
    log("")
    log("="*60)
    log(f"Bot exited with code: {e.code}")
    log("="*60)
    raise
    
except ImportError as e:
    log("")
    log("="*60)
    log(f"[✗] IMPORT ERROR: {e}")
    log("="*60)
    traceback.print_exc()
    log("")
    log("Full traceback saved to log file")
    sys.exit(1)
    
except Exception as e:
    log("")
    log("="*60)
    log(f"[✗] FATAL ERROR: {e}")
    log("="*60)
    log("Full traceback:")
    traceback.print_exc()
    log("")
    log("Full traceback saved to log file")
    sys.exit(1)












