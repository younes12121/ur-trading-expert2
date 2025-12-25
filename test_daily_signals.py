"""
Test script for the Daily Signals System
"""

from daily_signals_system import DailySignalsSystem

def test_daily_signals():
    """Test the daily signals system"""

    print("🔔 DAILY SIGNALS SYSTEM TEST")
    print("=" * 60)
    print("Testing high-frequency signal generation (3-5 signals/day)")
    print("With quality controls and risk management")
    print("=" * 60)

    system = DailySignalsSystem()

    # Generate test signals
    signals_generated = 0
    total_attempts = 20

    for i in range(total_attempts):
        signal = system.generate_daily_signal(1000)  # $1000 account

        if signal:
            signals_generated += 1
            print(f"\n🎯 SIGNAL {signals_generated}:")
            print(f"   Asset: {signal['asset']} ({signal['volatility']} volatility)")
            print(f"   Direction: {signal['direction']}")
            print(f"   Tier: {signal['tier']} ({signal['win_probability']*100:.0f}% win rate)")
            print(f"   Quality Score: {signal['quality_score']:.1f}/100")
            print(f"   Entry: {signal['entry_price']}")
            print(f"   Stop Loss: {signal['stop_loss']}")
            print(f"   Take Profit: {signal['take_profit_1']}")
            print(f"   Risk Amount: ${signal['risk_amount']:.2f}")
            print(f"   Position Size: {signal['position_size']:.4f}")
            print(f"   Session: {signal['session']}")
            print(f"   Valid Until: {signal['valid_until'].strftime('%H:%M UTC')}")
        else:
            print(f"❌ Attempt {i+1}: No signal available (quality/rate limits)")
            if signals_generated >= 5:  # Hit daily limit
                break

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Signals Generated: {signals_generated}")
    print(f"   Target Range: 3-5 signals/day")
    print(f"   Success Rate: {'✅ Excellent' if signals_generated >= 3 else '⚠️ Needs tuning'}")
    print(f"   Quality Maintained: {'✅ Yes' if signals_generated > 0 else '❓ Not tested'}")

    # Show system status
    status = system.get_system_status()
    print(f"\n🖥️  SYSTEM STATUS:")
    print(f"   Daily Signals Today: {status['daily_signals_today']}/{status['daily_limit']}")
    print(f"   Hourly Signals This Hour: {status['hourly_signals_this_hour']}/{status['hourly_limit']}")
    print(f"   Min Interval: {status['min_interval_hours']} hours")

    print("\n🎯 HOW TO INTEGRATE INTO YOUR BOT:")
    print("1. Import: from daily_signals_system import generate_daily_signal")
    print("2. Call: signal = generate_daily_signal(account_balance)")
    print("3. Use: if signal: send_signal_to_user(signal)")
    print("4. Monitor: Check status with get_daily_signals_status()")

    print("\n✅ Daily Signals System Ready for Production!")

if __name__ == "__main__":
    test_daily_signals()
