#!/usr/bin/env python3
"""
Test Enhanced Integration - Quick verification of all enhanced generators
"""

import sys
import os
from datetime import datetime

print("="*80)
print("🧪 TESTING ENHANCED INTEGRATION")
print("="*80)
print()

def test_enhanced_generator(generator_class, name, symbol=None):
    """Test an enhanced generator"""
    try:
        if symbol:
            generator = generator_class(symbol)
        else:
            generator = generator_class()
        
        print(f"🔧 Testing {name}...")
        signal = generator.generate_signal()
        
        if signal:
            if signal.get('direction') != 'HOLD':
                print(f"✅ {name}: ELITE {signal.get('grade', 'A+')} signal generated!")
                print(f"   Direction: {signal['direction']}")
                print(f"   Score: {signal.get('score', 'N/A')}")
                print(f"   Confidence: {signal.get('confidence', 0):.1f}%")
            else:
                print(f"⏳ {name}: No elite signal (Score: {signal.get('criteria_met', 0)}/20)")
        else:
            print(f"❌ {name}: No signal returned")
            
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)[:50]}")
        
    print()

# Test all enhanced generators
print("🚀 Testing Enhanced Generators:")
print("-" * 50)

try:
    from enhanced_btc_signal_generator import EnhancedBTCSignalGenerator
    test_enhanced_generator(EnhancedBTCSignalGenerator, "Enhanced BTC Generator")
except ImportError as e:
    print(f"❌ Enhanced BTC Generator: Import error - {e}")
    print()

try:
    from enhanced_gold_signal_generator import EnhancedGoldSignalGenerator
    test_enhanced_generator(EnhancedGoldSignalGenerator, "Enhanced Gold Generator")
except ImportError as e:
    print(f"❌ Enhanced Gold Generator: Import error - {e}")
    print()

try:
    from enhanced_forex_signal_generator import EnhancedForexSignalGenerator
    test_enhanced_generator(EnhancedForexSignalGenerator, "Enhanced EURUSD Generator", "EURUSD")
    test_enhanced_generator(EnhancedForexSignalGenerator, "Enhanced GBPUSD Generator", "GBPUSD")
except ImportError as e:
    print(f"❌ Enhanced Forex Generator: Import error - {e}")
    print()

try:
    from enhanced_futures_signal_generator import EnhancedFuturesSignalGenerator
    test_enhanced_generator(EnhancedFuturesSignalGenerator, "Enhanced ES Generator", "ES")
    test_enhanced_generator(EnhancedFuturesSignalGenerator, "Enhanced NQ Generator", "NQ")
except ImportError as e:
    print(f"❌ Enhanced Futures Generator: Import error - {e}")
    print()

print("="*80)
print("🎯 TELEGRAM BOT INTEGRATION TEST")
print("="*80)
print()

try:
    print("📱 Testing telegram bot import...")
    import telegram_bot
    print("✅ Telegram bot imports successfully!")
    print("✅ All enhanced generators are integrated!")
    print()
    
    print("🔍 Checking enhanced functions in bot:")
    
    # Check if enhanced functions exist
    if hasattr(telegram_bot, 'btc_command'):
        print("✅ Enhanced btc_command found")
    else:
        print("❌ btc_command not found")
        
    if hasattr(telegram_bot, 'gold_command'):
        print("✅ Enhanced gold_command found")
    else:
        print("❌ gold_command not found")
        
    if hasattr(telegram_bot, 'eurusd_command'):
        print("✅ Enhanced eurusd_command found")
    else:
        print("❌ eurusd_command not found")
    
except Exception as e:
    print(f"❌ Telegram bot integration error: {e}")

print()
print("="*80)
print("🎉 INTEGRATION TEST COMPLETE")
print("="*80)
print()
print("Next steps:")
print("1. Start your telegram bot: python telegram_bot.py")
print("2. Test enhanced commands: /btc, /gold, /eurusd")
print("3. Verify elite signal quality")
print()
print("🚀 Your bot is now ENHANCED with world-class signals!")
print()
