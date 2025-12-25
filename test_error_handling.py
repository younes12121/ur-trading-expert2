"""
Comprehensive Error Handling and Validation Tests
Tests all error conditions and validation logic for advanced order features
"""

import unittest
from advanced_order_manager import (
    create_bracket_order, create_oco_order, create_trailing_stop,
    update_price_feed, cancel_order, get_portfolio_summary
)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and validation for advanced order functions"""

    def setUp(self):
        """Clear state before each test"""
        from advanced_order_manager import advanced_order_manager
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()
        advanced_order_manager.oco_orders.clear()
        advanced_order_manager.trailing_stops.clear()

    # ============================================================================
    # BRACKET ORDER VALIDATION TESTS
    # ============================================================================

    def test_bracket_order_invalid_side(self):
        """Test bracket order with invalid side"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "INVALID", 1.0850, 1000, 1.0800, 1.0950)

        self.assertIn("Invalid side", str(context.exception))
        self.assertIn("BUY or SELL", str(context.exception))

    def test_bracket_order_zero_quantity(self):
        """Test bracket order with zero quantity"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "BUY", 1.0850, 0, 1.0800, 1.0950)

        self.assertIn("positive", str(context.exception))

    def test_bracket_order_negative_quantity(self):
        """Test bracket order with negative quantity"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "BUY", 1.0850, -1000, 1.0800, 1.0950)

        self.assertIn("positive", str(context.exception))

    def test_bracket_order_zero_prices(self):
        """Test bracket order with zero prices"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "BUY", 0, 1000, 1.0800, 1.0950)

        self.assertIn("positive", str(context.exception))

    def test_bracket_order_negative_prices(self):
        """Test bracket order with negative prices"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "BUY", -1.0850, 1000, 1.0800, 1.0950)

        self.assertIn("positive", str(context.exception))

    def test_bracket_order_buy_invalid_stop_loss(self):
        """Test BUY bracket order with stop loss above entry"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0900, 1.0950)

        self.assertIn("stop loss", str(context.exception).lower())
        self.assertIn("below entry", str(context.exception).lower())

    def test_bracket_order_buy_invalid_take_profit(self):
        """Test BUY bracket order with take profit below entry"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0750)

        self.assertIn("take profit", str(context.exception).lower())
        self.assertIn("above entry", str(context.exception).lower())

    def test_bracket_order_sell_invalid_stop_loss(self):
        """Test SELL bracket order with stop loss below entry"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "SELL", 1.0850, 1000, 1.0800, 1.0950)

        self.assertIn("stop loss", str(context.exception).lower())
        self.assertIn("above entry", str(context.exception).lower())

    def test_bracket_order_sell_invalid_take_profit(self):
        """Test SELL bracket order with take profit above entry"""
        with self.assertRaises(ValueError) as context:
            create_bracket_order("EURUSD", "SELL", 1.0850, 1000, 1.0900, 1.0950)

        self.assertIn("take profit", str(context.exception).lower())
        self.assertIn("below entry", str(context.exception).lower())

    # ============================================================================
    # OCO ORDER VALIDATION TESTS
    # ============================================================================

    def test_oco_order_zero_quantity(self):
        """Test OCO order with zero quantity"""
        with self.assertRaises(ValueError) as context:
            create_oco_order("EURUSD", 0, [
                {'side': 'SELL', 'price': 1.0900, 'type': 'limit'}
            ])

        self.assertIn("positive", str(context.exception))

    def test_oco_order_insufficient_orders(self):
        """Test OCO order with only one order specification"""
        with self.assertRaises(ValueError) as context:
            create_oco_order("EURUSD", 1000, [
                {'side': 'SELL', 'price': 1.0900, 'type': 'limit'}
            ])

        self.assertIn("at least 2", str(context.exception))

    def test_oco_order_invalid_side(self):
        """Test OCO order with invalid side"""
        with self.assertRaises(ValueError) as context:
            create_oco_order("EURUSD", 1000, [
                {'side': 'INVALID', 'price': 1.0900, 'type': 'limit'},
                {'side': 'SELL', 'stop_price': 1.0850, 'type': 'stop'}
            ])

        self.assertIn("Invalid or missing side", str(context.exception))

    def test_oco_order_invalid_type(self):
        """Test OCO order with invalid type"""
        with self.assertRaises(ValueError) as context:
            create_oco_order("EURUSD", 1000, [
                {'side': 'SELL', 'price': 1.0900, 'type': 'invalid'},
                {'side': 'SELL', 'stop_price': 1.0850, 'type': 'stop'}
            ])

        self.assertIn("Invalid or missing type", str(context.exception))

    def test_oco_order_limit_missing_price(self):
        """Test OCO order with limit type missing price"""
        with self.assertRaises(ValueError) as context:
            create_oco_order("EURUSD", 1000, [
                {'side': 'SELL', 'type': 'limit'},
                {'side': 'SELL', 'stop_price': 1.0850, 'type': 'stop'}
            ])

        self.assertIn("missing price", str(context.exception))

    def test_oco_order_stop_missing_stop_price(self):
        """Test OCO order with stop type missing stop_price"""
        with self.assertRaises(ValueError) as context:
            create_oco_order("EURUSD", 1000, [
                {'side': 'SELL', 'price': 1.0900, 'type': 'limit'},
                {'side': 'SELL', 'type': 'stop'}
            ])

        self.assertIn("missing stop_price", str(context.exception))

    # ============================================================================
    # TRAILING STOP VALIDATION TESTS
    # ============================================================================

    def test_trailing_stop_invalid_side(self):
        """Test trailing stop with invalid side"""
        with self.assertRaises(ValueError) as context:
            create_trailing_stop("EURUSD", "INVALID", 1000, 0.0050)

        self.assertIn("Invalid side", str(context.exception))

    def test_trailing_stop_zero_quantity(self):
        """Test trailing stop with zero quantity"""
        with self.assertRaises(ValueError) as context:
            create_trailing_stop("EURUSD", "SELL", 0, 0.0050)

        self.assertIn("positive", str(context.exception))

    def test_trailing_stop_zero_distance(self):
        """Test trailing stop with zero distance"""
        with self.assertRaises(ValueError) as context:
            create_trailing_stop("EURUSD", "SELL", 1000, 0)

        self.assertIn("positive", str(context.exception))

    def test_trailing_stop_negative_distance(self):
        """Test trailing stop with negative distance"""
        with self.assertRaises(ValueError) as context:
            create_trailing_stop("EURUSD", "SELL", 1000, -0.0050)

        self.assertIn("positive", str(context.exception))

    def test_trailing_stop_negative_activation_price(self):
        """Test trailing stop with negative activation price"""
        with self.assertRaises(ValueError) as context:
            create_trailing_stop("EURUSD", "SELL", 1000, 0.0050, -1.0850)

        self.assertIn("positive", str(context.exception))

    def test_trailing_stop_zero_activation_price(self):
        """Test trailing stop with zero activation price"""
        with self.assertRaises(ValueError) as context:
            create_trailing_stop("EURUSD", "SELL", 1000, 0.0050, 0)

        self.assertIn("positive", str(context.exception))

    # ============================================================================
    # PRICE UPDATE VALIDATION TESTS
    # ============================================================================

    def test_update_price_feed_zero_price(self):
        """Test price update with zero price"""
        with self.assertRaises(ValueError) as context:
            update_price_feed("EURUSD", 0)

        self.assertIn("positive", str(context.exception))

    def test_update_price_feed_negative_price(self):
        """Test price update with negative price"""
        with self.assertRaises(ValueError) as context:
            update_price_feed("EURUSD", -1.0850)

        self.assertIn("positive", str(context.exception))

    # ============================================================================
    # ORDER CANCELLATION TESTS
    # ============================================================================

    def test_cancel_nonexistent_order(self):
        """Test cancelling an order that doesn't exist"""
        result = cancel_order("NONEXISTENT_ORDER_ID")
        self.assertFalse(result)

    def test_cancel_order_success(self):
        """Test successful order cancellation"""
        # Create an order first
        bracket = create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        # Cancel it
        result = cancel_order(bracket['entry_order'])
        self.assertTrue(result)

        # Verify it's gone from portfolio
        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 0)

    # ============================================================================
    # INTEGRATION ERROR TESTS
    # ============================================================================

    def test_multiple_invalid_orders(self):
        """Test creating multiple invalid orders doesn't corrupt state"""
        # Try to create several invalid orders
        with self.assertRaises(ValueError):
            create_bracket_order("EURUSD", "INVALID", 1.0850, 1000, 1.0800, 1.0950)

        with self.assertRaises(ValueError):
            create_oco_order("EURUSD", 0, [{'side': 'BUY', 'price': 1.0850, 'type': 'limit'}])

        with self.assertRaises(ValueError):
            create_trailing_stop("EURUSD", "SELL", -1000, 0.0050)

        # State should remain clean
        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 0)
        self.assertEqual(summary['bracket_orders'], 0)
        self.assertEqual(summary['oco_orders'], 0)
        self.assertEqual(summary['trailing_stops'], 0)

    def test_mixed_valid_invalid_operations(self):
        """Test mixing valid and invalid operations"""
        # Create one valid order
        bracket = create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        # Try invalid operations
        with self.assertRaises(ValueError):
            create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0900, 1.0950)  # Invalid stop

        # Valid order should still exist
        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 3)  # bracket has 3 orders
        self.assertEqual(summary['bracket_orders'], 1)

    def test_error_recovery_after_invalid_operations(self):
        """Test that system recovers properly after invalid operations"""
        initial_summary = get_portfolio_summary()

        # Perform some invalid operations
        try:
            create_bracket_order("EURUSD", "INVALID", 1.0850, 1000, 1.0800, 1.0950)
        except ValueError:
            pass

        try:
            update_price_feed("EURUSD", -1.0)
        except ValueError:
            pass

        # System should be in same state
        final_summary = get_portfolio_summary()
        self.assertEqual(final_summary['active_orders'], initial_summary['active_orders'])
        self.assertEqual(final_summary['bracket_orders'], initial_summary['bracket_orders'])

    # ============================================================================
    # EDGE CASES AND BOUNDARY CONDITIONS
    # ============================================================================

    def test_extreme_price_values(self):
        """Test with extreme but valid price values"""
        # Very high prices
        bracket = create_bracket_order("EURUSD", "BUY", 999999.9999, 1000, 999990.0000, 1000000.0000)

        # Very low prices
        oco = create_oco_order("EURUSD", 1000, [
            {'side': 'SELL', 'price': 0.0001, 'type': 'limit'},
            {'side': 'SELL', 'stop_price': 0.00005, 'type': 'stop'}
        ])

        # Very small distances
        trailing = create_trailing_stop("EURUSD", "SELL", 1000, 0.000001)

        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 6)  # 3 + 2 + 1
        self.assertEqual(summary['bracket_orders'], 1)
        self.assertEqual(summary['oco_orders'], 1)
        self.assertEqual(summary['trailing_stops'], 1)

    def test_large_quantity_values(self):
        """Test with very large quantities"""
        # Large quantities
        bracket = create_bracket_order("EURUSD", "BUY", 1.0850, 999999999, 1.0800, 1.0950)

        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 3)

    def test_special_characters_in_symbol(self):
        """Test symbols with special characters"""
        # Symbols with numbers and special chars
        bracket = create_bracket_order("BTC/USD", "BUY", 45000.00, 0.1, 44000.00, 46000.00)
        oco = create_oco_order("XAUUSD.pro", 10, [
            {'side': 'SELL', 'price': 1950.00, 'type': 'limit'},
            {'side': 'SELL', 'stop_price': 1920.00, 'type': 'stop'}
        ])

        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 5)

    def test_empty_and_whitespace_symbols(self):
        """Test with empty or whitespace symbols"""
        with self.assertRaises(Exception):
            # This should fail during order creation (empty symbol not validated, but may cause issues)
            create_bracket_order("", "BUY", 1.0850, 1000, 1.0800, 1.0950)

    def test_concurrent_error_conditions(self):
        """Test multiple error conditions occurring simultaneously"""
        # Create a valid order first
        bracket = create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        # Try multiple invalid operations at once
        errors = []

        try:
            create_bracket_order("EURUSD", "INVALID", 1.0850, 1000, 1.0800, 1.0950)
        except ValueError:
            errors.append("invalid_side")

        try:
            update_price_feed("EURUSD", -1.0)
        except ValueError:
            errors.append("negative_price")

        try:
            cancel_order("NONEXISTENT")
        except:
            errors.append("cancel_nonexistent")

        # Should have caught multiple errors
        self.assertGreater(len(errors), 1)

        # Valid order should still exist
        summary = get_portfolio_summary()
        self.assertGreater(summary['active_orders'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
