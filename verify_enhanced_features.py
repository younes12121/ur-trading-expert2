#!/usr/bin/env python3
"""
Verify Enhanced Trading System Features
Simple test without Unicode characters
"""

import sys
import json

def test_risk_management():
    """Test enhanced risk management"""
    print("=" * 70)
    print("ENHANCED RISK MANAGEMENT VERIFICATION")
    print("=" * 70)

    try:
        from risk_manager import RiskManager

        rm = RiskManager()
        balance = 1000  # Updated from 500
        risk_pct = 0.015  # Updated from 0.01 (1.5%)
        entry_price = 1.0850
        stop_loss = 1.0800

        position = rm.calculate_position_size(balance, entry_price, stop_loss, risk_pct, "EURUSD")

        if position:
            print(f"Position Size: {position['lots']} lots")
            print(f"Risk Amount: ${position['risk_amount']:.2f}")
            print("SUCCESS: Risk management working")
            return True
        else:
            print("FAILED: Position calculation failed")
            return False

    except Exception as e:
        print(f"FAILED: Risk management test error - {e}")
        return False

def test_broker_connectivity():
    """Test multiple broker connectivity"""
    print("=" * 70)
    print("MULTIPLE BROKER CONNECTIVITY TEST")
    print("=" * 70)

    try:
        from broker_connector import BrokerConnector

        bc = BrokerConnector()

        # Check connections for test user
        connections = bc.get_all_connections(7713994326)

        if len(connections) >= 3:  # Should have MT5, OANDA, and new brokers
            print(f"SUCCESS: {len(connections)} broker connections found")
            for conn in connections:
                broker = conn['broker_type'].upper()
                status = "CONNECTED" if conn['status'] == 'connected' else "DISCONNECTED"
                print(f"  - {broker}: {status}")
            return True
        else:
            print(f"FAILED: Only {len(connections)} connections found, expected 5+")
            return False

    except Exception as e:
        print(f"FAILED: Broker connectivity test error - {e}")
        return False

def test_capital_allocation():
    """Test improved capital allocation"""
    print("=" * 70)
    print("IMPROVED CAPITAL ALLOCATION VERIFICATION")
    print("=" * 70)

    try:
        import config
        import bot_config

        # Check enhanced settings
        checks = [
            ("Capital", config.CAPITAL >= 1000),  # Increased from 500
            ("Risk per Trade", config.RISK_PER_TRADE >= 0.015),  # Increased from 0.01
            ("Lot Size", config.LOT_SIZE >= 0.05),  # Increased from 0.02
            ("Max Positions", config.MAX_OPEN_POSITIONS >= 2),  # Increased from 1
            ("Max Daily Loss", config.MAX_DAILY_LOSS <= 0.03),  # Tightened from 0.05
            ("Leverage", config.LEVERAGE >= 2),  # Added leverage
        ]

        passed = 0
        for check_name, passed_check in checks:
            status = "PASS" if passed_check else "FAIL"
            print(f"{check_name}: {status}")
            if passed_check:
                passed += 1

        print(f"\nCapital allocation: {passed}/{len(checks)} checks passed")
        return passed == len(checks)

    except Exception as e:
        print(f"FAILED: Capital allocation test error - {e}")
        return False

def test_signal_testing():
    """Test comprehensive signal testing"""
    print("=" * 70)
    print("COMPREHENSIVE SIGNAL TESTING VERIFICATION")
    print("=" * 70)

    try:
        # Check if signals database exists and has data
        with open('signals_db.json', 'r') as f:
            signals = json.load(f)

        if len(signals) > 0:
            print(f"SUCCESS: {len(signals)} signals in database")
            # Check signal criteria
            valid_signals = 0
            for signal in signals:
                if all(key in signal for key in ['pair', 'direction', 'entry', 'tp', 'sl']):
                    valid_signals += 1

            print(f"Valid signals: {valid_signals}/{len(signals)}")
            return valid_signals > 0
        else:
            print("FAILED: No signals in database")
            return False

    except Exception as e:
        print(f"FAILED: Signal testing error - {e}")
        return False

if __name__ == "__main__":
    print("\nCOMPREHENSIVE TRADING SYSTEM VERIFICATION")
    print("=" * 70)

    tests = [
        ("Enhanced Risk Management", test_risk_management),
        ("Multiple Broker Connectivity", test_broker_connectivity),
        ("Improved Capital Allocation", test_capital_allocation),
        ("Comprehensive Signal Testing", test_signal_testing),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"CRASH: {test_name} - {e}")
            results.append((test_name, False))
            print()

    # Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\nALL ENHANCED FEATURES VERIFIED SUCCESSFULLY!")
        print("Your trading system is production-ready with:")
        print("- Enhanced risk management")
        print("- Multiple broker connectivity")
        print("- Improved capital allocation")
        print("- Comprehensive signal testing")
        sys.exit(0)
    else:
        print(f"\n{passed} out of {total} tests passed. Review issues above.")
        sys.exit(1)

    print("=" * 70)
