"""
Advanced Order Types Demo
Showcase the new sophisticated order management capabilities
"""

from advanced_order_manager import (
    create_bracket_order, create_oco_order, create_trailing_stop,
    update_price_feed, get_portfolio_summary, cancel_order
)
import time

def demo_bracket_orders():
    """Demonstrate bracket order functionality"""
    print("BRACKET ORDERS DEMO")
    print("=" * 50)

    # Create a bracket order for EURUSD long
    print("Creating bracket order: EURUSD BUY at 1.0850, Stop at 1.0800, Target at 1.0950")
    bracket = create_bracket_order(
        symbol="EURUSD",
        side="BUY",
        entry_price=1.0850,
        quantity=1000,
        stop_loss=1.0800,
        take_profit=1.0950,
        trailing_stop=True,
        trailing_distance=0.0050
    )
    print(f"[OK] Bracket order created: {bracket['bracket_id']}")

    # Simulate price movement
    print("\nSimulating price movement...")
    prices = [1.0840, 1.0850, 1.0860, 1.0880, 1.0920, 1.0850]

    for price in prices:
        triggered = update_price_feed("EURUSD", price)
        if triggered:
            print(f"  Price {price}: {triggered[0]['type']} - {triggered[0]['order_id']}")
        else:
            print(f"  Price {price}: No orders triggered")

    print()

def demo_oco_orders():
    """Demonstrate OCO order functionality"""
    print("OCO ORDERS DEMO")
    print("=" * 50)

    # Create OCO order for GBPUSD
    print("Creating OCO order: GBPUSD - Take profit at 1.2750 OR Stop loss at 1.2650")
    oco = create_oco_order(
        symbol="GBPUSD",
        quantity=500,
        orders=[
            {'side': 'SELL', 'price': 1.2750, 'type': 'limit'},  # Take profit
            {'side': 'SELL', 'stop_price': 1.2650, 'type': 'stop'}  # Stop loss
        ]
    )
    print(f"[OK] OCO order created: {oco['oco_id']}")

    # Simulate price movement
    print("\nSimulating price movement...")
    prices = [1.2700, 1.2720, 1.2750, 1.2680]

    for price in prices:
        triggered = update_price_feed("GBPUSD", price)
        if triggered:
            print(f"  Price {price}: {triggered[0]['type']} - {triggered[0]['order_id']}")
        else:
            print(f"  Price {price}: No orders triggered")

    print()

def demo_trailing_stops():
    """Demonstrate trailing stop functionality"""
    print("TRAILING STOPS DEMO")
    print("=" * 50)

    # Create trailing stop for BTC
    print("Creating trailing stop: BTC SELL (long position) with 500 distance")
    trailing_id = create_trailing_stop(
        symbol="BTC",
        side="SELL",
        quantity=0.1,
        trailing_distance=500,
        activation_price=43500
    )
    print(f"[OK] Trailing stop created: {trailing_id}")

    # Simulate price movement
    print("\nSimulating price movement (BTC from 43000 to 45000)...")
    prices = [43000, 43500, 44000, 44500, 45000, 44700, 44200]

    for price in prices:
        triggered = update_price_feed("BTC", price)
        if triggered:
            print(f"  Price {price}: {triggered[0]['type']} - Stop triggered!")
            break
        else:
            print(f"  Price {price}: Trailing stop active")

    print()

def demo_order_management():
    """Demonstrate order management features"""
    print("ORDER MANAGEMENT DEMO")
    print("=" * 50)

    # Create multiple orders
    print("Creating sample orders...")
    bracket = create_bracket_order("USDJPY", "BUY", 150.00, 10000, 149.50, 151.00)
    oco = create_oco_order("AUDUSD", 2000, [
        {'side': 'SELL', 'price': 0.6800, 'type': 'limit'},
        {'side': 'SELL', 'stop_price': 0.6700, 'type': 'stop'}
    ])
    trailing = create_trailing_stop("XAUUSD", "SELL", 10, 2.0)

    # Show portfolio summary
    summary = get_portfolio_summary()
    print("Portfolio Summary:")
    print(f"  Active Orders: {summary['active_orders']}")
    print(f"  Bracket Orders: {summary['bracket_orders']}")
    print(f"  OCO Groups: {summary['oco_orders']}")
    print(f"  Trailing Stops: {summary['trailing_stops']}")

    if summary['by_symbol']:
        print("  By Symbol:")
        for symbol, counts in summary['by_symbol'].items():
            print(f"    {symbol}: {counts['buy']} BUY, {counts['sell']} SELL")

    # Cancel an order
    print(f"\nCancelling bracket order: {bracket['bracket_id']}")
    success = cancel_order(bracket['entry_order'])
    print(f"  Cancellation {'successful' if success else 'failed'}")

    # Show updated summary
    summary = get_portfolio_summary()
    print(f"\nUpdated Portfolio Summary:")
    print(f"  Active Orders: {summary['active_orders']}")

    print()

def main():
    """Run all demos"""
    print("ADVANCED ORDER TYPES COMPREHENSIVE DEMO")
    print("=" * 60)
    print("This demo showcases the new advanced order management system")
    print("including bracket orders, OCO orders, and trailing stops.\n")

    demo_bracket_orders()
    time.sleep(1)

    demo_oco_orders()
    time.sleep(1)

    demo_trailing_stops()
    time.sleep(1)

    demo_order_management()

    print("DEMO COMPLETE!")
    print("=" * 60)
    print("Your trading system now supports:")
    print("* Bracket Orders - Automated entry, stop loss, and take profit")
    print("* OCO Orders - One-cancels-other for multiple scenarios")
    print("* Trailing Stops - Intelligent profit protection")
    print("* Order Management - View, cancel, and monitor all orders")
    print("\nUse these commands in your Telegram bot:")
    print("/bracket - Create bracket orders")
    print("/oco - Create OCO orders")
    print("/trail - Create trailing stops")
    print("/orders - View active orders")
    print("/cancel - Cancel orders")

if __name__ == "__main__":
    main()
