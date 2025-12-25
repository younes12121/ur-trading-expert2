"""
Institutional-Grade Backtesting Engine
Simulates trading strategy on historical data with realistic execution modeling
PERFORMANCE OPTIMIZED VERSION
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Generator
from dataclasses import dataclass, field
from enum import Enum
import warnings
import time
import logging
from numba import jit, njit
from functools import lru_cache
from global_error_learning import global_error_manager, record_error

logger = logging.getLogger(__name__)

# Performance-optimized calculation functions
@jit(nopython=True)
def calculate_atr_numba(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> np.ndarray:
    """Numba-optimized ATR calculation"""
    n = len(high)
    atr = np.zeros(n)
    tr = np.zeros(n)

    # Calculate True Range
    for i in range(n):
        if i == 0:
            tr[i] = high[i] - low[i]
        else:
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i-1]),
                abs(low[i] - close[i-1])
            )

    # Calculate ATR using rolling mean
    for i in range(period-1, n):
        if i == period-1:
            atr[i] = np.mean(tr[:period])
        else:
            atr[i] = (atr[i-1] * (period-1) + tr[i]) / period

    return atr

@jit(nopython=True)
def calculate_volatility_numba(returns: np.ndarray, lookback: int) -> np.ndarray:
    """Numba-optimized volatility calculation"""
    n = len(returns)
    volatility = np.zeros(n)

    for i in range(lookback-1, n):
        window = returns[max(0, i-lookback+1):i+1]
        volatility[i] = np.std(window) if len(window) > 0 else 0.0

    return volatility

@jit(nopython=True)
def vectorized_slippage_calculation(price: float, direction: int, volatility: float,
                                   slippage_base: float, bid_ask_spread: float) -> tuple:
    """Vectorized slippage calculation"""
    # Bid/ask spread
    spread_half = bid_ask_spread / 2
    if direction == 1:  # BUY
        spread_price = price * (1 + spread_half)
    else:  # SELL
        spread_price = price * (1 - spread_half)

    # Volatility-adjusted slippage
    volatility_multiplier = 1.0 + (volatility * 10)
    slippage_pct = slippage_base * volatility_multiplier

    if direction == 1:  # BUY
        final_price = spread_price * (1 + slippage_pct)
        slippage_amount = final_price - price
    else:  # SELL
        final_price = spread_price * (1 - slippage_pct)
        slippage_amount = price - final_price

    return final_price, slippage_amount


class ExecutionPriority(Enum):
    """Order execution priority"""
    STOP_LOSS_FIRST = "stop_loss_first"
    TAKE_PROFIT_FIRST = "take_profit_first"
    FIFO = "fifo"


class PositionMode(Enum):
    """Position netting mode"""
    NETTING = "netting"  # Net positions (long + short = net)
    HEDGING = "hedging"  # Allow long and short simultaneously


@dataclass
class Trade:
    """Represents a single trade with enhanced tracking"""
    entry_time: datetime
    entry_price: float
    direction: str  # 'BUY' or 'SELL'
    lot_size: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    symbol: str = "UNKNOWN"
    
    # Exit information (filled when trade closes)
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None  # 'SL', 'TP1', 'TP2', 'MANUAL', 'END'
    pnl: float = 0.0
    pnl_pct: float = 0.0
    duration_hours: float = 0.0
    status: str = 'OPEN'  # 'OPEN', 'CLOSED'
    
    # For partial closes
    remaining_size: float = field(init=False)
    tp1_hit: bool = False
    tp2_hit: bool = False
    
    # Fee tracking
    entry_fee: float = 0.0
    exit_fee: float = 0.0
    total_fees: float = 0.0
    
    # Slippage tracking
    entry_slippage: float = 0.0
    exit_slippage: float = 0.0
    
    # Scenario tags for attribution
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Realized vs unrealized P&L
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    
    def __post_init__(self):
        self.remaining_size = self.lot_size
        self.total_fees = self.entry_fee
    
    def close_partial(self, exit_time: datetime, exit_price: float, 
                     close_pct: float, reason: str, exit_fee: float = 0.0) -> float:
        """Close a portion of the trade"""
        close_size = self.lot_size * close_pct
        
        if self.direction == 'BUY':
            pnl = close_size * (exit_price - self.entry_price)
        else:  # SELL
            pnl = close_size * (self.entry_price - exit_price)
        
        realized_pnl = pnl - exit_fee
        self.remaining_size -= close_size
        self.realized_pnl += realized_pnl
        self.pnl += realized_pnl
        self.exit_fee += exit_fee
        self.total_fees += exit_fee
        
        if reason == 'TP1':
            self.tp1_hit = True
        elif reason == 'TP2':
            self.tp2_hit = True
        
        return realized_pnl
    
    def close_full(self, exit_time: datetime, exit_price: float, reason: str, exit_fee: float = 0.0):
        """Close the entire trade"""
        if self.remaining_size > 0:
            if self.direction == 'BUY':
                pnl = self.remaining_size * (exit_price - self.entry_price)
            else:
                pnl = self.remaining_size * (self.entry_price - exit_price)
            
            realized_pnl = pnl - exit_fee
            self.realized_pnl += realized_pnl
            self.pnl += realized_pnl
            self.exit_fee += exit_fee
            self.total_fees += exit_fee
        
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_reason = reason
        self.status = 'CLOSED'
        
        if self.entry_price * self.lot_size > 0:
            self.pnl_pct = (self.pnl / (self.entry_price * self.lot_size)) * 100
        
        if self.exit_time and self.entry_time:
            self.duration_hours = (self.exit_time - self.entry_time).total_seconds() / 3600
    
    def update_unrealized_pnl(self, current_price: float):
        """Update unrealized P&L for mark-to-market"""
        if self.status == 'CLOSED':
            self.unrealized_pnl = 0.0
            return
        
        if self.direction == 'BUY':
            self.unrealized_pnl = self.remaining_size * (current_price - self.entry_price)
        else:  # SELL
            self.unrealized_pnl = self.remaining_size * (self.entry_price - current_price)


class BacktestEngine:
    """Institutional-grade backtesting engine with realistic execution modeling"""
    
    def __init__(
        self,
        initial_capital: float = 500,
        risk_per_trade: float = 0.01,
        slippage: float = 0.0005,
        fee: Optional[float] = None,  # Legacy: sets both entry and exit fees
        # Enhanced parameters
        bid_ask_spread: float = 0.0002,  # 0.02% spread
        fee_entry: Optional[float] = None,  # Per-side fees
        fee_exit: Optional[float] = None,
        volatility_lookback: int = 20,  # Periods for volatility calculation
        max_concurrent_trades: int = 1,
        max_positions_per_symbol: int = 1,
        position_mode: PositionMode = PositionMode.NETTING,
        execution_priority: ExecutionPriority = ExecutionPriority.STOP_LOSS_FIRST,
        # Risk limits
        max_daily_loss_pct: Optional[float] = None,  # Stop trading if daily loss exceeds this
        max_drawdown_pct: Optional[float] = None,  # Stop trading if drawdown exceeds this
        max_leverage: Optional[float] = None,  # Maximum leverage
        per_asset_cap_pct: Optional[float] = None,  # Max capital per asset
        # Risk-based sizing
        use_atr_sizing: bool = False,
        atr_period: int = 14,
        volatility_factor: float = 1.0,  # Multiplier for volatility-based sizing
        # Random seed for reproducibility
        random_seed: Optional[int] = None
    ):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.cash = initial_capital  # Available cash
        self.reserved_margin = 0.0  # Margin reserved for open positions
        self.risk_per_trade = risk_per_trade
        
        # Execution parameters
        self.slippage_base = slippage
        self.bid_ask_spread = bid_ask_spread
        
        # Backward compatibility: if fee is provided, use it for both entry and exit
        if fee is not None:
            self.fee_entry = fee_entry if fee_entry is not None else fee
            self.fee_exit = fee_exit if fee_exit is not None else fee
        else:
            # Default fees if neither fee nor fee_entry/fee_exit provided
            default_fee = 0.001
            self.fee_entry = fee_entry if fee_entry is not None else default_fee
            self.fee_exit = fee_exit if fee_exit is not None else default_fee
        self.volatility_lookback = volatility_lookback
        self.execution_priority = execution_priority
        
        # Position management
        self.max_concurrent_trades = max_concurrent_trades
        self.max_positions_per_symbol = max_positions_per_symbol
        self.position_mode = position_mode
        
        # Risk limits
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.max_leverage = max_leverage
        self.per_asset_cap_pct = per_asset_cap_pct
        
        # Risk-based sizing
        self.use_atr_sizing = use_atr_sizing
        self.atr_period = atr_period
        self.volatility_factor = volatility_factor
        
        # State tracking
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.positions_by_symbol: Dict[str, List[Trade]] = {}  # Track positions per symbol
        self.equity_curve = []
        self.balance_history = []
        self.daily_pnl = {}  # Track daily P&L for daily loss limits
        self.peak_equity = initial_capital  # For drawdown calculation
        self.trading_enabled = True  # Can be disabled by risk limits
        
        # Random seed for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)

        # Performance optimization caches
        self._precomputed_data = None
        self._volatility_cache = {}
        self._atr_cache = {}
        self._performance_mode = False  # Toggle for performance optimizations
    
    def calculate_atr(self, data: pd.DataFrame, period: int = None) -> pd.Series:
        """Calculate Average True Range (optimized version)"""
        if period is None:
            period = self.atr_period

        if len(data) < period + 1:
            return pd.Series(index=data.index, data=0.0)

        # Use optimized Numba version
        high = data['high'].values
        low = data['low'].values
        close = data['close'].values

        atr_values = calculate_atr_numba(high, low, close, period)

        return pd.Series(atr_values, index=data.index)
    
    def precompute_data(self, data: pd.DataFrame):
        """Pre-compute expensive operations for performance optimization"""
        if self._performance_mode:
            logger.info("Pre-computing data for performance optimization...")

            # Pre-compute returns for volatility calculations
            returns = data['close'].pct_change().fillna(0)

            # Pre-compute volatility for each possible window
            vol_lookback = self.volatility_lookback
            self._precomputed_data = {
                'returns': returns.values,
                'high': data['high'].values,
                'low': data['low'].values,
                'close': data['close'].values,
                'volatility': calculate_volatility_numba(returns.values, vol_lookback),
                'atr': calculate_atr_numba(data['high'].values, data['low'].values,
                                         data['close'].values, self.atr_period),
                'data_index': data.index
            }

    def calculate_volatility(self, data: pd.DataFrame, lookback: int = None) -> float:
        """Calculate realized volatility (optimized version)"""
        if lookback is None:
            lookback = self.volatility_lookback

        if len(data) < lookback + 1:
            return 0.001  # Default low volatility

        # Use optimized Numba version
        returns = data['close'].pct_change().fillna(0).values
        volatility_array = calculate_volatility_numba(returns, lookback)
        volatility = volatility_array[-1] if len(volatility_array) > 0 else 0.001

        return max(volatility, 0.0001)  # Minimum volatility
    
    def calculate_adaptive_slippage(self, price: float, volatility: float, 
                                   direction: str, is_market_order: bool = True) -> float:
        """Calculate volatility-aware slippage"""
        base_slippage = self.slippage_base
        
        # Increase slippage with volatility
        volatility_multiplier = 1.0 + (volatility * 10)  # Scale volatility impact
        
        # Market orders have more slippage than limit orders
        order_type_multiplier = 1.5 if is_market_order else 0.5
        
        adaptive_slippage = base_slippage * volatility_multiplier * order_type_multiplier
        
        return adaptive_slippage
    
    def apply_bid_ask_spread(self, price: float, direction: str) -> float:
        """Apply bid/ask spread to price"""
        spread_half = self.bid_ask_spread / 2
        
        if direction == 'BUY':
            # Buying at ask price (higher)
            return price * (1 + spread_half)
        else:  # SELL
            # Selling at bid price (lower)
            return price * (1 - spread_half)
    
    def apply_slippage(self, price: float, direction: str, volatility: float = 0.001,
                      is_market_order: bool = True) -> tuple:
        """Apply slippage and spread to entry/exit price, returns (price, slippage_amount) - optimized"""
        # Convert direction to int for numba
        direction_int = 1 if direction == 'BUY' else -1

        # Use optimized slippage calculation
        order_type_multiplier = 1.5 if is_market_order else 0.5
        slippage_base = self.slippage_base * order_type_multiplier

        return vectorized_slippage_calculation(price, direction_int, volatility,
                                             slippage_base, self.bid_ask_spread)
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                               data: pd.DataFrame = None, symbol: str = "UNKNOWN") -> float:
        """Calculate position size based on risk, with optional ATR-based sizing"""
        risk_amount = self.capital * self.risk_per_trade
        
        # Check per-asset capital cap
        if self.per_asset_cap_pct is not None:
            asset_cap = self.capital * self.per_asset_cap_pct
            risk_amount = min(risk_amount, asset_cap)
        
        # Calculate stop distance
        if self.use_atr_sizing and data is not None and len(data) >= self.atr_period:
            atr = self.calculate_atr(data, self.atr_period)
            if len(atr) > 0 and not pd.isna(atr.iloc[-1]) and atr.iloc[-1] > 0:
                stop_distance = atr.iloc[-1] * self.volatility_factor
            else:
                stop_distance = abs(entry_price - stop_loss)
        else:
            stop_distance = abs(entry_price - stop_loss)
        
        if stop_distance == 0:
            return 0
        
        lot_size = risk_amount / stop_distance
        
        # Check leverage limits
        if self.max_leverage is not None:
            position_value = lot_size * entry_price
            max_position_value = self.capital * self.max_leverage
            if position_value > max_position_value:
                lot_size = max_position_value / entry_price
        
        return round(lot_size, 4)
    
    def calculate_fee(self, price: float, lot_size: float, is_entry: bool = True) -> float:
        """Calculate trading fee (per-side)"""
        fee_rate = self.fee_entry if is_entry else self.fee_exit
        return price * lot_size * fee_rate
    
    def check_risk_limits(self, current_time: datetime, current_equity: float) -> bool:
        """Check if risk limits are violated, returns True if trading should continue"""
        if not self.trading_enabled:
            return False
        
        # Check daily loss limit
        if self.max_daily_loss_pct is not None:
            date_key = current_time.date()
            if date_key not in self.daily_pnl:
                self.daily_pnl[date_key] = 0.0
            
            daily_loss_pct = abs(self.daily_pnl[date_key]) / self.initial_capital * 100
            if daily_loss_pct >= self.max_daily_loss_pct:
                if self.trading_enabled:
                    warnings.warn(f"Daily loss limit ({self.max_daily_loss_pct}%) reached. Stopping trading.")
                    self.trading_enabled = False
                return False
        
        # Check max drawdown
        if self.max_drawdown_pct is not None:
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity
            
            drawdown = (self.peak_equity - current_equity) / self.peak_equity * 100
            if drawdown >= self.max_drawdown_pct:
                if self.trading_enabled:
                    warnings.warn(f"Max drawdown limit ({self.max_drawdown_pct}%) reached. Stopping trading.")
                    self.trading_enabled = False
                return False
        
        return True
    
    def get_positions_by_symbol(self, symbol: str) -> List[Trade]:
        """Get all open positions for a symbol"""
        return [t for t in self.open_trades if t.symbol == symbol]
    
    def can_open_trade(self, symbol: str) -> bool:
        """Check if we can open a new trade"""
        if not self.trading_enabled:
            return False
        
        if len(self.open_trades) >= self.max_concurrent_trades:
            return False
        
        symbol_positions = self.get_positions_by_symbol(symbol)
        if len(symbol_positions) >= self.max_positions_per_symbol:
            return False
        
        return True
    
    def open_trade(self, signal: Dict, current_time: datetime, 
                  data: pd.DataFrame = None, tags: Dict[str, str] = None) -> Optional[Trade]:
        """Open a new trade based on signal"""
        if signal['direction'] == 'HOLD':
            return None
        
        symbol = signal.get('symbol', 'UNKNOWN')
        
        if not self.can_open_trade(symbol):
            return None
        
        # Calculate position size
        lot_size = self.calculate_position_size(
            signal['entry_price'],
            signal['stop_loss'],
            data,
            symbol
        )
        
        if lot_size <= 0:
            return None
        
        # Calculate volatility for adaptive slippage
        volatility = 0.001
        if data is not None and len(data) >= self.volatility_lookback:
            volatility = self.calculate_volatility(data, self.volatility_lookback)
        
        # Apply slippage to entry
        entry_price, entry_slippage = self.apply_slippage(
            signal['entry_price'], 
            signal['direction'],
            volatility,
            is_market_order=True
        )
        
        # Calculate fees
        entry_fee = self.calculate_fee(entry_price, lot_size, is_entry=True)
        
        # Check if we have enough capital
        position_value = entry_price * lot_size
        required_capital = position_value + entry_fee
        
        if self.cash < required_capital:
            return None  # Insufficient capital
        
        # Create trade
        trade = Trade(
            entry_time=current_time,
            entry_price=entry_price,
            direction=signal['direction'],
            lot_size=lot_size,
            stop_loss=signal['stop_loss'],
            take_profit_1=signal.get('take_profit_1', signal['entry_price'] * 1.01),
            take_profit_2=signal.get('take_profit_2', signal['entry_price'] * 1.02),
            symbol=symbol,
            entry_fee=entry_fee,
            entry_slippage=entry_slippage,
            tags=tags or {}
        )
        
        # Deduct entry fee and reserve margin
        self.cash -= entry_fee
        self.capital -= entry_fee
        self.reserved_margin += position_value
        trade.pnl -= entry_fee
        trade.realized_pnl -= entry_fee
        
        self.open_trades.append(trade)
        self.trades.append(trade)
        
        # Track positions by symbol
        if symbol not in self.positions_by_symbol:
            self.positions_by_symbol[symbol] = []
        self.positions_by_symbol[symbol].append(trade)
        
        return trade
    
    def check_exits(self, candle: pd.Series, current_time: datetime, 
                   data: pd.DataFrame = None, volatility: float = 0.001):
        """Check if any open trades should be closed with proper execution priority"""
        trades_to_close = []
        
        # Sort trades by priority if needed
        if self.execution_priority == ExecutionPriority.STOP_LOSS_FIRST:
            # Check stop losses first
            priority_trades = [t for t in self.open_trades if self._check_stop_loss(t, candle, current_time, data, volatility)]
            other_trades = [t for t in self.open_trades if t not in priority_trades]
            sorted_trades = priority_trades + other_trades
        else:
            sorted_trades = self.open_trades
        
        for trade in sorted_trades:
            high = candle['high']
            low = candle['low']
            close = candle['close']
            
            if trade.direction == 'BUY':
                # Check stop loss (highest priority for risk management)
                if low <= trade.stop_loss:
                    exit_price, exit_slippage = self.apply_slippage(trade.stop_loss, 'SELL', volatility)
                    exit_fee = self.calculate_fee(exit_price, trade.remaining_size, is_entry=False)
                    trade.exit_slippage = exit_slippage
                    trade.close_full(current_time, exit_price, 'SL', exit_fee)
                    trades_to_close.append(trade)
                    continue
                
                # Check TP1
                if not trade.tp1_hit and high >= trade.take_profit_1:
                    exit_price, exit_slippage = self.apply_slippage(trade.take_profit_1, 'SELL', volatility)
                    exit_fee = self.calculate_fee(exit_price, trade.lot_size * 0.5, is_entry=False)
                    trade.exit_slippage = exit_slippage
                    pnl = trade.close_partial(current_time, exit_price, 0.5, 'TP1', exit_fee)
                    self.capital += pnl
                    self.cash += pnl
                    self.reserved_margin -= trade.lot_size * 0.5 * exit_price
                    # Move SL to breakeven
                    trade.stop_loss = trade.entry_price
                
                # Check TP2
                if trade.tp1_hit and not trade.tp2_hit and high >= trade.take_profit_2:
                    exit_price, exit_slippage = self.apply_slippage(trade.take_profit_2, 'SELL', volatility)
                    exit_fee = self.calculate_fee(exit_price, trade.remaining_size, is_entry=False)
                    trade.exit_slippage = exit_slippage
                    trade.close_full(current_time, exit_price, 'TP2', exit_fee)
                    trades_to_close.append(trade)
            
            else:  # SELL
                # Check stop loss
                if high >= trade.stop_loss:
                    exit_price, exit_slippage = self.apply_slippage(trade.stop_loss, 'BUY', volatility)
                    exit_fee = self.calculate_fee(exit_price, trade.remaining_size, is_entry=False)
                    trade.exit_slippage = exit_slippage
                    trade.close_full(current_time, exit_price, 'SL', exit_fee)
                    trades_to_close.append(trade)
                    continue
                
                # Check TP1
                if not trade.tp1_hit and low <= trade.take_profit_1:
                    exit_price, exit_slippage = self.apply_slippage(trade.take_profit_1, 'BUY', volatility)
                    exit_fee = self.calculate_fee(exit_price, trade.lot_size * 0.5, is_entry=False)
                    trade.exit_slippage = exit_slippage
                    pnl = trade.close_partial(current_time, exit_price, 0.5, 'TP1', exit_fee)
                    self.capital += pnl
                    self.cash += pnl
                    self.reserved_margin -= trade.lot_size * 0.5 * exit_price
                    trade.stop_loss = trade.entry_price
                
                # Check TP2
                if trade.tp1_hit and not trade.tp2_hit and low <= trade.take_profit_2:
                    exit_price, exit_slippage = self.apply_slippage(trade.take_profit_2, 'BUY', volatility)
                    exit_fee = self.calculate_fee(exit_price, trade.remaining_size, is_entry=False)
                    trade.exit_slippage = exit_slippage
                    trade.close_full(current_time, exit_price, 'TP2', exit_fee)
                    trades_to_close.append(trade)
        
        # Remove closed trades from open trades
        for trade in trades_to_close:
            if trade in self.open_trades:
                self.open_trades.remove(trade)
                # Add final P&L to capital
                exit_fee = self.calculate_fee(trade.exit_price, trade.remaining_size, is_entry=False)
                final_pnl = trade.pnl
                self.capital += final_pnl
                self.cash += final_pnl
                self.reserved_margin -= trade.remaining_size * trade.exit_price
                
                # Update daily P&L
                date_key = current_time.date()
                if date_key not in self.daily_pnl:
                    self.daily_pnl[date_key] = 0.0
                self.daily_pnl[date_key] += final_pnl
                
                # Remove from symbol tracking
                if trade.symbol in self.positions_by_symbol:
                    if trade in self.positions_by_symbol[trade.symbol]:
                        self.positions_by_symbol[trade.symbol].remove(trade)
    
    def _check_stop_loss(self, trade: Trade, candle: pd.Series, 
                        current_time: datetime, data: pd.DataFrame = None,
                        volatility: float = 0.001) -> bool:
        """Check if stop loss would be hit (for priority sorting)"""
        if trade.direction == 'BUY':
            return candle['low'] <= trade.stop_loss
        else:
            return candle['high'] >= trade.stop_loss
    
    def run_backtest(self, data: pd.DataFrame, strategy_func: Callable,
                    verbose: bool = True, tags_func: Optional[Callable] = None,
                    performance_mode: bool = False):
        """
        Run backtest on historical data with error learning

        Args:
            data: DataFrame with OHLCV data (must have 'open', 'high', 'low', 'close', 'volume')
            strategy_func: Function that generates trading signals
                          Signature: (data: pd.DataFrame) -> Dict with keys:
                          'direction', 'entry_price', 'stop_loss', 'take_profit_1', 'take_profit_2', 'symbol'
            verbose: Print progress
            tags_func: Optional function to add scenario tags to trades
                      Signature: (data: pd.DataFrame, timestamp: datetime) -> Dict[str, str]
            performance_mode: Enable performance optimizations (disables some logging)
        """
        start_time = time.time()

        operation_context = {
            'operation_type': 'run_backtest',
            'strategy_type': 'custom',  # Could be enhanced to detect strategy type
            'timeframe': 'unknown',     # Could be detected from data
            'data_points': len(data),
            'computation_time': 0,      # Will be updated
            'parallel_jobs': 1,         # Could be enhanced for parallel execution
            'system_load': 0.5,
            'memory_usage': 0.5
        }

        # Predict error likelihood
        error_prediction = global_error_manager.predict_error_likelihood('backtest_engine', operation_context)

        if not error_prediction['should_attempt']:
            logger.warning(f"[BACKTEST_ENGINE] Avoiding backtest due to high error risk: {error_prediction['error_probability']:.1%}")
            if verbose:
                print("⚠️ Backtest cancelled due to high error risk prediction")
                print(f"   Alternative suggestions: {error_prediction['alternative_suggestions']}")

            record_error('backtest_engine', operation_context, had_error=False,
                        error_details="Proactively avoided due to error prediction",
                        success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']},
                        execution_time=time.time() - start_time)

            return self._create_error_result("Backtest cancelled due to high error risk prediction")

        self._performance_mode = performance_mode
        success = False
        error_details = None

        # Pre-compute expensive operations if in performance mode
        if performance_mode:
            self.precompute_data(data)

        try:
            if verbose and not performance_mode:
                print("=" * 70)
                print("🔄 Running Enhanced Backtest...")
                print("=" * 70)
                print(f"Initial Capital: ${self.initial_capital:,.2f}")
                print(f"Risk per Trade: {self.risk_per_trade * 100}%")
                print(f"Data Period: {data.index[0]} to {data.index[-1]}")
                print(f"Total Candles: {len(data)}")
                print(f"Max Concurrent Trades: {self.max_concurrent_trades}")
                print(f"Position Mode: {self.position_mode.value}")
                print(f"Execution Priority: {self.execution_priority.value}")
                if self.max_daily_loss_pct:
                    print(f"Max Daily Loss: {self.max_daily_loss_pct}%")
                if self.max_drawdown_pct:
                    print(f"Max Drawdown: {self.max_drawdown_pct}%")
                print()

            # Reset state
            self.peak_equity = self.initial_capital
            self.daily_pnl = {}
            self.trading_enabled = True

            # Use optimized iteration
            if performance_mode and self._precomputed_data is not None:
                # Performance mode: pre-computed data available
                volatility_array = self._precomputed_data['volatility']

                for i, (timestamp, candle) in enumerate(data.iterrows()):
                    # Calculate current equity (mark-to-market)
                    current_equity = self.capital
                    for trade in self.open_trades:
                        trade.update_unrealized_pnl(candle['close'])
                        current_equity += trade.unrealized_pnl

                    # Check risk limits
                    if not self.check_risk_limits(timestamp, current_equity):
                        # Still update equity curve but don't open new trades
                        self.equity_curve.append({
                            'timestamp': timestamp,
                            'equity': current_equity,
                            'capital': self.capital,
                            'cash': self.cash,
                            'reserved_margin': self.reserved_margin,
                            'open_trades': len(self.open_trades),
                            'drawdown_pct': (self.peak_equity - current_equity) / self.peak_equity * 100 if self.peak_equity > 0 else 0
                        })
                        continue
            
            # Calculate volatility for adaptive slippage (optimized)
            if performance_mode and self._precomputed_data is not None:
                volatility = volatility_array[i] if i < len(volatility_array) else 0.001
            else:
                volatility = 0.001
                if i >= self.volatility_lookback:
                    volatility = self.calculate_volatility(data.iloc[:i+1], self.volatility_lookback)
            
            # Check exits for open trades (optimized data passing)
            if performance_mode:
                # In performance mode, pass current candle data directly
                self.check_exits(candle, timestamp, None, volatility)
            else:
                self.check_exits(candle, timestamp, data.iloc[:i+1] if i > 0 else data.iloc[:1], volatility)

            # Generate signal
            if self.trading_enabled:
                if performance_mode:
                    # In performance mode, create minimal data slice for strategy
                    historical_data = data.iloc[max(0, i-100):i+1]  # Last 100 candles for context
                else:
                    historical_data = data.iloc[:i+1]
                signal = strategy_func(historical_data)
                
                if signal and signal['direction'] != 'HOLD':
                    # Get tags if function provided
                    tags = None
                    if tags_func:
                        tags = tags_func(historical_data, timestamp)
                    
                    self.open_trade(signal, timestamp, historical_data, tags)
            
            # Record equity
            current_equity = self.capital
            for trade in self.open_trades:
                trade.update_unrealized_pnl(candle['close'])
                current_equity += trade.unrealized_pnl
            
            # Update peak equity
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity
            
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': current_equity,
                'capital': self.capital,
                'cash': self.cash,
                'reserved_margin': self.reserved_margin,
                'open_trades': len(self.open_trades),
                'drawdown_pct': (self.peak_equity - current_equity) / self.peak_equity * 100 if self.peak_equity > 0 else 0
            })
        
        # Close any remaining open trades at final price
        if self.open_trades:
            final_candle = data.iloc[-1]
            final_time = data.index[-1]
            final_volatility = self.calculate_volatility(data, self.volatility_lookback)
            
            for trade in self.open_trades[:]:
                exit_price, exit_slippage = self.apply_slippage(final_candle['close'], 
                                                                 'SELL' if trade.direction == 'BUY' else 'BUY',
                                                                 final_volatility)
                exit_fee = self.calculate_fee(exit_price, trade.remaining_size, is_entry=False)
                trade.exit_slippage = exit_slippage
                trade.close_full(final_time, exit_price, 'END', exit_fee)
                self.capital += trade.pnl
                self.cash += trade.pnl
                self.reserved_margin -= trade.remaining_size * exit_price
                
                # Update daily P&L
                date_key = final_time.date()
                if date_key not in self.daily_pnl:
                    self.daily_pnl[date_key] = 0.0
                self.daily_pnl[date_key] += trade.pnl
                
                self.open_trades.remove(trade)
                if trade.symbol in self.positions_by_symbol:
                    if trade in self.positions_by_symbol[trade.symbol]:
                        self.positions_by_symbol[trade.symbol].remove(trade)

        success = True
        execution_time = time.time() - start_time

        if verbose:
            self.print_summary()

        # Record successful operation
        record_error('backtest_engine', operation_context, had_error=False,
                    success_metrics={
                        'backtest_completed': True,
                        'trades_executed': len(self.trades),
                        'total_return': self.capital - self.initial_capital,
                        'win_rate': len([t for t in self.trades if t.pnl > 0]) / len(self.trades) if self.trades else 0
                    },
                    execution_time=execution_time)

        except Exception as e:
            error_details = str(e)
            execution_time = time.time() - start_time
            record_error('backtest_engine', operation_context, had_error=True,
                        error_details=error_details,
                        execution_time=execution_time)
            logger.error(f"[BACKTEST_ENGINE] Backtest failed: {error_details}")
            raise
    
    def print_summary(self):
        """Print backtest summary"""
        print("=" * 70)
        print("📊 BACKTEST RESULTS")
        print("=" * 70)
        
        total_trades = len(self.trades)
        if total_trades == 0:
            print("No trades executed")
            return
        
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        win_rate = len(winning_trades) / total_trades * 100
        
        total_pnl = sum(t.pnl for t in self.trades)
        total_fees = sum(t.total_fees for t in self.trades)
        total_slippage = sum(t.entry_slippage + t.exit_slippage for t in self.trades)
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        print(f"Total Trades:        {total_trades}")
        print(f"Winning Trades:      {len(winning_trades)}")
        print(f"Losing Trades:       {len(losing_trades)}")
        print(f"Win Rate:            {win_rate:.1f}%")
        print()
        print(f"Initial Capital:     ${self.initial_capital:,.2f}")
        print(f"Final Capital:       ${self.capital:,.2f}")
        print(f"Total P&L:           ${total_pnl:+,.2f}")
        print(f"Total Return:        {total_return:+.2f}%")
        print(f"Total Fees:          ${total_fees:,.2f}")
        print(f"Total Slippage:      ${total_slippage:,.2f}")
        print()
        print(f"Average Win:         ${avg_win:,.2f}")
        print(f"Average Loss:        ${avg_loss:,.2f}")
        if avg_loss != 0:
            print(f"Profit Factor:       {abs(avg_win / avg_loss):.2f}")
        
        # Drawdown info
        if self.equity_curve:
            equity_values = [e['equity'] for e in self.equity_curve]
            peak = max(equity_values)
            final_equity = equity_values[-1]
            max_dd = min([e['drawdown_pct'] for e in self.equity_curve])
            print(f"Max Drawdown:        {max_dd:.2f}%")
        
        print("=" * 70)
    
    def get_trades_df(self) -> pd.DataFrame:
        """Convert trades to DataFrame with enhanced fields"""
        if not self.trades:
            return pd.DataFrame()
        
        trades_data = []
        for trade in self.trades:
            trades_data.append({
                'entry_time': trade.entry_time,
                'exit_time': trade.exit_time,
                'symbol': trade.symbol,
                'direction': trade.direction,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'lot_size': trade.lot_size,
                'pnl': trade.pnl,
                'realized_pnl': trade.realized_pnl,
                'unrealized_pnl': trade.unrealized_pnl,
                'pnl_pct': trade.pnl_pct,
                'exit_reason': trade.exit_reason,
                'duration_hours': trade.duration_hours,
                'tp1_hit': trade.tp1_hit,
                'tp2_hit': trade.tp2_hit,
                'entry_fee': trade.entry_fee,
                'exit_fee': trade.exit_fee,
                'total_fees': trade.total_fees,
                'entry_slippage': trade.entry_slippage,
                'exit_slippage': trade.exit_slippage,
                **{f'tag_{k}': v for k, v in trade.tags.items()}
            })
        
        return pd.DataFrame(trades_data)
    
    def get_equity_curve_df(self) -> pd.DataFrame:
        """Convert equity curve to DataFrame with drawdown"""
        if not self.equity_curve:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.equity_curve)
        df.set_index('timestamp', inplace=True)
        return df


# Test function
if __name__ == "__main__":
    print("Enhanced backtest engine created successfully!")
    print("Use with historical data and strategy function.")