"""
Advanced Order Management System
Implements sophisticated order types: Bracket Orders, OCO Orders, Trailing Stops
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PARTIAL = "partial"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Advanced order structure"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    limit_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: Optional[float] = None
    timestamp: datetime = None
    expiry: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class AdvancedOrderManager:
    """
    Advanced Order Management System
    Handles complex order types and automated execution
    """

    def __init__(self):
        self.active_orders = {}
        self.order_history = []
        self.trailing_stops = {}
        self.bracket_orders = {}
        self.oco_orders = {}

        # Order ID counter
        self._order_counter = 0

    def generate_order_id(self) -> str:
        """Generate unique order ID"""
        self._order_counter += 1
        return f"AO_{int(time.time())}_{self._order_counter}"

    def create_bracket_order(self, symbol: str, side: OrderSide, entry_price: float,
                           quantity: float, stop_loss: float, take_profit: float,
                           trailing_stop: bool = False, trailing_distance: float = 0.0) -> Dict[str, str]:
        """
        Create a bracket order with entry, stop loss, and take profit

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            entry_price: Entry price
            quantity: Order quantity
            stop_loss: Stop loss price
            take_profit: Take profit price
            trailing_stop: Enable trailing stop
            trailing_distance: Distance for trailing stop

        Returns:
            Dict with order IDs for parent, stop, and target orders
        """
        bracket_id = f"BRACKET_{self.generate_order_id()}"

        # Create parent entry order
        entry_order = Order(
            order_id=self.generate_order_id(),
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=entry_price,
            metadata={'bracket_id': bracket_id, 'bracket_type': 'entry'}
        )

        # Create stop loss order (opposite side)
        stop_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
        stop_order = Order(
            order_id=self.generate_order_id(),
            symbol=symbol,
            side=stop_side,
            order_type=OrderType.STOP,
            quantity=quantity,
            stop_price=stop_loss,
            metadata={'bracket_id': bracket_id, 'bracket_type': 'stop_loss'}
        )

        # Create take profit order (opposite side)
        tp_order = Order(
            order_id=self.generate_order_id(),
            symbol=symbol,
            side=stop_side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=take_profit,
            metadata={'bracket_id': bracket_id, 'bracket_type': 'take_profit'}
        )

        # Store bracket order
        self.bracket_orders[bracket_id] = {
            'entry': entry_order,
            'stop_loss': stop_order,
            'take_profit': tp_order,
            'trailing_stop': trailing_stop,
            'trailing_distance': trailing_distance,
            'status': 'pending'
        }

        # Add orders to active orders
        self.active_orders[entry_order.order_id] = entry_order
        self.active_orders[stop_order.order_id] = stop_order
        self.active_orders[tp_order.order_id] = tp_order

        logger.info(f"Created bracket order {bracket_id} for {symbol}")

        return {
            'bracket_id': bracket_id,
            'entry_order': entry_order.order_id,
            'stop_order': stop_order.order_id,
            'take_profit_order': tp_order.order_id
        }

    def create_oco_order(self, symbol: str, quantity: float, orders: List[Dict]) -> Dict[str, str]:
        """
        Create One-Cancels-Other (OCO) order group

        Args:
            symbol: Trading symbol
            quantity: Order quantity
            orders: List of order specs [{'side': 'BUY/SELL', 'price': float, 'type': 'limit/stop'}]

        Returns:
            Dict with OCO group ID and order IDs
        """
        oco_id = f"OCO_{self.generate_order_id()}"
        order_ids = []

        for i, order_spec in enumerate(orders):
            side = OrderSide(order_spec['side'].lower())
            order_type = OrderType(order_spec['type'].lower())

            order = Order(
                order_id=self.generate_order_id(),
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=order_spec.get('price'),
                stop_price=order_spec.get('stop_price'),
                metadata={'oco_id': oco_id, 'oco_index': i}
            )

            self.active_orders[order.order_id] = order
            order_ids.append(order.order_id)

        # Store OCO group
        self.oco_orders[oco_id] = {
            'orders': order_ids,
            'status': 'pending',
            'symbol': symbol
        }

        logger.info(f"Created OCO order {oco_id} with {len(order_ids)} orders for {symbol}")

        return {
            'oco_id': oco_id,
            'order_ids': order_ids
        }

    def create_trailing_stop(self, symbol: str, side: OrderSide, quantity: float,
                           trailing_distance: float, activation_price: Optional[float] = None) -> str:
        """
        Create a trailing stop order

        Args:
            symbol: Trading symbol
            side: SELL for long positions, BUY for short positions
            quantity: Order quantity
            trailing_distance: Distance to trail behind price
            activation_price: Price at which to activate trailing stop

        Returns:
            Trailing stop order ID
        """
        order_id = self.generate_order_id()

        trailing_stop = {
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'trailing_distance': trailing_distance,
            'activation_price': activation_price,
            'highest_price': float('-inf') if side == OrderSide.SELL else float('inf'),
            'lowest_price': float('inf') if side == OrderSide.SELL else float('-inf'),
            'current_stop_price': None,
            'status': 'active' if activation_price is None else 'pending',
            'created_at': datetime.now()
        }

        self.trailing_stops[order_id] = trailing_stop

        # Create the actual stop order
        stop_order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=OrderType.STOP,
            quantity=quantity,
            stop_price=None,  # Will be set when activated
            metadata={'trailing_stop': True}
        )

        self.active_orders[order_id] = stop_order

        logger.info(f"Created trailing stop {order_id} for {symbol}")

        return order_id

    def update_price(self, symbol: str, current_price: float) -> List[Dict[str, Any]]:
        """
        Update orders based on current market price
        Called whenever price updates occur

        Returns:
            List of triggered orders
        """
        triggered_orders = []

        # Update trailing stops
        triggered_orders.extend(self._update_trailing_stops(symbol, current_price))

        # Check for order fills
        triggered_orders.extend(self._check_order_fills(symbol, current_price))

        return triggered_orders

    def _update_trailing_stops(self, symbol: str, current_price: float) -> List[Dict[str, Any]]:
        """Update trailing stop orders"""
        triggered = []

        for order_id, ts in self.trailing_stops.items():
            if ts['symbol'] != symbol:
                continue

            # Activate trailing stop if price reaches activation level
            if ts['activation_price'] is not None and ts['status'] == 'pending':
                if ts['side'] == OrderSide.SELL and current_price >= ts['activation_price']:
                    ts['highest_price'] = current_price
                    ts['status'] = 'active'
                    ts['activation_price'] = None
                elif ts['side'] == OrderSide.BUY and current_price <= ts['activation_price']:
                    ts['lowest_price'] = current_price
                    ts['status'] = 'active'
                    ts['activation_price'] = None
                continue

            if ts['status'] != 'active':
                continue

            # Update trailing stop levels
            if ts['side'] == OrderSide.SELL:  # Long position
                if current_price > ts['highest_price']:
                    ts['highest_price'] = current_price
                    new_stop = current_price - ts['trailing_distance']
                    if ts['current_stop_price'] is None or new_stop > ts['current_stop_price']:
                        ts['current_stop_price'] = new_stop
                        self.active_orders[order_id].stop_price = new_stop

                # Check if stop is hit
                elif ts['current_stop_price'] is not None and current_price <= ts['current_stop_price']:
                    triggered.append({
                        'type': 'trailing_stop_triggered',
                        'order_id': order_id,
                        'symbol': symbol,
                        'price': current_price,
                        'stop_price': ts['current_stop_price']
                    })
                    ts['status'] = 'triggered'

            elif ts['side'] == OrderSide.BUY:  # Short position
                if current_price < ts['lowest_price']:
                    ts['lowest_price'] = current_price
                    new_stop = current_price + ts['trailing_distance']
                    if ts['current_stop_price'] is None or new_stop < ts['current_stop_price']:
                        ts['current_stop_price'] = new_stop
                        self.active_orders[order_id].stop_price = new_stop

                # Check if stop is hit
                elif ts['current_stop_price'] is not None and current_price >= ts['current_stop_price']:
                    triggered.append({
                        'type': 'trailing_stop_triggered',
                        'order_id': order_id,
                        'symbol': symbol,
                        'price': current_price,
                        'stop_price': ts['current_stop_price']
                    })
                    ts['status'] = 'triggered'

        return triggered

    def _check_order_fills(self, symbol: str, current_price: float) -> List[Dict[str, Any]]:
        """Check if any orders should be filled at current price"""
        triggered = []

        for order_id, order in self.active_orders.items():
            if order.symbol != symbol or order.status != OrderStatus.PENDING:
                continue

            should_fill = False

            if order.order_type == OrderType.MARKET:
                should_fill = True
            elif order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and current_price <= order.price:
                    should_fill = True
                elif order.side == OrderSide.SELL and current_price >= order.price:
                    should_fill = True
            elif order.order_type == OrderType.STOP:
                if order.stop_price is not None:
                    if order.side == OrderSide.BUY and current_price >= order.stop_price:
                        should_fill = True
                    elif order.side == OrderSide.SELL and current_price <= order.stop_price:
                        should_fill = True
            elif order.order_type == OrderType.STOP_LIMIT:
                if (order.stop_price is not None and order.limit_price is not None):
                    # Check stop trigger first
                    stop_triggered = False
                    if order.side == OrderSide.BUY and current_price >= order.stop_price:
                        stop_triggered = True
                    elif order.side == OrderSide.SELL and current_price <= order.stop_price:
                        stop_triggered = True

                    if stop_triggered:
                        # Now check limit price
                        if order.side == OrderSide.BUY and current_price <= order.limit_price:
                            should_fill = True
                        elif order.side == OrderSide.SELL and current_price >= order.limit_price:
                            should_fill = True

            if should_fill:
                # Fill the order
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.average_fill_price = current_price

                triggered.append({
                    'type': 'order_filled',
                    'order_id': order_id,
                    'symbol': symbol,
                    'price': current_price,
                    'quantity': order.quantity,
                    'side': order.side.value
                })

                # Handle bracket order logic
                self._handle_bracket_order_fill(order)

                # Handle OCO order logic
                self._handle_oco_order_fill(order)

        return triggered

    def _handle_bracket_order_fill(self, filled_order: Order):
        """Handle bracket order logic when entry order fills"""
        if 'bracket_id' not in filled_order.metadata:
            return

        bracket_id = filled_order.metadata['bracket_id']
        if bracket_id not in self.bracket_orders:
            return

        bracket = self.bracket_orders[bracket_id]

        if filled_order.metadata.get('bracket_type') == 'entry':
            # Entry filled, activate stop loss and take profit
            bracket['status'] = 'active'
            logger.info(f"Activated bracket order {bracket_id}")

        elif filled_order.metadata.get('bracket_type') in ['stop_loss', 'take_profit']:
            # Exit order filled, cancel remaining orders
            self._cancel_bracket_orders(bracket_id, exclude_order=filled_order.order_id)
            bracket['status'] = 'closed'
            logger.info(f"Closed bracket order {bracket_id}")

    def _handle_oco_order_fill(self, filled_order: Order):
        """Handle OCO order logic when one order fills"""
        if 'oco_id' not in filled_order.metadata:
            return

        oco_id = filled_order.metadata['oco_id']
        if oco_id not in self.oco_orders:
            return

        oco_group = self.oco_orders[oco_id]

        # Cancel all other orders in the OCO group
        for order_id in oco_group['orders']:
            if order_id != filled_order.order_id:
                if order_id in self.active_orders:
                    self.active_orders[order_id].status = OrderStatus.CANCELLED

        oco_group['status'] = 'closed'
        logger.info(f"Closed OCO order {oco_id}")

    def _cancel_bracket_orders(self, bracket_id: str, exclude_order: str = None):
        """Cancel all orders in a bracket except the specified one"""
        if bracket_id not in self.bracket_orders:
            return

        bracket = self.bracket_orders[bracket_id]

        for order_type, order in bracket.items():
            if order_type in ['entry', 'stop_loss', 'take_profit']:
                if order.order_id != exclude_order and order.order_id in self.active_orders:
                    self.active_orders[order.order_id].status = OrderStatus.CANCELLED

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a specific order"""
        if order_id in self.active_orders:
            self.active_orders[order_id].status = OrderStatus.CANCELLED

            # Handle bracket order cancellation
            order = self.active_orders[order_id]
            if 'bracket_id' in order.metadata:
                bracket_id = order.metadata['bracket_id']
                if bracket_id in self.bracket_orders:
                    self._cancel_bracket_orders(bracket_id)

            # Handle OCO cancellation
            if 'oco_id' in order.metadata:
                oco_id = order.metadata['oco_id']
                if oco_id in self.oco_orders:
                    self._cancel_oco_orders(oco_id)

            logger.info(f"Cancelled order {order_id}")
            return True

        return False

    def _cancel_oco_orders(self, oco_id: str):
        """Cancel all orders in an OCO group"""
        if oco_id not in self.oco_orders:
            return

        oco_group = self.oco_orders[oco_id]

        for order_id in oco_group['orders']:
            if order_id in self.active_orders:
                self.active_orders[order_id].status = OrderStatus.CANCELLED

        oco_group['status'] = 'cancelled'

    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get status of a specific order"""
        return self.active_orders.get(order_id)

    def get_active_orders(self, symbol: str = None) -> List[Order]:
        """Get all active orders, optionally filtered by symbol"""
        orders = [order for order in self.active_orders.values()
                 if order.status == OrderStatus.PENDING]

        if symbol:
            orders = [order for order in orders if order.symbol == symbol]

        return orders

    def get_bracket_status(self, bracket_id: str) -> Optional[Dict]:
        """Get status of a bracket order"""
        return self.bracket_orders.get(bracket_id)

    def get_oco_status(self, oco_id: str) -> Optional[Dict]:
        """Get status of an OCO order"""
        return self.oco_orders.get(oco_id)

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get summary of all active orders and positions"""
        summary = {
            'active_orders': len(self.get_active_orders()),
            'bracket_orders': len([b for b in self.bracket_orders.values() if b['status'] in ['pending', 'active']]),
            'oco_orders': len([o for o in self.oco_orders.values() if o['status'] == 'pending']),
            'trailing_stops': len([t for t in self.trailing_stops.values() if t['status'] in ['pending', 'active']]),
            'by_symbol': {}
        }

        # Group by symbol
        for order in self.active_orders.values():
            if order.status == OrderStatus.PENDING:
                if order.symbol not in summary['by_symbol']:
                    summary['by_symbol'][order.symbol] = {'buy': 0, 'sell': 0}
                summary['by_symbol'][order.symbol][order.side.value] += 1

        return summary


# Global instance
advanced_order_manager = AdvancedOrderManager()


def create_bracket_order(symbol: str, side: str, entry_price: float,
                        quantity: float, stop_loss: float, take_profit: float,
                        trailing_stop: bool = False, trailing_distance: float = 0.0) -> Dict[str, str]:
    """Convenience function for creating bracket orders"""
    # Validate inputs
    if not symbol or not symbol.strip():
        raise ValueError("Symbol cannot be empty")

    if side.upper() not in ['BUY', 'SELL']:
        raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")

    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}. Must be positive")

    if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
        raise ValueError("Prices must be positive")

    # Validate order logic
    if side.upper() == 'BUY':
        if stop_loss >= entry_price:
            raise ValueError(f"BUY order stop loss ({stop_loss}) must be below entry price ({entry_price})")
        if take_profit <= entry_price:
            raise ValueError(f"BUY order take profit ({take_profit}) must be above entry price ({entry_price})")
    else:  # SELL
        if stop_loss <= entry_price:
            raise ValueError(f"SELL order stop loss ({stop_loss}) must be above entry price ({entry_price})")
        if take_profit >= entry_price:
            raise ValueError(f"SELL order take profit ({take_profit}) must be below entry price ({entry_price})")

    return advanced_order_manager.create_bracket_order(
        symbol, OrderSide(side.lower()), entry_price, quantity,
        stop_loss, take_profit, trailing_stop, trailing_distance
    )


def create_oco_order(symbol: str, quantity: float, orders: List[Dict]) -> Dict[str, str]:
    """Convenience function for creating OCO orders"""
    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}. Must be positive")

    if len(orders) < 2:
        raise ValueError("OCO orders must have at least 2 order specifications")

    # Validate each order
    for order_spec in orders:
        if 'side' not in order_spec or order_spec['side'].upper() not in ['BUY', 'SELL']:
            raise ValueError(f"Invalid or missing side in order spec: {order_spec}")
        if 'type' not in order_spec or order_spec['type'].lower() not in ['limit', 'stop']:
            raise ValueError(f"Invalid or missing type in order spec: {order_spec}")
        if order_spec['type'].lower() == 'limit' and 'price' not in order_spec:
            raise ValueError(f"Limit order missing price: {order_spec}")
        if order_spec['type'].lower() == 'stop' and 'stop_price' not in order_spec:
            raise ValueError(f"Stop order missing stop_price: {order_spec}")

    return advanced_order_manager.create_oco_order(symbol, quantity, orders)


def create_trailing_stop(symbol: str, side: str, quantity: float,
                        trailing_distance: float, activation_price: Optional[float] = None) -> str:
    """Convenience function for creating trailing stops"""
    if side.upper() not in ['BUY', 'SELL']:
        raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")

    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}. Must be positive")

    if trailing_distance <= 0:
        raise ValueError(f"Invalid trailing distance: {trailing_distance}. Must be positive")

    if activation_price is not None and activation_price <= 0:
        raise ValueError(f"Invalid activation price: {activation_price}. Must be positive")

    return advanced_order_manager.create_trailing_stop(
        symbol, OrderSide(side.lower()), quantity, trailing_distance, activation_price
    )


def update_price_feed(symbol: str, price: float) -> List[Dict[str, Any]]:
    """Update all orders with new price data"""
    return advanced_order_manager.update_price(symbol, price)


def cancel_order(order_id: str) -> bool:
    """Cancel a specific order"""
    return advanced_order_manager.cancel_order(order_id)


def get_portfolio_summary() -> Dict[str, Any]:
    """Get portfolio summary"""
    return advanced_order_manager.get_portfolio_summary()


if __name__ == "__main__":
    # Example usage
    print("Advanced Order Manager Demo")

    # Create a bracket order
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
    print(f"Created bracket order: {bracket}")

    # Create an OCO order
    oco = create_oco_order(
        symbol="GBPUSD",
        quantity=500,
        orders=[
            {'side': 'SELL', 'price': 1.2750, 'type': 'limit'},
            {'side': 'SELL', 'stop_price': 1.2650, 'type': 'stop'}
        ]
    )
    print(f"Created OCO order: {oco}")

    # Create trailing stop
    trailing = create_trailing_stop(
        symbol="BTC",
        side="SELL",
        quantity=0.1,
        trailing_distance=1000,
        activation_price=45000
    )
    print(f"Created trailing stop: {trailing}")

    # Simulate price updates
    print("\nSimulating price updates...")
    prices = [1.0850, 1.0860, 1.0870, 1.0900, 1.0850, 1.0800]

    for price in prices:
        triggered = update_price_feed("EURUSD", price)
        if triggered:
            print(f"Price {price}: {triggered}")

    print(f"\nPortfolio Summary: {get_portfolio_summary()}")


# Global instance
advanced_order_manager = AdvancedOrderManager()


def create_bracket_order(symbol: str, side: str, entry_price: float,
                        quantity: float, stop_loss: float, take_profit: float,
                        trailing_stop: bool = False, trailing_distance: float = 0.0) -> Dict[str, str]:
    """Convenience function for creating bracket orders"""
    # Validate inputs
    if not symbol or not symbol.strip():
        raise ValueError("Symbol cannot be empty")

    if side.upper() not in ['BUY', 'SELL']:
        raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")

    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}. Must be positive")

    if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
        raise ValueError("Prices must be positive")

    # Validate order logic
    if side.upper() == 'BUY':
        if stop_loss >= entry_price:
            raise ValueError(f"BUY order stop loss ({stop_loss}) must be below entry price ({entry_price})")
        if take_profit <= entry_price:
            raise ValueError(f"BUY order take profit ({take_profit}) must be above entry price ({entry_price})")
    else:  # SELL
        if stop_loss <= entry_price:
            raise ValueError(f"SELL order stop loss ({stop_loss}) must be above entry price ({entry_price})")
        if take_profit >= entry_price:
            raise ValueError(f"SELL order take profit ({take_profit}) must be below entry price ({entry_price})")

    return advanced_order_manager.create_bracket_order(
        symbol, OrderSide(side.lower()), entry_price, quantity,
        stop_loss, take_profit, trailing_stop, trailing_distance
    )


def create_oco_order(symbol: str, quantity: float, orders: List[Dict]) -> Dict[str, str]:
    """Convenience function for creating OCO orders"""
    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}. Must be positive")

    if len(orders) < 2:
        raise ValueError("OCO orders must have at least 2 order specifications")

    # Validate each order
    for order_spec in orders:
        if 'side' not in order_spec or order_spec['side'].upper() not in ['BUY', 'SELL']:
            raise ValueError(f"Invalid or missing side in order spec: {order_spec}")
        if 'type' not in order_spec or order_spec['type'].lower() not in ['limit', 'stop']:
            raise ValueError(f"Invalid or missing type in order spec: {order_spec}")
        if order_spec['type'].lower() == 'limit' and 'price' not in order_spec:
            raise ValueError(f"Limit order missing price: {order_spec}")
        if order_spec['type'].lower() == 'stop' and 'stop_price' not in order_spec:
            raise ValueError(f"Stop order missing stop_price: {order_spec}")

    return advanced_order_manager.create_oco_order(symbol, quantity, orders)


def create_trailing_stop(symbol: str, side: str, quantity: float,
                        trailing_distance: float, activation_price: Optional[float] = None) -> str:
    """Convenience function for creating trailing stops"""
    if side.upper() not in ['BUY', 'SELL']:
        raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")

    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}. Must be positive")

    if trailing_distance <= 0:
        raise ValueError(f"Invalid trailing distance: {trailing_distance}. Must be positive")

    if activation_price is not None and activation_price <= 0:
        raise ValueError(f"Invalid activation price: {activation_price}. Must be positive")

    return advanced_order_manager.create_trailing_stop(
        symbol, OrderSide(side.lower()), quantity, trailing_distance, activation_price
    )


def update_price_feed(symbol: str, price: float) -> List[Dict[str, Any]]:
    """Update all orders with new price data"""
    if price <= 0:
        raise ValueError(f"Invalid price: {price}. Must be positive")

    return advanced_order_manager.update_price(symbol, price)


def cancel_order(order_id: str) -> bool:
    """Cancel a specific order"""
    return advanced_order_manager.cancel_order(order_id)


def get_portfolio_summary() -> Dict[str, Any]:
    """Get portfolio summary"""
    return advanced_order_manager.get_portfolio_summary()


def get_order_status(order_id: str):
    """Get status of a specific order"""
    return advanced_order_manager.get_order_status(order_id)


def get_active_orders(symbol: str = None):
    """Get all active orders"""
    return advanced_order_manager.get_active_orders(symbol)
