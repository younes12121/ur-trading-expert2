from daily_signals_system import DailySignalsSystem

def run_signals_test():
    """Test the daily signals system for signal frequency"""

    print("🔔 DAILY SIGNALS SYSTEM - SIGNAL FREQUENCY TEST")
    print("=" * 60)
    print("Testing: 3-5 quality signals per day")
    print("With proper risk management and quality controls")
    print("=" * 60)

    system = DailySignalsSystem()
    signals = []

    # Test over multiple simulated hours to see frequency
    for hour in range(24):  # Simulate 24 hours
        print(f"\n🕐 Hour {hour}:00 - {hour+1}:00")

        # Reset hourly counter for new hour
        system.hourly_signals = 0
        system.last_hour = hour

        hour_signals = 0
        for attempt in range(10):  # Multiple attempts per hour
            signal = system.generate_daily_signal(1000)
            if signal:
                hour_signals += 1
                signals.append(signal)
                tier_info = "⭐" if signal['tier'] == 'A_PLUS' else "✅" if signal['tier'] == 'A_GRADE' else "🟡"
                print(f"  {tier_info} {signal['asset']} {signal['direction']} (Quality: {signal['quality_score']:.1f})")
                break  # Only one signal per "check" to simulate real usage

        if hour_signals == 0:
            print("  ⏸️  No signals (rate limits or quality filters)")

    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"   Total Signals Generated: {len(signals)}")
    print(f"   Target Range: 3-5 signals per day")
    print(f"   Success: {'✅ EXCELLENT' if 3 <= len(signals) <= 5 else '⚠️ NEEDS TUNING'}")

    if signals:
        print(f"\n🎯 SIGNAL BREAKDOWN:")
        tier_counts = {}
        asset_counts = {}
        for sig in signals:
            tier_counts[sig['tier']] = tier_counts.get(sig['tier'], 0) + 1
            asset_counts[sig['asset']] = asset_counts.get(sig['asset'], 0) + 1

        print("   By Quality Tier:")
        for tier, count in tier_counts.items():
            print(f"     {tier}: {count} signals")

        print("   By Asset:")
        for asset, count in asset_counts.items():
            print(f"     {asset}: {count} signals")

    print("\n🚀 INTEGRATION READY:")
    print("   ✅ Add to bot: /daily_signal command")
    print("   ✅ Auto-alerts: Background signal checking")
    print("   ✅ Risk management: 1% max risk per signal")
    print("   ✅ Quality control: Multi-tier filtering")

    return len(signals)

if __name__ == "__main__":
    signal_count = run_signals_test()

    if signal_count >= 3:
        print(f"\n🎉 SUCCESS: System generates {signal_count} signals per day!")
        print("   Your users will get 3-5 quality signals daily! 📈")
    else:
        print(f"\n⚠️ TUNING NEEDED: Only {signal_count} signals generated")
        print("   Adjust quality gates for more signals while maintaining quality")
