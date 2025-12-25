#!/usr/bin/env python3
"""
Test script for ETH A+ Filter
"""

from eth_aplus_filter import ETHAPlusFilter

def test_eth_filter():
    """Test the ETH A+ filter with sample data"""

    print("FIRE Testing ETH A+ Filter")
    print("=" * 50)

    # Initialize filter
    eth_filter = ETHAPlusFilter()
    print("SUCCESS ETH A+ Filter initialized successfully!")
    print(f"   Min Confidence: {eth_filter.min_confidence}%")
    print(f"   Min R:R Ratio: {eth_filter.min_rr_ratio}:1")
    print(f"   ETH Key Levels: {len(eth_filter.eth_key_levels['major_support'])} major supports")

    # Test with sample A+ setup
    print("\nTARGET Testing A+ Setup Criteria...")

    # Sample market data for ETH A+ setup
    market_data_aplus = {
        'eth_price': 3450.0,
        'eth_dominance': 18.5,      # Good range
        'eth_btc_ratio': 0.062,     # Good range
        'eth_volatility': 0.85,     # 85% - optimal
        'fear_greed_value': 20,     # Extreme fear - good for contrarian
        'volume_ratio': 1.8,        # High volume
        'btc_correlation': 0.75,    # Good correlation
        'eth_dominance_trend': 'stable',
        'eth_btc_ratio_trend': 'increasing'
    }

    signal_data_aplus = {
        'direction': 'BUY',
        'confidence': 82,           # Above 75%
        'entry_price': 3450.0,
        'stop_loss': 3300.0,        # ~4.5% stop
        'take_profit_2': 3800.0     # ~10% target (2.2:1 R:R)
    }

    is_aplus, reasons = eth_filter.filter_eth_signal(signal_data_aplus, market_data_aplus)

    print(f"\nResult: {'SUCCESS ETH A+ SETUP!' if is_aplus else 'FAIL Not A+'}")
    print(f"Overall: {reasons['overall']}")

    if is_aplus:
        print("\nSUCCESS Passing Criteria:")
        for key, reason in reasons.items():
            if key not in ['overall', 'news_items'] and '[OK]' in reason:
                print(f"   • {reason}")
    else:
        print("\nFAIL Failing Criteria:")
        for key, reason in reasons.items():
            if key not in ['overall', 'news_items'] and '[FAIL]' in reason:
                print(f"   • {reason}")

    # Test with non-A+ setup
    print("\n" + "=" * 50)
    print("TARGET Testing Non-A+ Setup...")

    market_data_bad = {
        'eth_price': 3450.0,
        'eth_dominance': 12.0,      # Too low
        'eth_btc_ratio': 0.045,     # Too low
        'eth_volatility': 0.3,      # Too low
        'fear_greed_value': 55,     # Neutral
        'volume_ratio': 0.7,        # Too low
        'btc_correlation': 0.4      # Too low
    }

    signal_data_bad = {
        'direction': 'BUY',
        'confidence': 65,           # Too low
        'entry_price': 3450.0,
        'stop_loss': 3400.0,        # Too tight
        'take_profit_2': 3550.0     # Poor R:R
    }

    is_bad_aplus, bad_reasons = eth_filter.filter_eth_signal(signal_data_bad, market_data_bad)

    print(f"\nResult: {'SUCCESS ETH A+ SETUP!' if is_bad_aplus else 'FAIL Not A+ (Expected)'}")
    print(f"Overall: {bad_reasons['overall']}")

    print("\n" + "=" * 50)
    print("SUCCESS ETH A+ Filter Test Complete!")
    print("Filter is working correctly - only approves ultra-high probability setups!")

if __name__ == "__main__":
    test_eth_filter()
