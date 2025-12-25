"""
Enhanced Risk Management Module for Trading Bot
Handles adaptive position sizing, dynamic stop losses, and multi-factor risk assessment.
"""

import time
import logging
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional
from global_error_learning import global_error_manager, record_error

logger = logging.getLogger(__name__)

class EnhancedRiskManager:
    def __init__(self):
        # Base risk limits
        self.MAX_RISK_PER_TRADE = 0.02  # 2% max risk
        self.MAX_PORTFOLIO_RISK = 0.06  # 6% max total open risk
        self.DRAWDOWN_LIMIT = 0.10      # 10% drawdown triggers preservation mode

        # Adaptive risk parameters
        self.volatility_multiplier = {
            'low': 1.0,      # Normal sizing in low vol
            'medium': 0.8,   # Reduce size in medium vol
            'high': 0.6      # Significantly reduce in high vol
        }

        self.market_regime_multiplier = {
            'RISK_ON': 1.0,      # Normal in correlated markets
            'RISK_OFF': 0.7,     # Reduce in decoupling
            'SAFE_HAVEN': 0.9,   # Slight reduction in defensive moves
            'NEUTRAL': 1.0       # Normal
        }

        self.confidence_multiplier = {
            'high': 1.0,     # Full size for high confidence
            'medium': 0.8,   # Reduce for medium confidence
            'low': 0.6       # Significant reduction for low confidence
        }

        # Performance tracking
        self.trade_history = []
        self.daily_pnl = {}
        self.weekly_pnl = {}

    def calculate_adaptive_position_size(self, balance: float, entry_price: float, stop_loss: float,
                                       market_data: Dict, signal_confidence: float,
                                       market_regime: str = 'NEUTRAL', pair: str = "EURUSD") -> Dict:
        """
        Calculate position size with multiple risk factors and error learning
        """
        start_time = time.time()
        operation_context = {
            'operation_type': 'calculate_position_size',
            'balance': balance,
            'confidence_level': signal_confidence,
            'market_regime': market_regime,
            'volatility': market_data.get('volatility', 0.02),
            'correlation_risk': market_data.get('correlation_risk', 0.1),
            'drawdown_pct': market_data.get('drawdown_pct', 0.0),
            'system_load': 0.5,  # Placeholder
            'memory_usage': 0.5   # Placeholder
        }

        # Predict error likelihood
        error_prediction = global_error_manager.predict_error_likelihood('risk_manager', operation_context)

        if not error_prediction['should_attempt']:
            logger.warning(f"[RISK_MANAGER] Avoiding position size calculation due to high error risk: {error_prediction['error_probability']:.1%}")
            logger.info(f"[RISK_MANAGER] Alternatives: {error_prediction['alternative_suggestions']}")

            # Record avoidance
            record_error('risk_manager', operation_context, had_error=False,
                        error_details="Proactively avoided due to error prediction",
                        success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']},
                        execution_time=time.time() - start_time)

            return {
                'position_size': balance * 0.01,  # Conservative fallback: 1% of balance
                'risk_amount': balance * 0.005,   # 0.5% risk
                'confidence': 0.3,
                'reason': f'High error risk detected ({error_prediction["error_probability"]:.1%})'
            }

        success = False
        error_details = None

        try:
            # Base risk calculation
            base_risk_pct = self._calculate_base_risk(signal_confidence, market_regime)

            # Apply volatility adjustment
            volatility = market_data.get('btc_volatility', 0.03)
            vol_adjustment = self._get_volatility_adjustment(volatility)

            # Apply market regime adjustment
            regime_adjustment = self.market_regime_multiplier.get(market_regime, 1.0)

            # Apply confidence adjustment
            confidence_level = self._classify_confidence(signal_confidence)
            confidence_adjustment = self.confidence_multiplier.get(confidence_level, 0.8)

            # Calculate final risk percentage
            final_risk_pct = base_risk_pct * vol_adjustment * regime_adjustment * confidence_adjustment

            # Ensure within limits
            final_risk_pct = min(final_risk_pct, self.MAX_RISK_PER_TRADE)

            # Calculate position size
            risk_amount = balance * final_risk_pct
            price_diff = abs(entry_price - stop_loss)

            if price_diff == 0:
                return self._get_error_response("Invalid stop loss distance")

            # Calculate units (simplified for crypto)
            units = risk_amount / price_diff
            lots = units / 100000  # Convert to standard lots

            success = True
            record_error('risk_manager', operation_context, had_error=False,
                        success_metrics={
                            'calculation_successful': True,
                            'risk_pct': final_risk_pct * 100,
                            'confidence_level': confidence_level
                        },
                        execution_time=time.time() - start_time)

            return {
                'risk_pct': final_risk_pct * 100,
                'risk_amount': risk_amount,
                'units': units,
                'lots': round(lots, 3),
                'base_risk_pct': base_risk_pct * 100,
                'volatility_adjustment': vol_adjustment,
                'regime_adjustment': regime_adjustment,
                'confidence_adjustment': confidence_adjustment,
                'confidence_level': confidence_level,
                'calculations': {
                    'price_diff': price_diff,
                    'volatility': volatility,
                    'market_regime': market_regime
                }
            }

        except Exception as e:
            error_details = str(e)
            record_error('risk_manager', operation_context, had_error=True,
                        error_details=error_details,
                        execution_time=time.time() - start_time)
            return self._get_error_response(f"Position size calculation error: {error_details}")

    def _calculate_base_risk(self, confidence: float, regime: str) -> float:
        """Calculate base risk percentage based on confidence and regime"""
        # Higher confidence = higher base risk
        if confidence >= 80:
            base_risk = 0.015  # 1.5%
        elif confidence >= 70:
            base_risk = 0.012  # 1.2%
        elif confidence >= 60:
            base_risk = 0.01   # 1.0%
        else:
            base_risk = 0.008  # 0.8%

        # Adjust for market regime
        if regime == 'RISK_OFF':
            base_risk *= 0.8  # Reduce in volatile environments
        elif regime == 'SAFE_HAVEN':
            base_risk *= 0.9  # Slight reduction in defensive moves

        return min(base_risk, self.MAX_RISK_PER_TRADE)

    def _get_volatility_adjustment(self, volatility: float) -> float:
        """Get volatility-based adjustment multiplier"""
        if volatility <= 0.02:
            return self.volatility_multiplier['low']
        elif volatility <= 0.05:
            return self.volatility_multiplier['medium']
        else:
            return self.volatility_multiplier['high']

    def _classify_confidence(self, confidence: float) -> str:
        """Classify confidence level"""
        if confidence >= 75:
            return 'high'
        elif confidence >= 60:
            return 'medium'
        else:
            return 'low'

    def calculate_dynamic_stop_loss(self, entry_price: float, direction: str,
                                  market_data: Dict, signal_strength: float) -> Dict:
        """
        Calculate dynamic stop loss based on volatility and market conditions
        """
        try:
            volatility = market_data.get('btc_volatility', 0.03)
            current_price = market_data.get('btc_price', entry_price)

            # Base stop distance based on volatility
            base_distance = current_price * volatility * 1.5  # ATR-style calculation

            # Adjust based on signal strength
            strength_multiplier = max(0.8, min(1.5, signal_strength / 2.0))

            # Adjust based on market regime
            regime = market_data.get('market_regime', 'NEUTRAL')
            regime_multiplier = 1.0
            if regime == 'HIGH_VOLATILITY':
                regime_multiplier = 1.3  # Wider stops in high vol
            elif regime == 'LOW_VOLATILITY':
                regime_multiplier = 0.8  # Tighter stops in low vol

            # Calculate final stop distance
            stop_distance = base_distance * strength_multiplier * regime_multiplier

            # Set minimum and maximum stop distances
            min_stop = current_price * 0.005  # 0.5% minimum
            max_stop = current_price * 0.03   # 3% maximum
            stop_distance = max(min_stop, min(max_stop, stop_distance))

            # Calculate stop price
            if direction == 'BUY':
                stop_price = entry_price - stop_distance
            elif direction == 'SELL':
                stop_price = entry_price + stop_distance
            else:
                stop_price = entry_price

            return {
                'stop_price': round(stop_price, 2),
                'stop_distance': round(stop_distance, 2),
                'stop_distance_pct': round((stop_distance / current_price) * 100, 2),
                'base_distance': round(base_distance, 2),
                'strength_multiplier': round(strength_multiplier, 2),
                'regime_multiplier': round(regime_multiplier, 2),
                'volatility': round(volatility * 100, 2)
            }

        except Exception as e:
            return {
                'stop_price': entry_price * 0.98,  # Fallback 2% stop
                'stop_distance': entry_price * 0.02,
                'error': f"Dynamic SL calculation failed: {e}"
            }

    def calculate_trailing_stop(self, entry_price: float, current_price: float,
                               direction: str, trailing_pct: float = 0.01) -> Dict:
        """
        Calculate trailing stop levels
        """
        try:
            if direction == 'BUY':
                # For long positions, trail below current price
                trail_distance = current_price * trailing_pct
                trailing_stop = current_price - trail_distance
            elif direction == 'SELL':
                # For short positions, trail above current price
                trail_distance = current_price * trailing_pct
                trailing_stop = current_price + trail_distance
            else:
                return {'error': 'Invalid direction'}

            return {
                'trailing_stop': round(trailing_stop, 2),
                'trail_distance': round(trail_distance, 2),
                'trail_pct': trailing_pct * 100,
                'current_price': current_price
            }

        except Exception as e:
            return {'error': f"Trailing stop calculation failed: {e}"}

    def assess_portfolio_risk(self, open_positions: List[Dict], account_balance: float) -> Dict:
        """
        Comprehensive portfolio risk assessment
        """
        try:
            total_risk_amount = 0
            total_exposure = 0
            risk_by_asset = {}
            correlation_risk = 0

            for position in open_positions:
                risk_amount = position.get('risk_amount', 0)
                position_value = position.get('position_value', 0)
                asset = position.get('asset', 'UNKNOWN')

                total_risk_amount += risk_amount
                total_exposure += position_value

                if asset not in risk_by_asset:
                    risk_by_asset[asset] = {'risk': 0, 'exposure': 0, 'count': 0}
                risk_by_asset[asset]['risk'] += risk_amount
                risk_by_asset[asset]['exposure'] += position_value
                risk_by_asset[asset]['count'] += 1

            # Calculate risk percentages
            total_risk_pct = (total_risk_amount / account_balance) * 100 if account_balance > 0 else 0
            total_exposure_pct = (total_exposure / account_balance) * 100 if account_balance > 0 else 0

            # Check concentration risk
            max_asset_risk = max([asset_data['risk'] for asset_data in risk_by_asset.values()], default=0)
            concentration_risk = (max_asset_risk / account_balance) * 100 if account_balance > 0 else 0

            # Risk assessment
            risk_level = 'LOW'
            if total_risk_pct > 8 or concentration_risk > 4:
                risk_level = 'HIGH'
            elif total_risk_pct > 5 or concentration_risk > 2.5:
                risk_level = 'MEDIUM'

            return {
                'total_risk_amount': round(total_risk_amount, 2),
                'total_risk_pct': round(total_risk_pct, 2),
                'total_exposure_pct': round(total_exposure_pct, 2),
                'concentration_risk_pct': round(concentration_risk, 2),
                'risk_level': risk_level,
                'risk_by_asset': risk_by_asset,
                'max_positions_allowed': self._calculate_max_positions(total_risk_pct),
                'recommendations': self._get_risk_recommendations(risk_level, concentration_risk)
            }

        except Exception as e:
            return {'error': f"Portfolio risk assessment failed: {e}"}

    def _calculate_max_positions(self, current_risk_pct: float) -> int:
        """Calculate maximum additional positions allowed"""
        remaining_risk_capacity = max(0, self.MAX_PORTFOLIO_RISK * 100 - current_risk_pct)
        avg_risk_per_position = 1.5  # Assume 1.5% average risk per position
        return max(0, int(remaining_risk_capacity / avg_risk_per_position))

    def _get_risk_recommendations(self, risk_level: str, concentration_risk: float) -> List[str]:
        """Get risk management recommendations"""
        recommendations = []

        if risk_level == 'HIGH':
            recommendations.append("⚠️ HIGH RISK: Reduce position sizes immediately")
            recommendations.append("❌ Stop opening new positions")
            recommendations.append("🔄 Consider closing some positions to reduce exposure")
        elif risk_level == 'MEDIUM':
            recommendations.append("⚡ MEDIUM RISK: Monitor closely")
            recommendations.append("📏 Reduce size of new positions")
        else:
            recommendations.append("✅ LOW RISK: Normal operations OK")

        if concentration_risk > 3:
            recommendations.append("🎯 HIGH CONCENTRATION: Diversify across more assets")

        return recommendations

    def _get_error_response(self, message: str) -> Dict:
        """Return standardized error response"""
        return {
            'error': message,
            'risk_pct': 0.5,  # Minimal fallback
            'lots': 0.001     # Minimal fallback
        }
        
    def calculate_position_size(self, balance, entry_price, stop_loss, risk_pct=0.01, pair="EURUSD"):
        """
        Calculate position size based on risk percentage
        Returns: dict with lot_size, units, risk_amount
        """
        if risk_pct > self.MAX_RISK_PER_TRADE:
            risk_pct = self.MAX_RISK_PER_TRADE
            
        risk_amount = balance * risk_pct
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return None
            
        # Standard Forex Calculation (approximate for USD base)
        # Risk = (Entry - SL) * Units
        # Units = Risk / (Entry - SL)
        
        # Adjust for JPY pairs (multiplier 100) or Gold (multiplier 1)
        multiplier = 1.0
        if "JPY" in pair:
            multiplier = 0.01 # JPY pips are 0.01
        elif "XAU" in pair or "GOLD" in pair:
            multiplier = 1.0
        else:
            multiplier = 0.0001 # Standard pips
            
        # Calculate pip value roughly (assuming USD account)
        # This is a simplified calculation. For precise values, we'd need exchange rates.
        # Position Size = Risk Amount / (Stop Loss Pips * Pip Value)
        
        pips = price_diff / multiplier
        
        # Standard lot = $10/pip (approx for EURUSD)
        # Mini lot = $1/pip
        # Micro lot = $0.10/pip
        
        # Simplified: Units = Risk Amount / Price Diff
        units = risk_amount / price_diff
        
        # Convert to lots (1 standard lot = 100,000 units)
        lots = units / 100000
        
        return {
            'risk_pct': risk_pct * 100,
            'risk_amount': risk_amount,
            'units': units,
            'lots': round(lots, 2),
            'pips': int(pips)
        }

    def calculate_risk_scenarios(self, balance, entry, stop_loss, pair="EURUSD"):
        """
        Calculate 3 risk scenarios: Conservative, Moderate, Aggressive
        """
        scenarios = {
            'conservative': self.calculate_position_size(balance, entry, stop_loss, 0.005, pair), # 0.5%
            'moderate': self.calculate_position_size(balance, entry, stop_loss, 0.01, pair),      # 1.0%
            'aggressive': self.calculate_position_size(balance, entry, stop_loss, 0.02, pair)     # 2.0%
        }
        return scenarios

    def check_portfolio_exposure(self, open_trades, balance):
        """
        Calculate total risk across all open trades
        """
        total_risk = 0.0
        exposure_map = {}
        asset_types = {'forex': [], 'crypto': [], 'commodities': [], 'stocks': [], 'indices': []}

        for trade in open_trades:
            # Assuming trade has 'risk_amount' or we calculate it
            risk = trade.get('risk_amount', 0)
            pair = trade.get('pair', 'Unknown')

            total_risk += risk
            exposure_map[pair] = exposure_map.get(pair, 0) + risk

            # Categorize assets
            if pair.upper() in ['BTC', 'ETH', 'LTC', 'ADA', 'DOT', 'SOL', 'MATIC']:
                asset_types['crypto'].append((pair, risk))
            elif pair.upper() in ['XAUUSD', 'XAUEUR', 'GOLD']:
                asset_types['commodities'].append((pair, risk))
            elif 'USD' in pair.upper() or 'EUR' in pair.upper() or 'GBP' in pair.upper() or 'JPY' in pair.upper():
                asset_types['forex'].append((pair, risk))
            elif pair.upper() in ['ES', 'NQ', 'YM', 'RTY']:
                asset_types['indices'].append((pair, risk))
            else:
                asset_types['stocks'].append((pair, risk))

        risk_pct = total_risk / balance if balance > 0 else 0

        return {
            'total_risk_amount': total_risk,
            'total_risk_pct': risk_pct * 100,
            'is_overexposed': risk_pct > self.MAX_PORTFOLIO_RISK,
            'exposure_map': exposure_map,
            'asset_types': asset_types,
            'heat_map': self._generate_heat_map(exposure_map, total_risk, risk_pct * 100)
        }

    def _generate_heat_map(self, exposure_map, total_risk, total_risk_pct):
        """Generate a visual heat map representation"""
        if not exposure_map:
            return "🔥 PORTFOLIO HEAT MAP\n\n⚪ No open trades - Portfolio is cool!"

        # Sort by risk exposure
        sorted_exposure = sorted(exposure_map.items(), key=lambda x: x[1], reverse=True)

        # Determine risk level colors
        def get_risk_color(risk_pct, total_risk_pct):
            if total_risk_pct > 10:  # Very high total risk
                base_intensity = 0.8
            elif total_risk_pct > 5:
                base_intensity = 0.6
            else:
                base_intensity = 0.4

            if risk_pct > 3: return "🔴"  # High risk (red)
            elif risk_pct > 1.5: return "🟠"  # Medium risk (orange)
            elif risk_pct > 0.5: return "🟡"  # Low risk (yellow)
            else: return "🟢"  # Very low risk (green)

        heat_map = "🔥 PORTFOLIO HEAT MAP\n\n"
        heat_map += f"💰 Total Portfolio Risk: *${total_risk:.2f}* ({total_risk_pct:.1f}%)\n\n"

        # Overall risk status
        if total_risk_pct > 10:
            heat_map += "🚨 **OVEREXPOSED** - Reduce positions immediately!\n\n"
        elif total_risk_pct > 5:
            heat_map += "⚠️ **HIGH RISK** - Monitor closely\n\n"
        elif total_risk_pct > 2:
            heat_map += "🟡 **MODERATE RISK** - Manage carefully\n\n"
        else:
            heat_map += "✅ **LOW RISK** - Good risk management\n\n"

        heat_map += "📊 Risk by Asset:\n"
        heat_map += "─" * 30 + "\n"

        for pair, risk_amount in sorted_exposure:
            risk_pct = (risk_amount / total_risk * 100) if total_risk > 0 else 0
            color = get_risk_color(risk_pct, total_risk_pct)

            # Create visual bar (max 20 chars)
            bar_length = min(20, max(1, int(risk_pct * 2)))
            bar = "█" * bar_length

            heat_map += f"{color} {pair:<10} ${risk_amount:<8.2f} ({risk_pct:<5.1f}%) {bar}\n"

        heat_map += "\n" + "─" * 30 + "\n"

        # Recommendations
        if total_risk_pct > self.MAX_PORTFOLIO_RISK * 100:
            heat_map += "💡 **RECOMMENDATIONS:**\n"
            heat_map += "• Close 2-3 positions to reduce exposure\n"
            heat_map += "• Avoid opening new trades\n"
            heat_map += "• Consider taking profits on winners\n"
        elif len(sorted_exposure) > 5:
            heat_map += "💡 **RECOMMENDATIONS:**\n"
            heat_map += "• Consider reducing number of open positions\n"
            heat_map += "• Focus on highest conviction trades\n"
        else:
            heat_map += "✅ **GOOD MANAGEMENT:** Keep monitoring!"

        return heat_map

    def optimize_risk_reward(self, entry_price, direction, market_data=None, current_risk_pct=1.0):
        """
        Interactive Risk/Reward optimizer - suggests optimal TP/SL levels

        Args:
            entry_price: Entry price
            direction: 'buy' or 'sell'
            market_data: Dict with volatility, support/resistance levels
            current_risk_pct: Current risk percentage (1% default)

        Returns:
            Dict with optimized scenarios
        """
        scenarios = {
            'conservative': {'rr_ratio': 1.5, 'description': 'Safe, steady profits'},
            'moderate': {'rr_ratio': 2.0, 'description': 'Balanced approach'},
            'aggressive': {'rr_ratio': 3.0, 'description': 'Higher reward potential'},
            'optimal': {'rr_ratio': 2.5, 'description': 'Sweet spot based on data'}
        }

        # Use market data if available
        volatility = market_data.get('volatility', 0.01) if market_data else 0.01
        atr = market_data.get('atr', entry_price * 0.02) if market_data else entry_price * 0.02

        # Calculate stop loss based on volatility (1.5-2x ATR)
        sl_distance = atr * 1.8

        # Calculate risk amount
        risk_amount = 1000 * current_risk_pct  # Assuming $1000 account for demo

        if direction.lower() == 'buy':
            stop_loss = entry_price - sl_distance
            risk_per_unit = entry_price - stop_loss
        else:  # sell
            stop_loss = entry_price + sl_distance
            risk_per_unit = stop_loss - entry_price

        # Calculate position size
        units = risk_amount / risk_per_unit
        lots = units / 100000  # Standard lots

        optimized_scenarios = {}

        for scenario_name, scenario_data in scenarios.items():
            rr_ratio = scenario_data['rr_ratio']

            if direction.lower() == 'buy':
                take_profit = entry_price + (risk_per_unit * rr_ratio)
                reward_amount = (take_profit - entry_price) * units
            else:  # sell
                take_profit = entry_price - (risk_per_unit * rr_ratio)
                reward_amount = (entry_price - take_profit) * units

            # Calculate probability of success (rough estimate)
            if scenario_name == 'conservative':
                win_prob = 0.70
            elif scenario_name == 'moderate':
                win_prob = 0.60
            elif scenario_name == 'aggressive':
                win_prob = 0.45
            else:  # optimal
                win_prob = 0.55

            # Expected value
            expected_value = (reward_amount * win_prob) - (risk_amount * (1 - win_prob))

            optimized_scenarios[scenario_name] = {
                'entry': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'rr_ratio': rr_ratio,
                'risk_amount': risk_amount,
                'reward_amount': reward_amount,
                'position_size': lots,
                'win_probability': win_prob,
                'expected_value': expected_value,
                'description': scenario_data['description'],
                'break_even_win_rate': 1 / (1 + rr_ratio)
            }

        return optimized_scenarios

    def get_risk_reward_analysis(self, entry, sl, tp, direction='buy'):
        """
        Analyze a specific risk/reward setup

        Returns:
            Dict with analysis and recommendations
        """
        if direction.lower() == 'buy':
            risk = entry - sl
            reward = tp - entry
        else:
            risk = sl - entry
            reward = entry - tp

        if risk <= 0:
            return {'error': 'Invalid stop loss - must be below entry for buys, above for sells'}

        rr_ratio = reward / risk

        # Analysis
        analysis = {
            'rr_ratio': rr_ratio,
            'risk_amount_per_unit': risk,
            'reward_amount_per_unit': reward,
            'break_even_win_rate': 1 / (1 + rr_ratio),
            'recommended': rr_ratio >= 1.5,
            'grade': self._grade_rr_ratio(rr_ratio)
        }

        # Recommendations
        if rr_ratio < 1.2:
            analysis['recommendation'] = "❌ POOR - Risk too high relative to reward. Consider wider targets or tighter stops."
        elif rr_ratio < 1.8:
            analysis['recommendation'] = "⚠️ FAIR - Decent ratio but could be better. Look for better entries."
        elif rr_ratio < 2.5:
            analysis['recommendation'] = "✅ GOOD - Solid risk/reward. This setup has potential."
        else:
            analysis['recommendation'] = "🎯 EXCELLENT - Premium setup. High probability of success."

        return analysis

    def _grade_rr_ratio(self, rr_ratio):
        """Grade the risk/reward ratio"""
        if rr_ratio >= 3.0: return "A+"
        elif rr_ratio >= 2.5: return "A"
        elif rr_ratio >= 2.0: return "B+"
        elif rr_ratio >= 1.5: return "B"
        elif rr_ratio >= 1.2: return "C+"
        elif rr_ratio >= 1.0: return "C"
        else: return "D"

    def check_drawdown(self, trade_history, starting_balance):
        """
        Check current drawdown and trigger preservation mode if needed
        """
        current_balance = starting_balance
        peak_balance = starting_balance
        max_drawdown = 0.0
        current_drawdown = 0.0
        
        for trade in trade_history:
            pnl = trade.get('pnl', 0)
            current_balance += pnl
            
            if current_balance > peak_balance:
                peak_balance = current_balance
            
            dd = (peak_balance - current_balance) / peak_balance
            if dd > max_drawdown:
                max_drawdown = dd
                
        current_drawdown = (peak_balance - current_balance) / peak_balance
        
        return {
            'current_balance': current_balance,
            'peak_balance': peak_balance,
            'current_drawdown_pct': current_drawdown * 100,
            'max_drawdown_pct': max_drawdown * 100,
            'preservation_mode': current_drawdown > self.DRAWDOWN_LIMIT
        }


# Backward compatibility alias
RiskManager = EnhancedRiskManager
