"""
Broker Connector Module
Manages connections to MT4/MT5 and other brokers for trade execution
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

# Try to import MetaTrader5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("[WARNING] MetaTrader5 library not installed. Install with: pip install MetaTrader5")

class BrokerType(Enum):
    """Supported broker types"""
    OANDA = "oanda"
    MT4 = "mt4"
    MT5 = "mt5"
    IC_MARKETS = "ic_markets"
    INTERACTIVE_BROKERS = "interactive_brokers"
    BINANCE = "binance"
    COINBASE = "coinbase"
    FXCM = "fxcm"
    PEPPERSTONE = "pepperstone"
    XM = "xm"
    EXNESS = "exness"

class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

class TradeDirection(Enum):
    """Trade direction"""
    BUY = "buy"
    SELL = "sell"

class BrokerConnector:
    """Manages broker connections and trade execution"""
    
    def __init__(self, data_file="broker_connections.json"):
        self.data_file = data_file
        self.connections = {}  # {user_id: {broker_type, credentials, status}}
        self.partnerships = {}  # {broker_name: {revenue_share, api_access, co_marketing}}
        self.load_connections()
        self.load_partnerships()
    
    def load_connections(self):
        """Load broker connections"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.connections = json.load(f)
            except:
                self.connections = {}
    
    def save_connections(self):
        """Save broker connections"""
        with open(self.data_file, 'w') as f:
            json.dump(self.connections, f, indent=2)
    
    def load_partnerships(self):
        """Load broker partnership configurations"""
        partnerships_file = "broker_partnerships.json"
        if os.path.exists(partnerships_file):
            try:
                with open(partnerships_file, 'r') as f:
                    self.partnerships = json.load(f)
            except:
                self.partnerships = {}
    
    def save_partnerships(self):
        """Save broker partnerships"""
        partnerships_file = "broker_partnerships.json"
        with open(partnerships_file, 'w') as f:
            json.dump(self.partnerships, f, indent=2)
    
    def add_partnership(self, broker_name: str, partnership_config: Dict):
        """Add or update broker partnership
        
        Args:
            broker_name: Name of broker
            partnership_config: {
                'revenue_share': 0.20,  # 20% commission
                'api_access': True,
                'co_marketing': True,
                'white_label': False,
                'integration_type': 'api' or 'webhook',
                'status': 'active' or 'pending'
            }
        """
        self.partnerships[broker_name] = {
            **partnership_config,
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
        self.save_partnerships()
    
    def get_partnership_info(self, broker_name: str) -> Optional[Dict]:
        """Get partnership information for a broker"""
        return self.partnerships.get(broker_name)
    
    def calculate_partnership_revenue(self, broker_name: str, user_volume: float) -> float:
        """Calculate revenue share for broker partnership
        
        Args:
            broker_name: Broker name
            user_volume: Trading volume from referred users
        
        Returns:
            Revenue share amount
        """
        partnership = self.get_partnership_info(broker_name)
        if not partnership or partnership.get('status') != 'active':
            return 0.0
        
        revenue_share_rate = partnership.get('revenue_share', 0.20)
        # Assume $5 commission per lot traded
        commission_per_lot = 5.0
        total_commissions = user_volume * commission_per_lot
        revenue_share = total_commissions * revenue_share_rate
        
        return revenue_share
    
    # ============================================================================
    # CONNECTION MANAGEMENT
    # ============================================================================
    
    def connect_broker(self, user_id: int, broker_type: str, credentials: Dict) -> bool:
        """Connect user to broker
        
        Args:
            user_id: User ID
            broker_type: Type of broker (oanda, mt4, mt5, etc.)
            credentials: Dict with API keys, account ID, etc.
        
        Returns:
            True if connection successful
        """
        user_id_str = str(user_id)
        
        # Validate broker type
        try:
            broker = BrokerType(broker_type.lower())
        except ValueError:
            return False
        
        # Validate credentials based on broker type
        if not self._validate_credentials(broker, credentials):
            return False
        
        # Create connection
        if user_id_str not in self.connections:
            self.connections[user_id_str] = {}
        
        self.connections[user_id_str][broker_type] = {
            'broker_type': broker_type,
            'credentials': credentials,  # In production, encrypt this!
            'status': 'connected',
            'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_used': None,
            'trades_executed': 0
        }
        
        self.save_connections()
        return True
    
    def disconnect_broker(self, user_id: int, broker_type: str) -> bool:
        """Disconnect from broker"""
        user_id_str = str(user_id)
        
        if user_id_str in self.connections and broker_type in self.connections[user_id_str]:
            del self.connections[user_id_str][broker_type]
            self.save_connections()
            return True
        
        return False
    
    def get_connection_status(self, user_id: int, broker_type: str) -> Optional[Dict]:
        """Get connection status"""
        user_id_str = str(user_id)
        
        if user_id_str in self.connections and broker_type in self.connections[user_id_str]:
            return self.connections[user_id_str][broker_type]
        
        return None
    
    def get_all_connections(self, user_id: int) -> List[Dict]:
        """Get all broker connections for user"""
        user_id_str = str(user_id)
        
        if user_id_str in self.connections:
            return list(self.connections[user_id_str].values())
        
        return []
    
    def _validate_credentials(self, broker: BrokerType, credentials: Dict) -> bool:
        """Validate credentials based on broker type"""
        if broker == BrokerType.OANDA:
            return 'api_key' in credentials and 'account_id' in credentials
        
        elif broker in [BrokerType.MT4, BrokerType.MT5]:
            return 'login' in credentials and 'password' in credentials and 'server' in credentials
        
        elif broker == BrokerType.IC_MARKETS:
            return 'api_key' in credentials and 'account_id' in credentials
        
        return False
    
    # ============================================================================
    # TRADE EXECUTION (Basic Implementation)
    # ============================================================================
    
    def execute_trade(self, user_id: int, broker_type: str, trade_params: Dict) -> Dict:
        """Execute a trade through broker
        
        Args:
            user_id: User ID
            broker_type: Broker to use
            trade_params: Dict with symbol, direction, lots, sl, tp, etc.
        
        Returns:
            Dict with trade result (success, trade_id, error, etc.)
        """
        # Check connection
        connection = self.get_connection_status(user_id, broker_type)
        
        if not connection or connection['status'] != 'connected':
            return {
                'success': False,
                'error': 'Not connected to broker'
            }
        
        # Validate trade parameters
        required_params = ['symbol', 'direction', 'lots']
        if not all(param in trade_params for param in required_params):
            return {
                'success': False,
                'error': 'Missing required trade parameters'
            }
        
        # Route to appropriate broker API
        if broker_type == 'oanda':
            result = self._execute_oanda_trade(connection, trade_params)
        elif broker_type in ['mt4', 'mt5']:
            result = self._execute_mt_trade(connection, trade_params, broker_type)
        else:
            return {
                'success': False,
                'error': f'Broker {broker_type} not supported yet'
            }
        
        # Update connection stats
        if result.get('success'):
            connection['last_used'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            connection['trades_executed'] += 1
            self.save_connections()
        
        return result
    
    def _execute_oanda_trade(self, connection: Dict, trade_params: Dict) -> Dict:
        """Execute trade through OANDA API
        
        This is a placeholder - would integrate with actual OANDA API
        """
        try:
            # In production, would use OANDA API client
            # from oanda_client import OandaClient
            # client = OandaClient(connection['credentials']['api_key'])
            # result = client.create_order(...)
            
            # Placeholder response
            return {
                'success': True,
                'trade_id': f"OANDA_{datetime.now().timestamp()}",
                'symbol': trade_params['symbol'],
                'direction': trade_params['direction'],
                'lots': trade_params['lots'],
                'entry_price': 0.0,  # Would come from broker
                'sl': trade_params.get('sl'),
                'tp': trade_params.get('tp'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_mt_trade(self, connection: Dict, trade_params: Dict, platform: str) -> Dict:
        """Execute trade through MT4/MT5 or Universal Broker API

        Universal adapter that works with or without MetaTrader5
        """
        try:
            # Try MetaTrader5 first if available
            if MT5_AVAILABLE and platform == 'mt5':
                return self._execute_mt5_native(connection, trade_params)
            elif platform == 'mt4':
                return self._execute_mt4_bridge(connection, trade_params)
            else:
                # Fallback: Universal broker adapter (works without MT5)
                return self._execute_universal_trade(connection, trade_params, platform)

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_mt5_native(self, connection: Dict, trade_params: Dict) -> Dict:
        """Execute trade using native MetaTrader5 API"""
        try:
            if not mt5.initialize():
                raise Exception("MT5 initialization failed")

            login = connection['credentials']['login']
            password = connection['credentials']['password']
            server = connection['credentials']['server']

            if not mt5.login(login=login, password=password, server=server):
                raise Exception("MT5 login failed")

            # Convert trade parameters to MT5 format
            symbol = trade_params['symbol']
            direction = trade_params['direction']
            volume = trade_params['lots']

            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if direction == 'buy' else mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).ask if direction == 'buy' else mt5.symbol_info_tick(symbol).bid,
                "sl": trade_params.get('sl', 0),
                "tp": trade_params.get('tp', 0),
                "deviation": 20,
                "magic": 234000,
                "comment": "UR Trading Expert Bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            result = mt5.order_send(request)
            mt5.shutdown()

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"MT5 trade failed: {result.retcode}")

            return {
                'success': True,
                'trade_id': str(result.order),
                'symbol': symbol,
                'direction': direction,
                'lots': volume,
                'entry_price': result.price,
                'sl': trade_params.get('sl'),
                'tp': trade_params.get('tp'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"MT5 Error: {str(e)}"
            }

    def _execute_mt4_bridge(self, connection: Dict, trade_params: Dict) -> Dict:
        """Execute trade through MT4 using REST API or bridge"""
        # MT4 bridge implementation would go here
        # For now, use universal adapter
        return self._execute_universal_trade(connection, trade_params, 'mt4')

    def _execute_universal_trade(self, connection: Dict, trade_params: Dict, platform: str) -> Dict:
        """Universal broker adapter - works with any broker API or simulation

        This method ensures the bot works regardless of Python version or MT5 availability
        """
        try:
            # Try to use actual broker APIs if available
            broker_name = connection.get('broker_type', platform)

            if broker_name == 'oanda' and self._has_oanda_api():
                return self._execute_oanda_trade(connection, trade_params)
            elif broker_name == 'interactive_brokers' and self._has_ib_api():
                return self._execute_ib_trade(connection, trade_params)
            else:
                # Fallback: Paper trading mode (simulated execution)
                return self._execute_paper_trade(connection, trade_params, platform)

        except Exception as e:
            return {
                'success': False,
                'error': f"Universal adapter error: {str(e)}"
            }

    def _execute_ib_trade(self, connection: Dict, trade_params: Dict) -> Dict:
        """Execute trade through Interactive Brokers API"""
        try:
            # Interactive Brokers implementation
            # from ibapi import *
            # Placeholder for IB API integration

            return {
                'success': True,
                'trade_id': f"IB_{datetime.now().timestamp()}",
                'symbol': trade_params['symbol'],
                'direction': trade_params['direction'],
                'lots': trade_params['lots'],
                'entry_price': 0.0,  # Would come from IB API
                'sl': trade_params.get('sl'),
                'tp': trade_params.get('tp'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'broker': 'interactive_brokers'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"IB Error: {str(e)}"
            }

    def _execute_paper_trade(self, connection: Dict, trade_params: Dict, platform: str) -> Dict:
        """Execute simulated paper trade when real broker API unavailable"""
        try:
            # Get current price from our data feeds
            symbol = trade_params['symbol']
            current_price = self._get_current_price(symbol)

            if not current_price:
                current_price = 1.0  # Fallback price

            # Simulate trade execution
            direction = trade_params['direction']
            entry_price = current_price

            return {
                'success': True,
                'trade_id': f"PAPER_{platform.upper()}_{datetime.now().timestamp()}",
                'symbol': symbol,
                'direction': direction,
                'lots': trade_params['lots'],
                'entry_price': entry_price,
                'sl': trade_params.get('sl'),
                'tp': trade_params.get('tp'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'broker': f'{platform}_paper',
                'note': 'Paper trading - no real money at risk'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Paper trade error: {str(e)}"
            }
    
    # ============================================================================
    # POSITION MANAGEMENT
    # ============================================================================
    
    def close_position(self, user_id: int, broker_type: str, position_id: str) -> Dict:
        """Close an open position
        
        Args:
            user_id: User ID
            broker_type: Broker
            position_id: Position ID to close
        
        Returns:
            Dict with result
        """
        connection = self.get_connection_status(user_id, broker_type)
        
        if not connection or connection['status'] != 'connected':
            return {
                'success': False,
                'error': 'Not connected to broker'
            }
        
        # Placeholder - would actually close position via broker API
        return {
            'success': True,
            'position_id': position_id,
            'close_price': 0.0,
            'pnl': 0.0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def modify_position(self, user_id: int, broker_type: str, position_id: str, 
                       new_sl: float = None, new_tp: float = None) -> Dict:
        """Modify stop loss or take profit
        
        Args:
            user_id: User ID
            broker_type: Broker
            position_id: Position ID
            new_sl: New stop loss price
            new_tp: New take profit price
        
        Returns:
            Dict with result
        """
        connection = self.get_connection_status(user_id, broker_type)
        
        if not connection or connection['status'] != 'connected':
            return {
                'success': False,
                'error': 'Not connected to broker'
            }
        
        # Placeholder - would actually modify position via broker API
        return {
            'success': True,
            'position_id': position_id,
            'new_sl': new_sl,
            'new_tp': new_tp,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_open_positions(self, user_id: int, broker_type: str) -> List[Dict]:
        """Get all open positions
        
        Args:
            user_id: User ID
            broker_type: Broker
        
        Returns:
            List of open positions
        """
        connection = self.get_connection_status(user_id, broker_type)
        
        if not connection or connection['status'] != 'connected':
            return []
        
        # MT5 Real Positions
        if broker_type in ['mt4', 'mt5'] and MT5_AVAILABLE:
            try:
                # Connect to MT5
                if not self._connect_mt5(connection):
                    return []
                
                # Get all positions
                positions = mt5.positions_get()
                
                if positions is None or len(positions) == 0:
                    mt5.shutdown()
                    return []
                
                result = []
                for pos in positions:
                    result.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == 0 else 'SELL',
                        'volume': pos.volume,
                        'open_price': pos.price_open,
                        'current_price': pos.price_current,
                        'sl': pos.sl,
                        'tp': pos.tp,
                        'profit': pos.profit,
                        'open_time': datetime.fromtimestamp(pos.time).strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # Shutdown MT5 connection
                mt5.shutdown()
                
                return result
                
            except Exception as e:
                print(f"Error getting MT5 positions: {e}")
                mt5.shutdown()
                return []
        
        # Placeholder for other brokers
        return []
    
    # ============================================================================
    # ACCOUNT INFORMATION
    # ============================================================================
    
    def _connect_mt5(self, connection: Dict) -> bool:
        """Initialize MT5 connection
        
        Args:
            connection: Connection dict with credentials
        
        Returns:
            True if connected successfully
        """
        if not MT5_AVAILABLE:
            return False
        
        # Initialize MT5
        if not mt5.initialize():
            return False
        
        # Login with credentials
        credentials = connection['credentials']
        login = int(credentials['login'])
        password = credentials['password']
        server = credentials['server']
        
        authorized = mt5.login(login=login, password=password, server=server)
        
        if not authorized:
            mt5.shutdown()
            return False
        
        return True
    
    def get_account_info(self, user_id: int, broker_type: str) -> Optional[Dict]:
        """Get account information from broker
        
        Args:
            user_id: User ID
            broker_type: Broker
        
        Returns:
            Dict with balance, equity, margin, etc.
        """
        connection = self.get_connection_status(user_id, broker_type)
        
        if not connection or connection['status'] != 'connected':
            return None
        
        # MT5 Real Account Info
        if broker_type in ['mt4', 'mt5'] and MT5_AVAILABLE:
            try:
                # Connect to MT5
                if not self._connect_mt5(connection):
                    return None
                
                # Get account info
                account_info = mt5.account_info()
                
                if account_info is None:
                    mt5.shutdown()
                    return None
                
                # Get positions count
                positions = mt5.positions_total()
                
                result = {
                    'balance': float(account_info.balance),
                    'equity': float(account_info.equity),
                    'margin_used': float(account_info.margin),
                    'margin_available': float(account_info.margin_free),
                    'open_positions': positions,
                    'currency': account_info.currency,
                    'leverage': account_info.leverage,
                    'profit': float(account_info.profit)
                }
                
                # Shutdown MT5 connection
                mt5.shutdown()
                
                return result
                
            except Exception as e:
                print(f"Error getting MT5 account info: {e}")
                mt5.shutdown()
                return None
        
        # Placeholder for OANDA and other brokers
        return {
            'balance': 10000.0,
            'equity': 10000.0,
            'margin_used': 0.0,
            'margin_available': 10000.0,
            'open_positions': 0,
            'currency': 'USD'
        }

    # ============================================================================
    # UNIVERSAL BROKER ADAPTER HELPERS
    # ============================================================================

    def _has_oanda_api(self) -> bool:
        """Check if Oanda API is available"""
        try:
            import oandapyV20
            return True
        except ImportError:
            return False

    def _has_ib_api(self) -> bool:
        """Check if Interactive Brokers API is available"""
        try:
            import ibapi
            return True
        except ImportError:
            return False

    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price from available data sources"""
        try:
            # Try TradingView first
            from tradingview_data_client import TradingViewDataClient
            client = TradingViewDataClient()
            price_data = client.get_price(symbol)

            if price_data and 'price' in price_data:
                return price_data['price']

            # Try Forex data client for forex pairs
            if symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']:
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "forex_client",
                        "Forex expert/shared/forex_data_client.py"
                    )
                    forex_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(forex_module)

                    client = forex_module.RealTimeForexClient()
                    price = client.get_price(symbol)
                    if price and 'mid' in price:
                        return price['mid']
                except:
                    pass

            return None

        except Exception:
            return None

    # ============================================================================
    # DISPLAY
    # ============================================================================
    
    def format_connection_message(self, user_id: int) -> str:
        """Format broker connections message"""
        connections = self.get_all_connections(user_id)
        
        if not connections:
            msg = "🔌 **BROKER CONNECTIONS**\n\n"
            msg += "No brokers connected yet.\n\n"
            msg += "*Supported Brokers:*\n"
            msg += "• OANDA\n"
            msg += "• MetaTrader 4\n"
            msg += "• MetaTrader 5\n"
            msg += "• IC Markets (coming soon)\n\n"
            msg += "*Benefits:*\n"
            msg += "✅ One-click trade execution\n"
            msg += "✅ Auto position sizing\n"
            msg += "✅ Auto SL/TP placement\n"
            msg += "✅ Real-time P&L tracking\n\n"
            msg += "*Commands:*\n"
            msg += "`/broker connect [type]` - Connect broker\n"
            msg += "`/broker help` - Setup instructions"
            return msg
        
        msg = "🔌 **YOUR BROKER CONNECTIONS**\n\n"
        
        for conn in connections:
            broker = conn['broker_type'].upper()
            status_emoji = {'connected': '[OK]', 'disconnected': '[FAIL]', 'error': '[WARNING]'}.get(conn['status'], '[WARNING]')
            
            msg += f"{status_emoji} *{broker}*\n"
            msg += f"   Connected: {conn['connected_at']}\n"
            msg += f"   Trades: {conn['trades_executed']}\n"
            
            if conn['last_used']:
                msg += f"   Last Used: {conn['last_used']}\n"
            
            msg += "\n"
        
        msg += "*Commands:*\n"
        msg += "`/broker account [type]` - View account info\n"
        msg += "`/broker positions [type]` - View open positions\n"
        msg += "`/broker disconnect [type]` - Disconnect broker"
        
        return msg


if __name__ == "__main__":
    # Test broker connector
    bc = BrokerConnector()
    
    # Connect OANDA
    oanda_creds = {
        'api_key': 'test_api_key_12345',
        'account_id': '001-004-1234567-001'
    }
    
    result = bc.connect_broker(123456, 'oanda', oanda_creds)
    print(f"OANDA Connection: {'Success' if result else 'Failed'}")
    
    # Execute trade
    trade_params = {
        'symbol': 'EUR_USD',
        'direction': 'buy',
        'lots': 0.1,
        'sl': 1.0850,
        'tp': 1.0950
    }
    
    result = bc.execute_trade(123456, 'oanda', trade_params)
    print(f"\nTrade Result: {result}")
    
    # View connections
    print("\n" + bc.format_connection_message(123456))

