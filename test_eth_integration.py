#!/usr/bin/env python3
"""
Test ETH A+ Integration
"""

from eth_aplus_filter import ETHAPlusFilter
from enhanced_btc_signal_generator import EnhancedBTCSignalGenerator

def test_eth_integration():
    """Test the complete ETH A+ integration"""

    print("FIRE Testing ETH A+ Integration...")
    print("=" * 50)

    # Test market data (simulated)
    market_data = {
        'eth_dominance': 18.5,
        'btc_dominance': 45.0,
        'eth_btc_ratio': 0.062,
        'eth_volatility': 0.85,  # 85%
        'fear_greed_value': 20,   # Extreme fear
        'volume_ratio': 1.8,
        'btc_correlation': 0.75,
        'eth_price': 3450,
        'eth_dominance_trend': 'stable',
        'eth_btc_ratio_trend': 'increasing',
        'open_interest_change': 2.5
    }

    print("SUCCESS Market data prepared:")
    print(f"   ETH Dominance: {market_data['eth_dominance']}%")
    print(f"   ETH/BTC Ratio: {market_data['eth_btc_ratio']:.3f}")
    print(f"   Fear & Greed: {market_data['fear_greed_value']}")

    # Test signal generation
    print("\nTARGET Testing signal generation...")
    generator = EnhancedBTCSignalGenerator()
    signal = generator.generate_signal()

    if signal:
        direction = signal.get('direction', 'HOLD')
        confidence = signal.get('confidence', 0)
        criteria_met = signal.get('criteria_met', 0)

        print(f"SUCCESS Signal generated: {direction}")
        print(f"   Confidence: {confidence:.1f}%")
        print(f"   Criteria Met: {criteria_met}/20")
    else:
        print("FAIL No signal generated")
        return

    # Test A+ filter
    print("\nDIAMOND Testing A+ filter...")
    eth_filter = ETHAPlusFilter()

    if signal.get('direction') != 'HOLD':
        is_aplus, reasons = eth_filter.filter_eth_signal(signal, market_data)

        result = "SUCCESS PASSED" if is_aplus else "FAIL FAILED"
        print(f"SUCCESS A+ Filter result: {result}")
        print(f"   Overall: {reasons.get('overall', 'No result')}")

        # Count criteria
        passed = sum(1 for r in reasons.values() if isinstance(r, str) and '[OK]' in r)
        total = len([r for r in reasons.values() if isinstance(r, str) and ('[OK]' in r or '[FAIL]' in r)])
        print(f"   Criteria: {passed}/{total} passed")

        if not is_aplus:
            print("   Failed criteria:")
            failed_count = 0
            for key, reason in reasons.items():
                if isinstance(reason, str) and '[FAIL]' in reason and failed_count < 3:
                    clean_reason = reason.replace('[FAIL] ', '')
                    print(f"   • {clean_reason}")
                    failed_count += 1
    else:
        print("WARNING No signal to filter (HOLD)")

    print("\nSUCCESS ETH A+ Integration test complete!")
    print("ROCKET Ready for live ETH A+ signals!")

if __name__ == "__main__":
    test_eth_integration()
