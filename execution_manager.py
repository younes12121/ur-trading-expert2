"""
Advanced Execution Manager
Implements 5 execution enhancements for maximum performance:
1. Dynamic Entry Optimization
2. Partial Position Scaling
3. Smart Stop Loss Management
4. Time-Based Exit Rules
5. Confluence Confirmation Delay
"""

import time
import logging
from datetime import datetime, timedelta
import config_execution as exec_config
from data_fetcher import BinanceDataFetcher
from global_error_learning import global_error_manager, record_error

logger = logging.getLogger(__name__)


class ExecutionManager:
    """
    Manages advanced execution logic for optimal trade execution
    Target: 90-95% win rate with better R:R
    """
    
    def __init__(self, data_fetcher=None):
        self.data_fetcher = data_fetcher or BinanceDataFetcher()
        self.config = exec_config
    
    # ========================================================================
    # Enhancement 1: Dynamic Entry Optimization
    # ========================================================================
    
    def optimize_entry(self, signal, market_data):
        """
        Find optimal entry price within time window with error learning
        Returns: (optimized_entry_price, should_enter, reason)
        """
        start_time = time.time()
        operation_context = {
            'operation_type': 'optimize_entry',
            'asset_symbol': signal.get('symbol', 'unknown'),
            'position_size': signal.get('position_size', 1.0),
            'market_volatility': market_data.get('volatility', 0.02),
            'spread_width': self._get_spread(market_data) if hasattr(self, '_get_spread') else 0.0001,
            'liquidity_score': market_data.get('liquidity_score', 0.8),
            'system_load': 0.5,  # Placeholder
            'memory_usage': 0.5   # Placeholder
        }

        # Predict error likelihood
        error_prediction = global_error_manager.predict_error_likelihood('execution_manager', operation_context)

        if not error_prediction['should_attempt']:
            logger.warning(f"[EXECUTION_MANAGER] Avoiding entry optimization due to high error risk: {error_prediction['error_probability']:.1%}")
            logger.info(f"[EXECUTION_MANAGER] Alternatives: {error_prediction['alternative_suggestions']}")

            # Record avoidance
            record_error('execution_manager', operation_context, had_error=False,
                        error_details="Proactively avoided due to error prediction",
                        success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']},
                        execution_time=time.time() - start_time)

            return signal['entry_price'], False, f"High error risk detected ({error_prediction['error_probability']:.1%})"

        success = False
        error_details = None

        try:
            signal_price = signal['entry_price']
            direction = signal['direction']

            # Check bid/ask spread
            spread = self._get_spread(market_data)
            if spread > self.config.TIGHT_SPREAD_THRESHOLD:
                reason = f"Spread too wide ({spread*100:.2f}%)"
                success = True  # This is a successful validation, not an error
                record_error('execution_manager', operation_context, had_error=False,
                           success_metrics={'validation_passed': False, 'reason': 'wide_spread'},
                           execution_time=time.time() - start_time)
                return signal_price, False, reason
            
            # Check for pullback opportunity
            current_price = market_data['btc_price']
            price_diff = abs(current_price - signal_price) / signal_price
            
            if direction == 'BUY':
                # For longs, wait for pullback (lower price)
                if current_price < signal_price:
                    pullback_pct = (signal_price - current_price) / signal_price
                    if self.config.PULLBACK_MIN <= pullback_pct <= self.config.PULLBACK_MAX:
                        return current_price, True, f"Good pullback ({pullback_pct*100:.2f}%)"
                    elif pullback_pct > self.config.PULLBACK_MAX:
                        return signal_price, False, f"Pullback too deep ({pullback_pct*100:.2f}%)"
                
            elif direction == 'SELL':
                # For shorts, wait for bounce (higher price)
                if current_price > signal_price:
                    bounce_pct = (current_price - signal_price) / signal_price
                    if self.config.PULLBACK_MIN <= bounce_pct <= self.config.PULLBACK_MAX:
                        return current_price, True, f"Good bounce ({bounce_pct*100:.2f}%)"
                    elif bounce_pct > self.config.PULLBACK_MAX:
                        return signal_price, False, f"Bounce too high ({bounce_pct*100:.2f}%)"
            
            # If no pullback yet, use signal price
            success = True
            record_error('execution_manager', operation_context, had_error=False,
                        success_metrics={'optimization_successful': True, 'used_signal_price': True},
                        execution_time=time.time() - start_time)
            return signal_price, True, "Entry at signal price"

        except Exception as e:
            error_details = str(e)
            record_error('execution_manager', operation_context, had_error=True,
                        error_details=error_details,
                        execution_time=time.time() - start_time)
            return signal['entry_price'], True, f"Optimization failed, using signal price: {error_details}"
    
    def _get_spread(self, market_data):
        """Calculate bid/ask spread"""
        try:
            order_book = self.data_fetcher.get_order_book(limit=5)
            if order_book and order_book['bids'] and order_book['asks']:
                best_bid = order_book['bids'][0][0]
                best_ask = order_book['asks'][0][0]
                spread = (best_ask - best_bid) / best_ask
                return spread
        except:
            pass
        return 0.001  # Default 0.1% if can't fetch
    
    # ========================================================================
    # Enhancement 2: Partial Position Scaling
    # ========================================================================
    
    def calculate_position_sizes(self, total_capital, risk_per_trade, 
                                signal_confidence: float = None, 
                                quality_score: float = None):
        """
        Calculate position sizes for scaled entry with confidence-based adjustment
        
        Args:
            total_capital: Total trading capital
            risk_per_trade: Base risk per trade (e.g., 0.01 for 1%)
            signal_confidence: Signal confidence (0-100)
            quality_score: Signal quality score (0-100)
            
        Returns:
            dict with tranche sizes and confidence adjustments
        """
        # Base risk amount
        base_risk_amount = total_capital * risk_per_trade
        
        # Calculate confidence multiplier (0.5x to 1.5x based on confidence/quality)
        confidence_multiplier = 1.0
        
        if signal_confidence is not None:
            # Confidence: 0-100 -> multiplier: 0.5-1.5
            confidence_multiplier = 0.5 + (signal_confidence / 100) * 1.0
        
        if quality_score is not None:
            # Quality: 0-100 -> multiplier: 0.5-1.5
            quality_multiplier = 0.5 + (quality_score / 100) * 1.0
            # Average the two multipliers
            confidence_multiplier = (confidence_multiplier + quality_multiplier) / 2
        
        # Apply multiplier to risk amount
        adjusted_risk_amount = base_risk_amount * confidence_multiplier
        
        # Calculate tranches
        tranches = {
            'immediate': adjusted_risk_amount * self.config.ENTRY_TRANCHES['immediate'],
            'pullback': adjusted_risk_amount * self.config.ENTRY_TRANCHES['pullback'],
            'confirmation': adjusted_risk_amount * self.config.ENTRY_TRANCHES['confirmation']
        }
        
        return {
            **tranches,
            'base_risk': base_risk_amount,
            'adjusted_risk': adjusted_risk_amount,
            'confidence_multiplier': round(confidence_multiplier, 2),
            'confidence': signal_confidence,
            'quality_score': quality_score
        }
    
    def calculate_exit_targets(self, entry_price, stop_loss, direction):
        """
        Calculate multiple take profit levels
        Returns: dict with TP1, TP2, TP3 prices and percentages
        """
        risk = abs(entry_price - stop_loss)
        
        targets = {}
        for tp_name, tp_config in self.config.EXIT_TARGETS.items():
            rr_ratio = tp_config['rr_ratio']
            percentage = tp_config['percentage']
            
            if direction == 'BUY':
                tp_price = entry_price + (risk * rr_ratio)
            else:  # SELL
                tp_price = entry_price - (risk * rr_ratio)
            
            targets[tp_name] = {
                'price': tp_price,
                'percentage': percentage,
                'rr_ratio': rr_ratio
            }
        
        return targets
    
    # ========================================================================
    # Enhancement 3: Smart Stop Loss Management
    # ========================================================================
    
    def manage_stop_loss(self, position, market_data, targets_hit, 
                        volatility_adjustment: bool = True):
        """
        Dynamically manage stop loss based on targets hit with adaptive adjustments
        
        Args:
            position: Position dictionary
            market_data: Current market data
            targets_hit: List of take profit targets hit
            volatility_adjustment: Whether to adjust based on current volatility
            
        Returns:
            (new_stop_loss, reason)
        """
        entry_price = position['entry_price']
        current_sl = position['stop_loss']
        direction = position['direction']
        current_price = market_data['btc_price']
        
        # Move to breakeven after TP1
        if 'tp1' in targets_hit and self.config.MOVE_SL_TO_BREAKEVEN_AFTER_TP1:
            if direction == 'BUY' and current_sl < entry_price:
                return entry_price, "Moved SL to breakeven (TP1 hit)"
            elif direction == 'SELL' and current_sl > entry_price:
                return entry_price, "Moved SL to breakeven (TP1 hit)"
        
        # Trail with ATR after TP2 (adaptive)
        if 'tp2' in targets_hit and self.config.TRAIL_SL_AFTER_TP2:
            atr = self.data_fetcher.calculate_atr()
            if atr:
                # Adaptive ATR multiplier based on volatility
                base_multiplier = self.config.TRAIL_ATR_MULTIPLIER
                
                if volatility_adjustment:
                    # Get current volatility vs average
                    try:
                        current_volatility = abs(current_price - entry_price) / entry_price
                        # Adjust multiplier: higher volatility = wider trailing stop
                        volatility_factor = min(1.5, max(0.7, current_volatility * 10))
                        trail_multiplier = base_multiplier * volatility_factor
                    except:
                        trail_multiplier = base_multiplier
                else:
                    trail_multiplier = base_multiplier
                
                trail_distance = atr * trail_multiplier
                
                if direction == 'BUY':
                    new_sl = current_price - trail_distance
                    # Ensure SL doesn't go below entry after TP1
                    if 'tp1' in targets_hit:
                        new_sl = max(new_sl, entry_price)
                    if new_sl > current_sl:  # Only move up
                        return new_sl, f"Adaptive trailing SL (ATR: ${atr:,.0f}, multiplier: {trail_multiplier:.2f})"
                else:  # SELL
                    new_sl = current_price + trail_distance
                    # Ensure SL doesn't go above entry after TP1
                    if 'tp1' in targets_hit:
                        new_sl = min(new_sl, entry_price)
                    if new_sl < current_sl:  # Only move down
                        return new_sl, f"Adaptive trailing SL (ATR: ${atr:,.0f}, multiplier: {trail_multiplier:.2f})"
        
        return current_sl, "SL unchanged"
    
    # ========================================================================
    # Enhancement 4: Time-Based Exit Rules
    # ========================================================================
    
    def check_time_exit(self, position, market_data):
        """
        Check if position should be exited based on time rules
        Returns: (should_exit, reason)
        """
        entry_time = position.get('entry_time', datetime.now())
        current_time = datetime.now()
        hours_open = (current_time - entry_time).total_seconds() / 3600
        
        # Check for no movement
        if hours_open >= self.config.TIME_EXIT_NO_MOVEMENT_HOURS:
            entry_price = position['entry_price']
            current_price = market_data['btc_price']
            movement = abs(current_price - entry_price) / entry_price
            
            if movement < self.config.TIME_EXIT_MOVEMENT_THRESHOLD:
                return True, f"No movement in {hours_open:.1f}h (only {movement*100:.2f}%)"
        
        # Check for Friday close
        if current_time.weekday() == 4:  # Friday
            if current_time.hour >= self.config.EXIT_FRIDAY_UTC_HOUR:
                return True, "Friday close - weekend risk"
        
        # Check for max position time
        if hours_open >= self.config.MAX_POSITION_HOURS:
            return True, f"Position open >{self.config.MAX_POSITION_HOURS}h - review needed"
        
        return False, "Time rules OK"
    
    # ========================================================================
    # Enhancement 5: Confluence Confirmation Delay
    # ========================================================================
    
    def confirm_signal(self, signal, market_data, ultra_filter, delay_seconds=None):
        """
        Wait and re-validate signal before entry
        Returns: (is_confirmed, reasons)
        """
        if delay_seconds is None:
            delay_seconds = self.config.CONFIRMATION_DELAY_MIN * 60
        
        print(f"\n[CONFIRMATION] Waiting {delay_seconds//60} minutes to re-validate signal...")
        
        # Store initial price
        initial_price = market_data['btc_price']
        
        # Wait for delay
        time.sleep(delay_seconds)
        
        # Get fresh market data
        fresh_market_data = self.data_fetcher.get_market_data()
        if not fresh_market_data:
            return False, "Failed to fetch fresh market data"
        
        current_price = fresh_market_data['btc_price']
        
        # Check price hasn't moved too much against signal
        price_change = (current_price - initial_price) / initial_price
        direction = signal['direction']
        
        if direction == 'BUY' and price_change < -self.config.MAX_PRICE_MOVE_AGAINST:
            return False, f"Price moved {price_change*100:.2f}% down (against long)"
        elif direction == 'SELL' and price_change > self.config.MAX_PRICE_MOVE_AGAINST:
            return False, f"Price moved {price_change*100:.2f}% up (against short)"
        
        # Re-check all 17 criteria
        if self.config.RECHECK_ALL_CRITERIA:
            is_still_valid, reasons = ultra_filter.filter_signal_ultra(signal, fresh_market_data)
            
            if not is_still_valid:
                failed_criteria = [k for k, v in reasons.items() 
                                 if k not in ['overall', 'news_items'] and '[FAIL]' in str(v)]
                return False, f"Signal invalidated: {len(failed_criteria)} criteria now failing"
            
            # Check confidence still high
            if signal['confidence'] < self.config.MIN_CONFIDENCE_AFTER_DELAY:
                return False, f"Confidence dropped to {signal['confidence']}%"
        
        return True, "Signal confirmed after delay"
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def create_execution_plan(self, signal, market_data, 
                             total_capital: float = 500, 
                             risk_per_trade: float = 0.01):
        """
        Create complete execution plan with all enhancements including confidence-based sizing
        
        Args:
            signal: Signal dictionary
            market_data: Current market data
            total_capital: Total trading capital
            risk_per_trade: Base risk per trade
            
        Returns:
            dict with execution details
        """
        # Optimize entry
        optimized_entry, should_enter, entry_reason = self.optimize_entry(signal, market_data)
        
        # Get signal confidence and quality score
        signal_confidence = signal.get('confidence', None)
        quality_score = signal.get('quality_score', None)
        
        # Calculate position sizes with confidence adjustment
        position_sizes = self.calculate_position_sizes(
            total_capital, 
            risk_per_trade,
            signal_confidence=signal_confidence,
            quality_score=quality_score
        )
        
        # Calculate exit targets
        exit_targets = self.calculate_exit_targets(
            optimized_entry,
            signal['stop_loss'],
            signal['direction']
        )
        
        return {
            'optimized_entry': optimized_entry,
            'should_enter': should_enter,
            'entry_reason': entry_reason,
            'position_sizes': position_sizes,
            'exit_targets': exit_targets,
            'original_entry': signal.get('entry_price', optimized_entry),
            'confidence_adjustment': {
                'confidence': signal_confidence,
                'quality_score': quality_score,
                'multiplier': position_sizes.get('confidence_multiplier', 1.0)
            }
        }


# Test the execution manager
if __name__ == "__main__":
    print("Testing Execution Manager...")
    print("=" * 80)
    
    from data_fetcher import BinanceDataFetcher
    
    data_fetcher = BinanceDataFetcher()
    exec_manager = ExecutionManager(data_fetcher)
    
    # Get market data
    market_data = data_fetcher.get_market_data()
    
    if market_data:
        # Create dummy signal
        signal = {
            'direction': 'BUY',
            'entry_price': market_data['btc_price'],
            'stop_loss': market_data['btc_price'] * 0.98,
            'confidence': 75
        }
        
        # Test execution plan
        plan = exec_manager.create_execution_plan(signal, market_data)
        
        print(f"\nCurrent Price: ${market_data['btc_price']:,.2f}")
        print(f"Signal Entry: ${signal['entry_price']:,.2f}")
        print(f"Optimized Entry: ${plan['optimized_entry']:,.2f}")
        print(f"Should Enter: {plan['should_enter']}")
        print(f"Reason: {plan['entry_reason']}")
        
        print("\nPosition Sizes:")
        for tranche, size in plan['position_sizes'].items():
            print(f"   {tranche}: ${size:.2f}")
        
        print("\nExit Targets:")
        for tp_name, tp_data in plan['exit_targets'].items():
            print(f"   {tp_name.upper()}: ${tp_data['price']:,.2f} ({tp_data['percentage']*100:.0f}% at 1:{tp_data['rr_ratio']})")
    
    print("\n" + "=" * 80)
    print("Execution manager test complete!")
