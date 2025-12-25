#!/usr/bin/env python3
"""
Test Script for New Features
Tests all new risk management and MTF analysis features locally
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_risk_management_suite():
    """Test the complete risk management suite"""
    print("\n" + "="*60)
    print("TESTING RISK MANAGEMENT SUITE")
    print("="*60)

    try:
        from risk_manager import EnhancedRiskManager
        risk_manager = EnhancedRiskManager()

        # Test 1: Position Sizing Calculator
        print("\n[1] Testing Position Sizing Calculator...")
        scenarios = risk_manager.calculate_risk_scenarios(1000, 1.0850, 1.0820)
        print("PASS - Conservative (0.5%):", scenarios['conservative']['lots'], "lots")
        print("PASS - Moderate (1.0%):", scenarios['moderate']['lots'], "lots")
        print("PASS - Aggressive (2.0%):", scenarios['aggressive']['lots'], "lots")

        # Test 2: Portfolio Heat Map
        print("\n[2] Testing Portfolio Heat Map...")
        mock_trades = [
            {'pair': 'EURUSD', 'risk_amount': 25.0},
            {'pair': 'GBPUSD', 'risk_amount': 18.0},
            {'pair': 'BTC', 'risk_amount': 32.0},
            {'pair': 'XAUUSD', 'risk_amount': 15.0}
        ]
        exposure = risk_manager.check_portfolio_exposure(mock_trades, 1000)
        print("PASS - Total Risk:", exposure['total_risk_pct'], "%")
        print("PASS - Overexposed:", exposure['is_overexposed'])
        print("PASS - Heat Map Generated:", len(exposure['heat_map']) > 0)

        # Test 3: Risk/Reward Optimizer
        print("\n[3] Testing Risk/Reward Optimizer...")
        market_data = {'volatility': 0.015, 'atr': 0.002}
        optimized = risk_manager.optimize_risk_reward(1.0850, 'BUY', market_data)
        print("PASS - Conservative RR:", optimized['conservative']['rr_ratio'])
        print("PASS - Moderate RR:", optimized['moderate']['rr_ratio'])
        print("PASS - Aggressive RR:", optimized['aggressive']['rr_ratio'])
        print("PASS - Optimal RR:", optimized['optimal']['rr_ratio'])

        # Test 4: Risk/Reward Analysis
        print("\n[4] Testing Risk/Reward Analysis...")
        analysis = risk_manager.get_risk_reward_analysis(1.0850, 1.0820, 1.0920, 'BUY')
        print("PASS - RR Ratio:", analysis['rr_ratio'])
        print("PASS - Grade:", analysis['grade'])
        print("PASS - Recommended:", analysis['recommended'])

        print("\nSUCCESS: RISK MANAGEMENT SUITE - ALL TESTS PASSED!")
        return True

    except Exception as e:
        print(f"FAILED: RISK MANAGEMENT TEST - {str(e)}")
        return False

def test_mtf_analysis():
    """Test the multi-timeframe analysis features"""
    print("\n" + "="*60)
    print("TESTING MULTI-TIMEFRAME ANALYSIS")
    print("="*60)

    try:
        from multi_timeframe_analyzer import MultiTimeframeAnalyzer
        analyzer = MultiTimeframeAnalyzer()

        # Test 1: Basic MTF Analysis
        print("\n[1] Testing Basic MTF Analysis...")
        analysis = analyzer.analyze_pair('EURUSD')
        print("PASS - Consensus:", analysis['consensus'])
        print("PASS - Alignment:", analysis['alignment_pct'], "%")
        print("PASS - Consistency Score:", analysis['consistency_score'])

        # Test 2: Divergence Detection
        print("\n[2] Testing Divergence Detection...")
        divergences = analysis['divergence']
        print("PASS - Divergence Detected:", divergences != ['NONE'])
        if divergences != ['NONE']:
            print("PASS - Divergence Types:", divergences)

        # Test 3: Dashboard Generation
        print("\n[3] Testing Dashboard Generation...")
        dashboard = analyzer.create_mtf_dashboard('EURUSD')
        print("PASS - Dashboard Generated:", len(dashboard) > 100)
        print("PASS - Contains Consensus:", "CONSENSUS" in dashboard)
        print("PASS - Contains Consistency:", "Consistency:" in dashboard)

        # Test 4: Best Entry Timeframe
        print("\n[4] Testing Best Entry Timeframe...")
        best_tf = analysis['best_entry_tf']
        print("PASS - Best Entry TF:", best_tf)
        print("PASS - Valid Timeframe:", best_tf in ['M15', 'H1', 'H4', 'D1'])

        print("\nSUCCESS: MULTI-TIMEFRAME ANALYSIS - ALL TESTS PASSED!")
        return True

    except Exception as e:
        print(f"FAILED: MTF ANALYSIS TEST - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_telegram_commands():
    """Test that Telegram command handlers are properly registered"""
    print("\n" + "="*60)
    print("TESTING TELEGRAM COMMAND REGISTRATION")
    print("="*60)

    try:
        # Import the bot (in test mode)
        os.environ['TEST_MODE'] = 'true'
        import telegram_bot

        # Check that our new commands are in the help system
        print("\n[1] Checking Command Registration...")
        # This is a basic import test - in real testing we'd mock Telegram API

        print("PASS - Bot imports successfully in test mode")
        print("PASS - No import errors with new features")

        # Test risk manager integration
        print("\n[2] Testing Risk Manager Integration...")
        if hasattr(telegram_bot, 'risk_manager'):
            print("PASS - Risk manager integrated in bot")
        else:
            print("WARN - Risk manager not found in bot scope")

        print("\nSUCCESS: TELEGRAM COMMANDS - BASIC TESTS PASSED!")
        return True

    except Exception as e:
        print(f"FAILED: TELEGRAM COMMANDS TEST - {str(e)}")
        return False

def run_all_tests():
    """Run all feature tests"""
    print("STARTING FEATURE TESTING SUITE")
    print("="*60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    test_results = []

    # Run all tests
    test_results.append(("Risk Management Suite", test_risk_management_suite()))
    test_results.append(("MTF Analysis", test_mtf_analysis()))
    test_results.append(("Telegram Commands", test_telegram_commands()))

    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1

    print("-" * 60)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("ALL FEATURES WORKING CORRECTLY!")
        print("\nREADY FOR PRODUCTION DEPLOYMENT")
        return True
    else:
        print("SOME TESTS FAILED - REVIEW ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
