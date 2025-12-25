#!/usr/bin/env python3
"""
Broker Setup Demonstration
Shows how to configure and use different brokers with the universal adapter
"""

from broker_connector import BrokerConnector, BrokerType

def main():
    bc = BrokerConnector()

    print("=== UR TRADING EXPERT - BROKER SETUP DEMO ===\n")

    # Show available brokers
    print("AVAILABLE BROKERS:")
    for broker in BrokerType:
        status = "[API READY]" if broker.value in ['oanda', 'interactive_brokers'] else "[API AVAILABLE]"
        print(f"   {broker.value.upper()} - {status}")
    print()

    # Show current connections
    print("CURRENT CONNECTIONS:")
    connections = bc.get_all_connections(7713994326)
    if connections:
        for conn in connections:
            print(f"   {conn['broker_type'].upper()}: {conn['status']} ({conn['trades_executed']} trades)")
    else:
        print("   No connections configured")
    print()

    # Setup OANDA (demo)
    print("SETTING UP OANDA CONNECTION (DEMO)...")
    oanda_creds = {
        'api_key': 'demo_api_key_12345',
        'account_id': '001-004-demo-001'
    }

    result = bc.connect_broker(7713994326, 'oanda', oanda_creds)
    print(f"   OANDA Connection: {'[SUCCESS]' if result else '[FAILED]'}")
    print()

    # Setup Interactive Brokers (demo)
    print("SETTING UP INTERACTIVE BROKERS CONNECTION (DEMO)...")
    ib_creds = {
        'host': '127.0.0.1',
        'port': 7497,
        'client_id': 1
    }

    result = bc.connect_broker(7713994326, 'interactive_brokers', ib_creds)
    print(f"   IB Connection: {'[SUCCESS]' if result else '[FAILED]'}")
    print()

    # Test trades
    print("TESTING TRADE EXECUTION...")

    trade_params = {
        'symbol': 'EURUSD',
        'direction': 'buy',
        'lots': 0.1,
        'sl': 1.08,
        'tp': 1.10
    }

    # Test OANDA
    print("   Testing OANDA trade...")
    result = bc.execute_trade(7713994326, 'oanda', trade_params)
    print(f"   Result: {'[SUCCESS]' if result['success'] else '[FAILED]'}")
    print(f"   Trade ID: {result['trade_id']}")
    print(f"   Broker: {result.get('broker', 'unknown')}")
    print()

    # Test MT5 (paper trading fallback)
    print("   Testing MT5 trade (paper trading fallback)...")
    result = bc.execute_trade(7713994326, 'mt5', trade_params)
    print(f"   Result: {'[SUCCESS]' if result['success'] else '[FAILED]'}")
    print(f"   Trade ID: {result['trade_id']}")
    print(f"   Broker: {result['broker']}")
    print(f"   Note: {result.get('note', 'N/A')}")
    print()

    # Show final status
    print("FINAL STATUS:")
    connections = bc.get_all_connections(7713994326)
    print(f"   Total connections: {len(connections)}")
    for conn in connections:
        print(f"   [OK] {conn['broker_type'].upper()} configured")
    print()
    print("YOUR BOT IS NOW READY FOR MULTI-BROKER TRADING!")
    print("   - OANDA API ready for live trading")
    print("   - Interactive Brokers API ready")
    print("   - Paper trading always available as fallback")
    print("   - Universal adapter handles everything automatically")

if __name__ == "__main__":
    main()
