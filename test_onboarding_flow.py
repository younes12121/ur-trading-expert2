"""
Lightweight tests for onboarding flow functionality
Tests onboarding logic without requiring actual Telegram API calls
"""

import sys
import os
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from onboarding_flow import OnboardingFlow, ONBOARDING_STATES

def test_onboarding_flow_initialization():
    """Test that onboarding flow initializes correctly"""
    flow = OnboardingFlow()
    assert flow.active_flows == {}
    print("PASS: Onboarding flow initialization test passed")

def test_start_flow():
    """Test starting a new onboarding flow"""
    flow = OnboardingFlow()
    user_id = 12345

    flow_data = flow.start_flow(user_id)

    assert user_id in flow.active_flows
    assert flow.active_flows[user_id]['state'] == ONBOARDING_STATES['WELCOME']
    assert flow.active_flows[user_id]['step'] == 1
    assert flow.active_flows[user_id]['total_steps'] == 6
    assert 'language' in flow.active_flows[user_id]['data']
    assert 'preferred_assets' in flow.active_flows[user_id]['data']
    print("PASS: Start flow test passed")

def test_flow_progression():
    """Test that flow progresses through states correctly"""
    flow = OnboardingFlow()
    user_id = 12345

    # Start flow
    flow.start_flow(user_id)

    # Test progression through states
    expected_states = [
        ONBOARDING_STATES['WELCOME'],
        ONBOARDING_STATES['LANGUAGE'],
        ONBOARDING_STATES['TIMEZONE'],
        ONBOARDING_STATES['EXPERIENCE'],
        ONBOARDING_STATES['ASSETS'],
        ONBOARDING_STATES['RISK'],
        ONBOARDING_STATES['NOTIFICATIONS'],
        ONBOARDING_STATES['COMPLETE']
    ]

    for expected_state in expected_states[1:]:  # Skip welcome since we start there
        flow.next_step(user_id)
        assert flow.active_flows[user_id]['state'] == expected_state

    print("PASS: Flow progression test passed")

def test_data_updates():
    """Test that flow data is updated correctly"""
    flow = OnboardingFlow()
    user_id = 12345

    flow.start_flow(user_id)

    # Test language update
    flow.update_flow_data(user_id, 'language', 'es')
    assert flow.active_flows[user_id]['data']['language'] == 'es'

    # Test asset selection
    flow.update_flow_data(user_id, 'preferred_assets', ['EURUSD', 'BTC'])
    assert flow.active_flows[user_id]['data']['preferred_assets'] == ['EURUSD', 'BTC']

    # Test risk tolerance
    flow.update_flow_data(user_id, 'risk_tolerance', 'high')
    assert flow.active_flows[user_id]['data']['risk_tolerance'] == 'high'

    print("PASS: Data updates test passed")

def test_callback_handling():
    """Test callback handling logic"""
    flow = OnboardingFlow()
    user_id = 12345

    flow.start_flow(user_id)

    # Test start callback
    message, keyboard, complete = flow.handle_callback(user_id, "onboard_start")
    assert message is not None and len(message) > 0  # Just check we got a message
    assert not complete

    # Test language selection
    message, keyboard, complete = flow.handle_callback(user_id, "lang_es")
    assert flow.active_flows[user_id]['data']['language'] == 'es'
    assert not complete

    # Test asset selection
    message, keyboard, complete = flow.handle_callback(user_id, "asset_EURUSD")
    assert 'EURUSD' in flow.active_flows[user_id]['data']['preferred_assets']
    assert not complete

    # Test completion
    # Advance to complete state
    for _ in range(6):  # Advance through remaining steps
        flow.next_step(user_id)

    message, keyboard, complete = flow.handle_callback(user_id, "onboard_finish")
    assert complete
    assert user_id not in flow.active_flows  # Should be removed after completion

    print("PASS: Callback handling test passed")

def test_step_messages():
    """Test that step messages are generated correctly"""
    flow = OnboardingFlow()
    user_id = 12345

    flow.start_flow(user_id)
    message, keyboard = flow.get_step_message(user_id)

    assert "QUICK START WIZARD" in message
    assert "Welcome" in message
    assert keyboard is not None

    # Test language step
    flow.next_step(user_id)
    message, keyboard = flow.get_step_message(user_id)
    assert "Choose Your Language" in message

    # Test assets step
    flow.next_step(user_id)  # timezone
    flow.next_step(user_id)  # experience
    flow.next_step(user_id)  # assets
    message, keyboard = flow.get_step_message(user_id)
    assert "Choose Your Assets" in message

    print("PASS: Step messages test passed")

def test_flow_completion():
    """Test flow completion and cleanup"""
    flow = OnboardingFlow()
    user_id = 12345

    flow.start_flow(user_id)

    # Fill in some data
    flow.update_flow_data(user_id, 'language', 'en')
    flow.update_flow_data(user_id, 'timezone', 'UTC')
    flow.update_flow_data(user_id, 'preferred_assets', ['BTC', 'GOLD'])

    # Complete flow
    result = flow.complete_flow(user_id)

    assert 'language' in result
    assert result['language'] == 'en'
    assert result['preferred_assets'] == ['BTC', 'GOLD']
    assert user_id not in flow.active_flows

    print("PASS: Flow completion test passed")

def run_all_tests():
    """Run all onboarding flow tests"""
    print("Running Onboarding Flow Tests...\n")

    try:
        test_onboarding_flow_initialization()
        test_start_flow()
        test_flow_progression()
        test_data_updates()
        test_callback_handling()
        test_step_messages()
        test_flow_completion()

        print("\nAll onboarding flow tests passed!")
        return True

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
