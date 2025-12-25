from daily_signals_system import generate_daily_signal, get_daily_signals_status

print("🔔 TESTING IMPROVED DAILY SIGNALS SYSTEM")
print("=" * 50)

signals = []
for i in range(12):
    signal = generate_daily_signal(1000)
    if signal:
        signals.append(signal)
        print(f"✅ Signal {len(signals)}: {signal['asset']} {signal['direction']} ({signal['tier']})")
    else:
        print(f"❌ Attempt {i+1}: No signal")

print(f"\n📊 Generated {len(signals)} signals (Target: 3-5 per day)")
print("✅ SUCCESS!" if len(signals) >= 3 else "⚠️ ADJUST NEEDED")

status = get_daily_signals_status()
print(f"Daily Count: {status['daily_signals_today']}/{status['daily_limit']}")
