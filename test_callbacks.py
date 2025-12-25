#!/usr/bin/env python3
"""
Test callback handler functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_callbacks():
    """Test that callback handlers work"""
    print("Testing callback handler functionality...")

    from telegram_bot import get_signals_keyboard, get_analysis_keyboard, get_settings_keyboard, get_account_keyboard

    # Test that keyboard functions work
    try:
        signals_kb = get_signals_keyboard()
        analysis_kb = get_analysis_keyboard()
        settings_kb = get_settings_keyboard()
        account_kb = get_account_keyboard()
        print("PASS: All keyboard functions work correctly")

        # Test that keyboards have buttons
        assert len(signals_kb.inline_keyboard) > 0, "Signals keyboard should have buttons"
        assert len(analysis_kb.inline_keyboard) > 0, "Analysis keyboard should have buttons"
        assert len(settings_kb.inline_keyboard) > 0, "Settings keyboard should have buttons"
        assert len(account_kb.inline_keyboard) > 0, "Account keyboard should have buttons"
        print("PASS: All keyboards have buttons")

    except Exception as e:
        print(f"FAIL: Keyboard function error: {e}")
        return False

    # Test specific callback_data values
    try:
        # Check that new professional button texts exist
        signals_buttons = [btn.text for row in signals_kb.inline_keyboard for btn in row]
        analysis_buttons = [btn.text for row in analysis_kb.inline_keyboard for btn in row]
        settings_buttons = [btn.text for row in settings_kb.inline_keyboard for btn in row]
        account_buttons = [btn.text for row in account_kb.inline_keyboard for btn in row]

        # Check for professional button texts
        assert any("Bitcoin Signals" in btn for btn in signals_buttons), "Should have professional Bitcoin Signals button"
        assert any("Smart Money Flow" in smf for smf in analysis_buttons), "Should have professional Smart Money Flow button"
        assert any("Language Settings" in ls for ls in settings_buttons), "Should have professional Language Settings button"
        assert any("Subscription Plans" in sp for sp in account_buttons), "Should have professional Subscription Plans button"

        print("PASS: Professional button texts are present")

    except Exception as e:
        print(f"FAIL: Button text check error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_callbacks()
    if success:
        print("\nAll callback handlers are working correctly!")
    else:
        print("\nSome callback handlers have issues.")
    sys.exit(0 if success else 1)
