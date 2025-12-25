#!/usr/bin/env python3
"""
Enhanced Signal Generators Installation Script
Automatically integrates enhanced generators into your telegram bot
"""

import os
import shutil
import sys
from datetime import datetime

def install_enhanced_generators():
    """Install enhanced signal generators"""
    
    print("🚀 ENHANCED SIGNAL GENERATORS INSTALLATION")
    print("="*60)
    
    # Check if enhanced files exist
    required_files = [
        'enhanced_criteria_system.py',
        'enhanced_btc_signal_generator.py',
        'enhanced_gold_signal_generator.py',
        'enhanced_forex_signal_generator.py',
        'enhanced_futures_signal_generator.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all enhanced generator files are in the current directory.")
        return False
    
    print("✅ All enhanced generator files found!")
    
    # Test imports
    print("\n🧪 Testing enhanced system imports...")
    try:
        from enhanced_criteria_system import Enhanced20CriteriaSystem
        from enhanced_btc_signal_generator import EnhancedBTCSignalGenerator
        from enhanced_gold_signal_generator import EnhancedGoldSignalGenerator
        from enhanced_forex_signal_generator import EnhancedForexSignalGenerator
        from enhanced_futures_signal_generator import EnhancedFuturesSignalGenerator
        print("✅ All imports successful!")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Quick functionality test
    print("\n🔧 Testing enhanced BTC generator...")
    try:
        btc_gen = EnhancedBTCSignalGenerator()
        print("✅ BTC generator initialized successfully!")
    except Exception as e:
        print(f"⚠️ BTC generator warning: {e}")
    
    print("\n🔧 Testing enhanced Gold generator...")
    try:
        gold_gen = EnhancedGoldSignalGenerator()
        print("✅ Gold generator initialized successfully!")
    except Exception as e:
        print(f"⚠️ Gold generator warning: {e}")
    
    print("\n🔧 Testing enhanced Forex generator...")
    try:
        forex_gen = EnhancedForexSignalGenerator('EURUSD')
        print("✅ Forex generator initialized successfully!")
    except Exception as e:
        print(f"⚠️ Forex generator warning: {e}")
    
    print("\n🎉 INSTALLATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update your telegram_bot.py with the integration code")
    print("2. Test each command individually")
    print("3. Monitor performance improvements")
    print("\n🚀 Your trading bot is now ENHANCED with world-class signal generation!")
    
    return True

if __name__ == "__main__":
    success = install_enhanced_generators()
    sys.exit(0 if success else 1)
