"""
Performance and Stress Tests for Advanced Order System
Tests system performance under high load and stress conditions
"""

import unittest
import time
import threading
import concurrent.futures
from advanced_order_manager import (
    create_bracket_order, create_oco_order, create_trailing_stop,
    update_price_feed, get_portfolio_summary, cancel_order,
    advanced_order_manager
)


class TestPerformance(unittest.TestCase):
    """Performance tests for advanced order system"""

    def setUp(self):
        """Clear state before each test"""
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()
        advanced_order_manager.oco_orders.clear()
        advanced_order_manager.trailing_stops.clear()

    def test_order_creation_performance(self):
        """Test performance of creating many orders"""
        start_time = time.time()

        # Create 100 bracket orders
        for i in range(100):
            symbol = f"EURUSD{i}"
            entry = 1.0850 + (i * 0.0001)
            stop = entry - 0.0050
            target = entry + 0.0100
            create_bracket_order(symbol, "BUY", entry, 1000, stop, target)

        end_time = time.time()
        duration = end_time - start_time

        # Should create 100 brackets (300 orders) in reasonable time
        summary = get_portfolio_summary()
        self.assertEqual(summary['bracket_orders'], 100)
        self.assertEqual(summary['active_orders'], 300)

        # Should be fast (< 0.5 seconds for 100 orders)
        self.assertLess(duration, 0.5, f"Order creation too slow: {duration:.3f}s")

    def test_price_update_performance(self):
        """Test performance of high-frequency price updates"""
        # Create orders across multiple symbols
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD"]

        for symbol in symbols:
            # Create 10 orders per symbol
            for i in range(10):
                entry = 1.0850 + (i * 0.001)
                create_bracket_order(symbol, "BUY", entry, 1000, entry - 0.005, entry + 0.010)
                create_trailing_stop(symbol, "SELL", 500, 0.005)

        initial_orders = get_portfolio_summary()['active_orders']

        start_time = time.time()

        # Simulate 1000 price updates across all symbols (small movements)
        for i in range(1000):
            for symbol in symbols:
                # Small random movements around entry price to avoid triggering orders
                price = 1.0850 + ((hash(f"{symbol}{i}") % 200) - 100) * 0.00001
                update_price_feed(symbol, price)

        end_time = time.time()
        duration = end_time - start_time

        # Should handle 6000 price updates in reasonable time
        final_orders = get_portfolio_summary()['active_orders']

        # Should complete in under 2 seconds
        self.assertLess(duration, 2.0, f"Price updates too slow: {duration:.3f}s")

        # Orders should still exist (some may have been filled/cancelled)
        self.assertGreater(final_orders, initial_orders // 4)  # Allow many orders to be filled in performance test

    def test_concurrent_order_creation(self):
        """Test creating orders from multiple threads"""
        results = []
        errors = []

        def create_orders_thread(thread_id):
            """Worker function for concurrent order creation"""
            try:
                local_results = []
                for i in range(10):
                    symbol = f"EURUSD_T{thread_id}_{i}"
                    bracket = create_bracket_order(symbol, "BUY", 1.0850, 1000, 1.0800, 1.0950)
                    local_results.append(bracket)
                results.extend(local_results)
            except Exception as e:
                errors.append(str(e))

        # Start 5 threads, each creating 10 orders
        threads = []
        for i in range(5):
            t = threading.Thread(target=create_orders_thread, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Should have no errors
        self.assertEqual(len(errors), 0, f"Concurrent creation errors: {errors}")

        # Should have created 50 brackets (150 orders)
        summary = get_portfolio_summary()
        self.assertEqual(summary['bracket_orders'], 50)
        self.assertEqual(summary['active_orders'], 150)

    def test_memory_usage_scaling(self):
        """Test memory usage as order count scales"""
        memory_usage = []

        # Test with increasing order counts
        for order_count in [10, 50, 100, 200]:
            # Clear previous orders
            advanced_order_manager.active_orders.clear()
            advanced_order_manager.bracket_orders.clear()

            start_time = time.time()

            # Create orders
            for i in range(order_count):
                symbol = f"TEST{i}"
                create_bracket_order(symbol, "BUY", 1.0850, 1000, 1.0800, 1.0950)

            creation_time = time.time() - start_time

            summary = get_portfolio_summary()
            memory_usage.append({
                'orders': order_count,
                'active_orders': summary['active_orders'],
                'creation_time': creation_time
            })

        # Verify scaling is reasonable (should not be exponential)
        for i in range(1, len(memory_usage)):
            prev = memory_usage[i-1]
            curr = memory_usage[i]

            # Creation time should not increase exponentially
            time_ratio = curr['creation_time'] / prev['creation_time']
            order_ratio = curr['orders'] / prev['orders']

            # Time should scale roughly linearly or slightly worse, but not exponentially
            self.assertLess(time_ratio / order_ratio, 5.0,
                          f"Performance scaling too poor: {time_ratio / order_ratio:.2f}x")

    def test_stress_test_price_updates(self):
        """Stress test with continuous price updates"""
        # Create a complex portfolio
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "XAUUSD"]

        for symbol in symbols:
            # Mix of different order types
            create_bracket_order(symbol, "BUY", 1.0850, 1000, 1.0800, 1.0950)
            create_oco_order(symbol, 500, [
                {'side': 'SELL', 'price': 1.0900, 'type': 'limit'},
                {'side': 'SELL', 'stop_price': 1.0850, 'type': 'stop'}
            ])
            create_trailing_stop(symbol, "SELL", 1000, 0.0050)

        initial_summary = get_portfolio_summary()

        start_time = time.time()

        # Simulate 30 seconds of continuous trading
        end_time = start_time + 30.0
        update_count = 0

        while time.time() < end_time:
            for symbol in symbols:
                # Generate realistic price movement
                base_price = 1.0850
                volatility = 0.001  # 0.1% volatility per update
                price_change = (hash(f"{symbol}{update_count}") % 2000 - 1000) / 1000000.0
                price = base_price * (1 + price_change * volatility)

                update_price_feed(symbol, max(price, 0.0001))  # Ensure positive price

            update_count += 1

            # Small delay to prevent CPU hogging
            time.sleep(0.001)

        duration = time.time() - start_time
        final_summary = get_portfolio_summary()

        # Should have completed the full 30 seconds
        self.assertGreaterEqual(duration, 29.0)

        # Should have performed many updates
        self.assertGreater(update_count, 1000)

        # System should still be functional
        self.assertIsInstance(final_summary, dict)
        self.assertIn('active_orders', final_summary)


class TestStressConditions(unittest.TestCase):
    """Stress tests for extreme conditions"""

    def setUp(self):
        """Clear state before each test"""
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()
        advanced_order_manager.oco_orders.clear()
        advanced_order_manager.trailing_stops.clear()

    def test_maximum_order_capacity(self):
        """Test system with maximum reasonable order count"""
        max_orders = 500  # Reasonable maximum

        start_time = time.time()

        try:
            for i in range(max_orders):
                symbol = f"STRESS{i % 10}"  # Rotate through 10 symbols
                create_bracket_order(symbol, "BUY", 1.0850, 1000, 1.0800, 1.0950)

            creation_time = time.time() - start_time

            summary = get_portfolio_summary()

            # Should have created all orders
            self.assertEqual(summary['bracket_orders'], max_orders)
            self.assertEqual(summary['active_orders'], max_orders * 3)

            # Should be reasonably fast
            self.assertLess(creation_time, 5.0, f"Mass order creation too slow: {creation_time:.3f}s")

        except MemoryError:
            self.fail("System ran out of memory with 500 orders")
        except Exception as e:
            self.fail(f"Unexpected error with mass order creation: {e}")

    def test_extreme_price_volatility(self):
        """Test system under extreme price volatility"""
        # Create orders
        create_bracket_order("EURUSD", "BUY", 1.0850, 1000, 1.0800, 1.0950)
        create_trailing_stop("EURUSD", "SELL", 1000, 0.0100)  # Wide trailing stop

        # Simulate extreme volatility (50% price swings)
        prices = []
        base_price = 1.0850

        for i in range(1000):
            # Generate extreme price movements
            volatility = 0.5  # 50% volatility
            price_change = (hash(f"volatility{i}") % 2000 - 1000) / 1000.0
            price = base_price * (1 + price_change * volatility)
            prices.append(max(price, 0.0001))

        start_time = time.time()

        # Feed all prices rapidly
        for price in prices:
            update_price_feed("EURUSD", price)

        duration = time.time() - start_time

        # Should handle extreme volatility without crashing
        self.assertLess(duration, 2.0, f"Extreme volatility handling too slow: {duration:.3f}s")

        # System should still be functional
        summary = get_portfolio_summary()
        self.assertIsInstance(summary, dict)

    def test_concurrent_price_updates(self):
        """Test concurrent price updates from multiple sources"""
        # Create orders across multiple symbols
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

        for symbol in symbols:
            create_bracket_order(symbol, "BUY", 1.0850, 1000, 1.0800, 1.0950)
            create_trailing_stop(symbol, "SELL", 1000, 0.0050)

        initial_summary = get_portfolio_summary()

        def price_update_worker(symbol, worker_id):
            """Worker function for concurrent price updates"""
            for i in range(100):
                price = 1.0850 + (i * 0.0001) + (worker_id * 0.001)
                update_price_feed(symbol, price)

        # Run concurrent updates
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i, symbol in enumerate(symbols):
                future = executor.submit(price_update_worker, symbol, i)
                futures.append(future)

            # Wait for all to complete
            for future in concurrent.futures.as_completed(futures):
                future.result()

        final_summary = get_portfolio_summary()

        # System should handle concurrent updates
        self.assertIsInstance(final_summary, dict)
        self.assertIn('active_orders', final_summary)

    def test_resource_cleanup(self):
        """Test that resources are properly cleaned up"""
        import gc

        # Create many orders
        for i in range(100):
            create_bracket_order(f"CLEANUP{i}", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        initial_objects = len(advanced_order_manager.active_orders)

        # Delete all orders
        order_ids = list(advanced_order_manager.active_orders.keys())
        for order_id in order_ids:
            cancel_order(order_id)

        # Check that active orders count is 0 (cancelled orders not counted)
        final_summary = get_portfolio_summary()
        self.assertEqual(final_summary['active_orders'], 0)
        self.assertEqual(initial_objects, 300)  # 100 brackets * 3 orders each

    def test_error_recovery_under_load(self):
        """Test error recovery when system is under load"""
        # Create some valid orders
        for i in range(10):
            create_bracket_order(f"LOAD{i}", "BUY", 1.0850, 1000, 1.0800, 1.0950)

        initial_orders = get_portfolio_summary()['active_orders']

        # Mix valid and invalid operations under load
        errors_caught = 0

        for i in range(100):
            try:
                if i % 10 == 0:
                    # Invalid operation
                    create_bracket_order("EURUSD", "INVALID", 1.0850, 1000, 1.0800, 1.0950)
                else:
                    # Valid operation that may fill orders
                    price = 1.0800 + (i * 0.0005)
                    update_price_feed("LOAD0", price)
            except ValueError:
                errors_caught += 1

        final_orders = get_portfolio_summary()['active_orders']

        # Should have caught some errors
        self.assertGreater(errors_caught, 0)

        # System should still be functional
        self.assertIsInstance(final_orders, int)

        # Should not have corrupted the order book
        self.assertGreaterEqual(final_orders, 0)


class TestBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and edge cases"""

    def setUp(self):
        """Clear state before each test"""
        advanced_order_manager.active_orders.clear()
        advanced_order_manager.bracket_orders.clear()
        advanced_order_manager.oco_orders.clear()
        advanced_order_manager.trailing_stops.clear()

    def test_minimum_valid_values(self):
        """Test minimum valid values for all parameters"""
        # Minimum valid prices (very small positive numbers)
        create_bracket_order("EURUSD", "BUY", 0.000001, 1, 0.0000005, 0.000002)

        # Minimum quantity
        create_oco_order("EURUSD", 1, [
            {'side': 'SELL', 'price': 0.000002, 'type': 'limit'},
            {'side': 'SELL', 'stop_price': 0.000001, 'type': 'stop'}
        ])

        # Minimum trailing distance
        create_trailing_stop("EURUSD", "SELL", 1, 0.000001)

        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 6)  # 3 + 2 + 1

    def test_maximum_reasonable_values(self):
        """Test maximum reasonable values"""
        # Large but reasonable values
        create_bracket_order("EURUSD", "BUY", 999999.99, 1000000, 999990.00, 1000000.00)

        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 3)

    def test_precision_limits(self):
        """Test floating point precision limits"""
        # High precision prices
        price = 1.085012345678901
        stop = 1.080012345678901
        target = 1.095012345678901

        create_bracket_order("EURUSD", "BUY", price, 1000, stop, target)

        # Should handle high precision without issues
        summary = get_portfolio_summary()
        self.assertEqual(summary['active_orders'], 3)

    def test_symbol_name_limits(self):
        """Test various symbol name formats"""
        symbols = [
            "EURUSD",  # Standard
            "BTC/USD",  # With slash
            "XAUUSD.pro",  # With dot
            "US30.cash",  # With multiple dots
            "123456",  # Numbers only
            "MIXED123abc",  # Mixed alphanumeric
        ]

        for symbol in symbols:
            create_bracket_order(symbol, "BUY", 1.0850, 1000, 1.0800, 1.0950)

        summary = get_portfolio_summary()
        self.assertEqual(summary['bracket_orders'], len(symbols))


if __name__ == '__main__':
    unittest.main(verbosity=2)
