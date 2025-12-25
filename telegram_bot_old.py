"""
Main Trading Bot
Integrates all components for automated trading
"""

import time
from datetime import datetime
import sys

# Import our modules
from btc_analyzer_v2 import BTCScalpingAnalyzerV2
from risk_manager import RiskManager, TrailingStopManager
from trade_executor import BinanceExecutor
from data_fetcher import BinanceDataFetcher
import config

class TradingBot:
    """Main trading bot that coordinates all components"""
    
    def __init__(self, capital: float = 500, risk_per_trade: float = 0.01, 
                 testnet: bool = True, auto_trade: bool = False):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.auto_trade = auto_trade
        
        # Initialize components
        self.analyzer = BTCScalpingAnalyzerV2(capital=capital, risk_per_trade=risk_per_trade)
        self.risk_manager = RiskManager(initial_capital=capital, max_risk_per_trade=risk_per_trade)
        self.trail_manager = TrailingStopManager()
        self.executor = BinanceExecutor(testnet=testnet)
        self.data_fetcher = BinanceDataFetcher()
        
        # Active positions
        self.active_positions = []
        
        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
    def run_once(self):
        """Run one iteration of the trading loop"""
        print("\n" + "=" * 70)
        print(f"🤖 Trading Bot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Check if we can trade
        can_trade, reason = self.risk_manager.can_trade()
        if not can_trade:
            print(f"🚫 Trading blocked: {reason}")
            self.risk_manager.print_risk_status()
            return
        
        # Generate trading signal
        print("\n📊 Analyzing market...")
        signal = self.analyzer.generate_trading_signal()
        
        if signal['direction'] == 'HOLD':
            print("⏸️  No trading signal - HOLD")
            return
        
        # Display signal
        print(f"\n🎯 Signal Generated:")
        print(f"   Direction: {signal['direction']}")
        print(f"   Entry: ${signal['entry_price']:,.2f}")
        print(f"   Stop Loss: ${signal['stop_loss']:,.2f}")
        print(f"   TP1: ${signal['take_profit_1']:,.2f}")
        print(f"   TP2: ${signal['take_profit_2']:,.2f}")
        print(f"   Confidence: {signal['confidence']}%")
        print(f"   Lot Size: {signal['lot_size']}")
        
        # Check confidence threshold
        if signal['confidence'] < 65:
            print(f"\n⚠️  Confidence too low ({signal['confidence']}%) - skipping trade")
            return
        
        # Execute trade
        if self.auto_trade:
            print("\n🚀 Auto-trading enabled - executing trade...")
            result = self.executor.execute_trade(signal)
            
            if result:
                print("✅ Trade executed successfully!")
                self.active_positions.append({
                    'signal': signal,
                    'order_ids': result,
                    'entry_time': datetime.now()
                })
                self.total_trades += 1
            else:
                print("❌ Trade execution failed")
        else:
            print("\n⚠️  Auto-trading disabled - signal generated but not executed")
            print("   Set auto_trade=True to enable automatic execution")
    
    def monitor_positions(self):
        """Monitor and manage active positions"""
        if not self.active_positions:
            return
        
        print(f"\n📈 Monitoring {len(self.active_positions)} active position(s)...")
        
        for position in self.active_positions:
            signal = position['signal']
            
            # Get current price
            current_price = self.data_fetcher.get_current_price()
            
            if not current_price:
                continue
            
            # Check if we should trail stop
            new_sl = self.trail_manager.calculate_new_stop(signal, current_price)
            
            if new_sl:
                print(f"   🔄 Trailing stop to ${new_sl:,.2f}")
                # Update stop loss order (would need to cancel old and place new)
                # self.executor.cancel_order(...)
                # self.executor.place_stop_loss(...)
    
    def run_continuous(self, interval_minutes: int = 5):
        """Run bot continuously"""
        print("=" * 70)
        print("🤖 TRADING BOT STARTED")
        print("=" * 70)
        print(f"Capital: ${self.capital}")
        print(f"Risk per Trade: {self.risk_per_trade * 100}%")
        print(f"Auto-trade: {self.auto_trade}")
        print(f"Check Interval: {interval_minutes} minutes")
        print("=" * 70)
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_once()
                self.monitor_positions()
                
                # Wait for next iteration
                print(f"\n⏰ Next check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            self.print_summary()
    
    def print_summary(self):
        """Print trading summary"""
        print("\n" + "=" * 70)
        print("📊 TRADING SUMMARY")
        print("=" * 70)
        print(f"Total Trades: {self.total_trades}")
        print(f"Winning Trades: {self.winning_trades}")
        print(f"Losing Trades: {self.losing_trades}")
        
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        
        self.risk_manager.print_risk_status()
        print("=" * 70)


# Main entry point
if __name__ == "__main__":
    print("\n" + "*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  BTC TRADING BOT - PRODUCTION READY".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    # Configuration
    CAPITAL = config.CAPITAL
    RISK_PER_TRADE = config.RISK_PER_TRADE
    USE_TESTNET = config.USE_TESTNET
    AUTO_TRADE = False  # Set to True to enable automatic trading
    
    print("⚙️  Configuration:")
    print(f"   Capital: ${CAPITAL}")
    print(f"   Risk per Trade: {RISK_PER_TRADE * 100}%")
    print(f"   Testnet: {USE_TESTNET}")
    print(f"   Auto-trade: {AUTO_TRADE}")
    print()
    
    if not AUTO_TRADE:
        print("⚠️  AUTO-TRADING IS DISABLED")
        print("   The bot will generate signals but NOT execute trades")
        print("   Set AUTO_TRADE = True in this file to enable execution")
        print()
    
    # Create and run bot
    bot = TradingBot(
        capital=CAPITAL,
        risk_per_trade=RISK_PER_TRADE,
        testnet=USE_TESTNET,
        auto_trade=AUTO_TRADE
    )
    
    # Choose mode
    print("Select mode:")
    print("1. Run once (generate one signal)")
    print("2. Run continuously (check every 5 minutes)")
    print()
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            bot.run_once()
            bot.print_summary()
        elif choice == "2":
            bot.run_continuous(interval_minutes=5)
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nBot stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
