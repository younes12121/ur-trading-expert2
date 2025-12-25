"""
Trade Executor
Handles order execution on Binance (testnet and live)
"""

import requests
import time
import hmac
import hashlib
from typing import Dict, Optional
from datetime import datetime
import config

class BinanceExecutor:
    """Execute trades on Binance"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        self.api_key = api_key or config.BINANCE_API_KEY
        self.api_secret = api_secret or config.BINANCE_API_SECRET
        self.testnet = testnet
        
        if testnet:
            self.base_url = "https://testnet.binance.vision"
        else:
            self.base_url = "https://api.binance.com"
        
        self.headers = {
            'X-MBX-APIKEY': self.api_key
        }
    
    def _generate_signature(self, params: dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        try:
            endpoint = "/api/v3/account"
            params = {
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting account info: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception getting account info: {e}")
            return None
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """
        Place a market order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Amount to trade
        
        Returns:
            Order response or None
        """
        try:
            endpoint = "/api/v3/order"
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': quantity,
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error placing order: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception placing order: {e}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, 
                         price: float) -> Optional[Dict]:
        """Place a limit order"""
        try:
            endpoint = "/api/v3/order"
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'LIMIT',
                'timeInForce': 'GTC',  # Good Till Cancel
                'quantity': quantity,
                'price': price,
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error placing limit order: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception placing limit order: {e}")
            return None
    
    def place_stop_loss(self, symbol: str, side: str, quantity: float, 
                       stop_price: float) -> Optional[Dict]:
        """Place a stop loss order"""
        try:
            endpoint = "/api/v3/order"
            
            # For stop loss, side is opposite of position
            # If you're LONG (bought), stop loss is SELL
            # If you're SHORT (sold), stop loss is BUY
            
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'STOP_LOSS_LIMIT',
                'timeInForce': 'GTC',
                'quantity': quantity,
                'price': stop_price,  # Limit price
                'stopPrice': stop_price,  # Trigger price
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error placing stop loss: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception placing stop loss: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
        """Cancel an order"""
        try:
            endpoint = "/api/v3/order"
            params = {
                'symbol': symbol,
                'orderId': order_id,
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error canceling order: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception canceling order: {e}")
            return None
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """Get order status"""
        try:
            endpoint = "/api/v3/order"
            params = {
                'symbol': symbol,
                'orderId': order_id,
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting order status: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception getting order status: {e}")
            return None
    
    def execute_trade(self, signal: Dict) -> Optional[Dict]:
        """
        Execute a complete trade with entry, SL, and TP orders
        
        Args:
            signal: Trading signal with direction, entry, SL, TP1, TP2, lot_size
        
        Returns:
            Dictionary with order IDs
        """
        symbol = config.SYMBOL
        direction = signal['direction']
        lot_size = signal['lot_size']
        
        print(f"\n🚀 Executing {direction} trade...")
        print(f"   Symbol: {symbol}")
        print(f"   Lot Size: {lot_size}")
        
        # Step 1: Place market entry order
        entry_order = self.place_market_order(
            symbol=symbol,
            side=direction,
            quantity=lot_size
        )
        
        if not entry_order:
            print("❌ Failed to place entry order")
            return None
        
        print(f"✅ Entry order placed: {entry_order['orderId']}")
        
        # Step 2: Place stop loss
        sl_side = 'SELL' if direction == 'BUY' else 'BUY'
        sl_order = self.place_stop_loss(
            symbol=symbol,
            side=sl_side,
            quantity=lot_size,
            stop_price=signal['stop_loss']
        )
        
        if sl_order:
            print(f"✅ Stop loss placed: {sl_order['orderId']}")
        else:
            print("⚠️  Failed to place stop loss")
        
        # Step 3: Place take profit orders (TP1 and TP2)
        tp_side = 'SELL' if direction == 'BUY' else 'BUY'
        
        # TP1 - 50% of position
        tp1_quantity = lot_size / 2
        tp1_order = self.place_limit_order(
            symbol=symbol,
            side=tp_side,
            quantity=tp1_quantity,
            price=signal['take_profit_1']
        )
        
        if tp1_order:
            print(f"✅ TP1 placed: {tp1_order['orderId']}")
        
        # TP2 - remaining 50%
        tp2_order = self.place_limit_order(
            symbol=symbol,
            side=tp_side,
            quantity=tp1_quantity,
            price=signal['take_profit_2']
        )
        
        if tp2_order:
            print(f"✅ TP2 placed: {tp2_order['orderId']}")
        
        return {
            'entry_order_id': entry_order['orderId'],
            'sl_order_id': sl_order['orderId'] if sl_order else None,
            'tp1_order_id': tp1_order['orderId'] if tp1_order else None,
            'tp2_order_id': tp2_order['orderId'] if tp2_order else None,
            'timestamp': datetime.now()
        }


# Test (requires API keys)
if __name__ == "__main__":
    print("=" * 70)
    print("Trade Executor - Test Mode")
    print("=" * 70)
    print()
    print("⚠️  This requires valid Binance API keys")
    print("⚠️  Set BINANCE_API_KEY and BINANCE_API_SECRET in config.py")
    print()
    print("For safety, this will use Binance TESTNET by default")
    print()
    
    # Check if API keys are set
    if not config.BINANCE_API_KEY or not config.BINANCE_API_SECRET:
        print("❌ API keys not configured")
        print("   Please add your keys to config.py")
    else:
        executor = BinanceExecutor(testnet=True)
        
        # Test account info
        print("Testing account connection...")
        account = executor.get_account_info()
        
        if account:
            print("✅ Connected to Binance Testnet!")
            print(f"   Account Type: {account.get('accountType', 'N/A')}")
        else:
            print("❌ Failed to connect")
    
    print("\n" + "=" * 70)
