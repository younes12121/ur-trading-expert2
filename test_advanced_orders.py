"""
Comprehensive Test Suite for Advanced Order Features
Tests bracket orders, OCO orders, trailing stops, and order management
"""

import unittest
import time
from datetime import datetime
from advanced_order_manager import (
    AdvancedOrderManager, create_bracket_order, create_oco_order,
    create_trailing_stop, update_price_feed, get_portfolio_summary, cancel_order
)


class TestAdvancedOrderManager(unittest.TestCase):
    """Test cases for AdvancedOrderManager class"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear global state for each test
        from advanced_order_manager import advanced_order_manager
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()
        advanced_order_manager.oco_orders.clear()
        advanced_order_manager.trailing_stops.clear()
        self.test_symbol = "EURUSD"

    def test_bracket_order_creation(self):
        """Test bracket order creation with valid parameters"""
        from advanced_order_manager import advanced_order_manager

        bracket = create_bracket_order(
            symbol=self.test_symbol,
            side="BUY",
            entry_price=1.0850,
            quantity=1000,
            stop_loss=1.0800,
            take_profit=1.0950
        )

        # Verify bracket structure
        self.assertIn('bracket_id', bracket)
        self.assertIn('entry_order', bracket)
        self.assertIn('stop_order', bracket)
        self.assertIn('take_profit_order', bracket)

        # Verify orders were created
        summary = get_portfolio_summary()
        self.assertEqual(summary['bracket_orders'], 1)
        self.assertEqual(summary['active_orders'], 3)  # entry + stop + tp

    def test_bracket_order_with_trailing_stop(self):
        """Test bracket order with trailing stop"""
        from advanced_order_manager import advanced_order_manager

        bracket = create_bracket_order(
            symbol=self.test_symbol,
            side="BUY",
            entry_price=1.0850,
            quantity=1000,
            stop_loss=1.0800,
            take_profit=1.0950,
            trailing_stop=True,
            trailing_distance=0.0050
        )

        # Verify trailing stop was enabled
        bracket_id = bracket['bracket_id']
        bracket_info = advanced_order_manager.bracket_orders[bracket_id]
        self.assertTrue(bracket_info['trailing_stop'])
        self.assertEqual(bracket_info['trailing_distance'], 0.0050)

    def test_bracket_order_validation(self):
        """Test bracket order parameter validation"""
        # Invalid side
        with self.assertRaises(Exception):
            create_bracket_order(
                symbol=self.test_symbol,
                side="INVALID",
                entry_price=1.0850,
                quantity=1000,
                stop_loss=1.0800,
                take_profit=1.0950
            )

        # Invalid BUY order (stop >= entry)
        with self.assertRaises(Exception):
            create_bracket_order(
                symbol=self.test_symbol,
                side="BUY",
                entry_price=1.0850,
                quantity=1000,
                stop_loss=1.0860,  # Stop above entry
                take_profit=1.0950
            )

        # Invalid SELL order (stop <= entry)
        with self.assertRaises(Exception):
            create_bracket_order(
                symbol=self.test_symbol,
                side="SELL",
                entry_price=1.0850,
                quantity=1000,
                stop_loss=1.0840,  # Stop below entry
                take_profit=1.0750
            )

    def test_oco_order_creation(self):
        """Test OCO order creation"""
        from advanced_order_manager import advanced_order_manager

        oco = create_oco_order(
            symbol=self.test_symbol,
            quantity=500,
            orders=[
                {'side': 'SELL', 'price': 1.0900, 'type': 'limit'},
                {'side': 'SELL', 'stop_price': 1.0850, 'type': 'stop'}
            ]
        )

        # Verify OCO structure
        self.assertIn('oco_id', oco)
        self.assertIn('order_ids', oco)
        self.assertEqual(len(oco['order_ids']), 2)

        # Verify orders were created
        summary = get_portfolio_summary()
        self.assertEqual(summary['oco_orders'], 1)
        self.assertEqual(summary['active_orders'], 2)

    def test_oco_order_execution(self):
        """Test OCO one-cancels-other logic"""
        oco = create_oco_order(
            symbol=self.test_symbol,
            quantity=500,
            orders=[
                {'side': 'SELL', 'price': 1.0900, 'type': 'limit'},
                {'side': 'SELL', 'stop_price': 1.0850, 'type': 'stop'}
            ]
        )

        # Simulate price hitting first order
        triggered = update_price_feed(self.test_symbol, 1.0900)

        # Verify first order was filled and second was cancelled
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0]['type'], 'order_filled')

        # Check that OCO group is closed
        from advanced_order_manager import advanced_order_manager
        oco_id = oco['oco_id']
        oco_info = advanced_order_manager.oco_orders[oco_id]
        self.assertEqual(oco_info['status'], 'closed')

    def test_trailing_stop_creation(self):
        """Test trailing stop creation"""
        from advanced_order_manager import advanced_order_manager

        order_id = create_trailing_stop(
            symbol=self.test_symbol,
            side="SELL",
            quantity=1000,
            trailing_distance=0.0050,
            activation_price=1.0850
        )

        # Verify trailing stop was created
        self.assertIn(order_id, advanced_order_manager.trailing_stops)
        ts_info = advanced_order_manager.trailing_stops[order_id]
        self.assertEqual(ts_info['symbol'], self.test_symbol)
        self.assertEqual(ts_info['trailing_distance'], 0.0050)
        self.assertEqual(ts_info['activation_price'], 1.0850)

    def test_trailing_stop_activation(self):
        """Test trailing stop activation and adjustment"""
        order_id = create_trailing_stop(
            symbol=self.test_symbol,
            side="SELL",  # Long position
            quantity=1000,
            trailing_distance=0.0050,
            activation_price=1.0850
        )

        # Price reaches activation level
        update_price_feed(self.test_symbol, 1.0850)

        # Verify activation
        from advanced_order_manager import advanced_order_manager
        ts_info = advanced_order_manager.trailing_stops[order_id]
        self.assertEqual(ts_info['status'], 'active')
        self.assertEqual(ts_info['highest_price'], 1.0850)

        # Price moves higher, stop should trail
        update_price_feed(self.test_symbol, 1.0900)
        self.assertEqual(ts_info['highest_price'], 1.0900)
        self.assertAlmostEqual(ts_info['current_stop_price'], 1.0850, places=4)  # 1.0900 - 0.0050

        # Price hits stop
        triggered = update_price_feed(self.test_symbol, 1.0840)  # Below stop
        self.assertEqual(len(triggered), 2)  # trailing_stop_triggered + order_filled
        trigger_types = [t['type'] for t in triggered]
        self.assertIn('trailing_stop_triggered', trigger_types)
        self.assertIn('order_filled', trigger_types)
        self.assertEqual(ts_info['status'], 'triggered')

    def test_order_cancellation(self):
        """Test order cancellation functionality"""
        # Create orders
        bracket = create_bracket_order(
            symbol=self.test_symbol,
            side="BUY",
            entry_price=1.0850,
            quantity=1000,
            stop_loss=1.0800,
            take_profit=1.0950
        )

        initial_orders = get_portfolio_summary()['active_orders']

        # Cancel entry order (should cancel entire bracket)
        success = cancel_order(bracket['entry_order'])
        self.assertTrue(success)

        # Verify all bracket orders were cancelled
        final_orders = get_portfolio_summary()['active_orders']
        self.assertEqual(final_orders, initial_orders - 3)  # entry + stop + tp

    def test_portfolio_summary(self):
        """Test portfolio summary functionality"""
        # Orders are already cleared in setUp

        # Create various orders
        create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)
        create_oco_order("GBPUSD", 500, [
            {'side': 'SELL', 'price': 1.2750, 'type': 'limit'},
            {'side': 'SELL', 'stop_price': 1.2650, 'type': 'stop'}
        ])
        create_trailing_stop("BTC", "SELL", 0.1, 1000)

        summary = get_portfolio_summary()

        # Verify counts
        self.assertEqual(summary['active_orders'], 6)  # 3 bracket + 2 OCO + 1 trailing
        self.assertEqual(summary['bracket_orders'], 1)
        self.assertEqual(summary['oco_orders'], 1)
        self.assertEqual(summary['trailing_stops'], 1)

        # Verify symbols
        self.assertIn('EURUSD', summary['by_symbol'])
        self.assertIn('GBPUSD', summary['by_symbol'])
        self.assertIn('BTC', summary['by_symbol'])

    def test_concurrent_price_updates(self):
        """Test handling multiple price updates"""
        # Create multiple orders
        create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)
        create_oco_order("GBPUSD", 500, [
            {'side': 'SELL', 'price': 1.2750, 'type': 'limit'},
            {'side': 'SELL', 'stop_price': 1.2650, 'type': 'stop'}
        ])

        # Simulate rapid price updates
        prices = [1.0840, 1.0850, 1.0860, 1.2700, 1.2720, 1.2750]

        total_triggered = 0
        for price in prices:
            # Update both symbols
            triggered_eur = update_price_feed("EURUSD", price)
            triggered_gbp = update_price_feed("GBPUSD", price)
            total_triggered += len(triggered_eur) + len(triggered_gbp)

        # Should have triggered some orders
        self.assertGreater(total_triggered, 0)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Zero quantity
        with self.assertRaises(Exception):
            create_bracket_order("EURUSD", "BUY", 1.0850, 0, 1.0800, 1.0950)

        # Negative prices
        with self.assertRaises(Exception):
            create_bracket_order("EURUSD", "BUY", -1.0850, 1000, 1.0800, 1.0950)

        # Invalid symbol
        bracket = create_bracket_order("", "BUY", 1.0850, 1000, 1.0800, 1.0950)
        # Should still create but may have issues with empty symbol

    def test_memory_management(self):
        """Test that orders are properly cleaned up"""
        from advanced_order_manager import advanced_order_manager
        initial_memory = len(advanced_order_manager.active_orders)

        # Create and fill orders
        bracket = create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        # Fill the entry order
        update_price_feed("EURUSD", 1.0850)

        # The bracket should be marked as active, not cleaned up
        from advanced_order_manager import advanced_order_manager
        bracket_info = advanced_order_manager.bracket_orders[bracket['bracket_id']]
        self.assertEqual(bracket_info['status'], 'active')


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for realistic trading scenarios"""

    def setUp(self):
        # Clear global state for each test
        from advanced_order_manager import advanced_order_manager
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()
        advanced_order_manager.oco_orders.clear()
        advanced_order_manager.trailing_stops.clear()

    def test_scalping_strategy(self):
        """Test scalping strategy with tight bracket orders"""
        # Create tight scalping bracket
        bracket = create_bracket_order(
            symbol="EURUSD",
            side="BUY",
            entry_price=1.08500,
            quantity=10000,
            stop_loss=1.08450,  # 5 pip stop
            take_profit=1.08550  # 5 pip target
        )

        # Simulate quick scalping moves
        prices = [1.08480, 1.08500, 1.08520, 1.08550]  # Hit target

        triggered = []
        for price in prices:
            triggered.extend(update_price_feed("EURUSD", price))

        # Should have filled entry and take profit
        self.assertGreater(len(triggered), 0)

    def test_breakout_strategy(self):
        """Test breakout strategy with OCO orders"""
        # OCO for breakout: break above resistance OR pull back to support
        oco = create_oco_order(
            symbol="GBPUSD",
            quantity=2000,
            orders=[
                {'side': 'BUY', 'price': 1.2750, 'type': 'limit'},    # Breakout buy
                {'side': 'SELL', 'price': 1.2650, 'type': 'limit'}     # Pullback sell
            ]
        )

        # Simulate breakout
        triggered = update_price_feed("GBPUSD", 1.2750)

        # Should fill one side of OCO
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0]['type'], 'order_filled')

    def test_trend_following(self):
        """Test trend following with trailing stops"""
        # Enter long position
        entry_price = 1.0850
        trailing_distance = 0.0100  # 100 pip trail

        trailing_id = create_trailing_stop(
            symbol="EURUSD",
            side="SELL",  # Long position
            quantity=5000,
            trailing_distance=trailing_distance
        )

        # Simulate trending market
        trend_prices = [
            entry_price,  # Activate
            1.0900,  # Move up
            1.0950,  # Continue up
            1.1000,  # Peak
            1.0850,  # Pullback to trigger stop
        ]

        triggered = []
        for price in trend_prices:
            result = update_price_feed("EURUSD", price)
            triggered.extend(result)

        # Should have triggered trailing stop
        trailing_triggers = [t for t in triggered if t['type'] == 'trailing_stop_triggered']
        self.assertGreater(len(trailing_triggers), 0)

    def test_multi_asset_portfolio(self):
        """Test managing multiple assets simultaneously"""
        # Create orders for different assets
        create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)
        create_bracket_order("GBPUSD", "SELL", 1.2750, 800, 1.2850, 1.2650)
        create_trailing_stop("BTC", "SELL", 0.1, 1000)

        summary = get_portfolio_summary()

        # Should have orders across multiple symbols
        self.assertGreater(len(summary['by_symbol']), 1)
        self.assertIn('EURUSD', summary['by_symbol'])
        self.assertIn('GBPUSD', summary['by_symbol'])
        self.assertIn('BTC', summary['by_symbol'])


class TestPerformance(unittest.TestCase):
    """Performance and stress tests"""

    def setUp(self):
        # Clear global state for each test
        from advanced_order_manager import advanced_order_manager
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()
        advanced_order_manager.oco_orders.clear()
        advanced_order_manager.trailing_stops.clear()

    def test_high_frequency_updates(self):
        """Test performance with high-frequency price updates"""
        # Create many orders
        for i in range(10):
            create_bracket_order(f"EURUSD{i}", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        start_time = time.time()

        # Simulate 1000 price updates
        for i in range(1000):
            price = 1.0800 + (i * 0.0001)  # Gradual price movement
            update_price_feed("EURUSD5", price)  # Update one symbol

        end_time = time.time()
        duration = end_time - start_time

        # Should handle 1000 updates in reasonable time (< 1 second)
        self.assertLess(duration, 1.0, f"Performance test failed: {duration:.2f}s")

    def test_memory_usage(self):
        """Test memory usage with many orders"""
        from advanced_order_manager import advanced_order_manager
        initial_orders = len(advanced_order_manager.active_orders)

        # Create 100 orders
        for i in range(100):
            create_bracket_order(f"TEST{i}", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        final_orders = len(advanced_order_manager.active_orders)

        # Should have created 300 orders (3 per bracket)
        self.assertEqual(final_orders - initial_orders, 300)

        # Clean up
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
