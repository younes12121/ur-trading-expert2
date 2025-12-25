"""
Adaptive Filter with Market Regime Detection
Dynamically adjusts criteria thresholds based on market conditions
Adapts filtering to different market regimes (trending, ranging, volatile, etc.)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional, Tuple
from enum import Enum


class MarketRegime(Enum):
    """Market regime types"""
    TRENDING_BULLISH = "trending_bullish"
    TRENDING_BEARISH = "trending_bearish"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    UNKNOWN = "unknown"


class AdaptiveFilter:
    """
    Adaptive filter that adjusts criteria thresholds based on market regime
    """
    
    def __init__(self):
        # Base thresholds (used in normal conditions)
        self.base_thresholds = {
            'rsi_min': 40,
            'rsi_max': 70,
            'volume_ratio_min': 0.8,
            'atr_min': 100,
            'ema_spacing_min': 50,
            'adx_min': 20,
            'criteria_required': 17  # Out of 20
        }
        
        # Regime-specific threshold adjustments
        self.regime_adjustments = {
            MarketRegime.TRENDING_BULLISH: {
                'rsi_min': 45,  # Slightly higher for trending
                'rsi_max': 75,
                'volume_ratio_min': 0.7,  # Lower volume OK in strong trends
                'criteria_required': 16  # Slightly more lenient
            },
            MarketRegime.TRENDING_BEARISH: {
                'rsi_min': 25,
                'rsi_max': 55,
                'volume_ratio_min': 0.7,
                'criteria_required': 16
            },
            MarketRegime.RANGING: {
                'rsi_min': 35,
                'rsi_max': 65,
                'volume_ratio_min': 1.0,  # Need higher volume in ranges
                'criteria_required': 18  # Stricter in ranging markets
            },
            MarketRegime.HIGH_VOLATILITY: {
                'atr_min': 150,  # Higher ATR threshold
                'ema_spacing_min': 75,  # Need more spacing
                'criteria_required': 17
            },
            MarketRegime.LOW_VOLATILITY: {
                'atr_min': 50,  # Lower ATR threshold
                'volume_ratio_min': 1.2,  # Need higher volume
                'criteria_required': 18  # Stricter in low vol
            },
            MarketRegime.BREAKOUT: {
                'volume_ratio_min': 1.5,  # Need strong volume for breakouts
                'criteria_required': 16  # More lenient for breakouts
            }
        }
    
    def detect_market_regime(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Detect current market regime from data
        
        Args:
            data: Multi-timeframe data
            
        Returns:
            Dict with regime detection results
        """
        try:
            h1_data = data.get('H1')
            h4_data = data.get('H4')
            
            if h1_data is None or len(h1_data) < 50:
                return {
                    'regime': MarketRegime.UNKNOWN,
                    'confidence': 0.0,
                    'reason': 'Insufficient data'
                }
            
            # Calculate indicators
            closes = h1_data['close'].tail(50).values
            highs = h1_data['high'].tail(50).values
            lows = h1_data['low'].tail(50).values
            volumes = h1_data['volume'].tail(50).values if 'volume' in h1_data.columns else None
            
            # Calculate returns and volatility
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            
            # Calculate trend strength
            ema_21 = h1_data['close'].ewm(span=21).mean().iloc[-1]
            ema_50 = h1_data['close'].ewm(span=50).mean().iloc[-1]
            trend_direction = 'bullish' if ema_21 > ema_50 else 'bearish'
            trend_strength = abs(ema_21 - ema_50) / ema_50
            
            # Calculate ATR
            high_low = h1_data['high'] - h1_data['low']
            high_close = (h1_data['high'] - h1_data['close'].shift()).abs()
            low_close = (h1_data['low'] - h1_data['close'].shift()).abs()
            ranges = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = ranges.rolling(14).mean().iloc[-1]
            avg_atr = ranges.rolling(50).mean().iloc[-1]
            
            # Calculate range (high - low over period)
            period_range = (highs.max() - lows.min()) / closes.mean()
            
            # Detect regime
            regime_scores = {}
            
            # Trending detection
            if trend_strength > 0.02:  # Strong trend
                if trend_direction == 'bullish':
                    regime_scores[MarketRegime.TRENDING_BULLISH] = 0.8
                else:
                    regime_scores[MarketRegime.TRENDING_BEARISH] = 0.8
            
            # Ranging detection
            if period_range < 0.05 and trend_strength < 0.01:  # Tight range, weak trend
                regime_scores[MarketRegime.RANGING] = 0.9
            
            # Volatility detection
            if atr > avg_atr * 1.5:
                regime_scores[MarketRegime.HIGH_VOLATILITY] = 0.7
            elif atr < avg_atr * 0.7:
                regime_scores[MarketRegime.LOW_VOLATILITY] = 0.7
            
            # Breakout detection
            if volumes is not None:
                recent_volume = np.mean(volumes[-5:])
                avg_volume = np.mean(volumes[-20:])
                if recent_volume > avg_volume * 1.5 and period_range > 0.03:
                    regime_scores[MarketRegime.BREAKOUT] = 0.6
            
            # Select regime with highest score
            if regime_scores:
                best_regime = max(regime_scores.items(), key=lambda x: x[1])
                return {
                    'regime': best_regime[0],
                    'confidence': best_regime[1],
                    'scores': regime_scores,
                    'trend_direction': trend_direction,
                    'trend_strength': trend_strength,
                    'volatility': volatility,
                    'atr_ratio': atr / avg_atr if avg_atr > 0 else 1.0
                }
            else:
                return {
                    'regime': MarketRegime.UNKNOWN,
                    'confidence': 0.5,
                    'reason': 'No clear regime detected'
                }
                
        except Exception as e:
            return {
                'regime': MarketRegime.UNKNOWN,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_adaptive_thresholds(self, regime_detection: Dict) -> Dict:
        """
        Get adaptive thresholds based on detected regime
        
        Args:
            regime_detection: Result from detect_market_regime()
            
        Returns:
            Dict with adjusted thresholds
        """
        regime = regime_detection.get('regime', MarketRegime.UNKNOWN)
        
        # Start with base thresholds
        thresholds = self.base_thresholds.copy()
        
        # Apply regime-specific adjustments
        if regime in self.regime_adjustments:
            adjustments = self.regime_adjustments[regime]
            thresholds.update(adjustments)
        
        # Add regime info
        thresholds['regime'] = regime.value if isinstance(regime, MarketRegime) else str(regime)
        thresholds['regime_confidence'] = regime_detection.get('confidence', 0.0)
        
        return thresholds
    
    def apply_adaptive_filter(self, criteria_results: Dict[str, bool], 
                            data: Dict[str, pd.DataFrame]) -> Tuple[bool, Dict]:
        """
        Apply adaptive filtering with regime-aware thresholds
        
        Args:
            criteria_results: Dict of criteria pass/fail results
            data: Multi-timeframe data for regime detection
            
        Returns:
            (is_valid, filter_details)
        """
        # Detect market regime
        regime_detection = self.detect_market_regime(data)
        
        # Get adaptive thresholds
        thresholds = self.get_adaptive_thresholds(regime_detection)
        
        # Count passed criteria
        passed_count = sum(1 for v in criteria_results.values() if v)
        total_count = len(criteria_results)
        
        # Check if meets required criteria count
        required = thresholds.get('criteria_required', 17)
        is_valid = passed_count >= required
        
        filter_details = {
            'regime': regime_detection.get('regime'),
            'regime_confidence': regime_detection.get('confidence', 0.0),
            'thresholds_used': thresholds,
            'passed_criteria': passed_count,
            'total_criteria': total_count,
            'required_criteria': required,
            'is_valid': is_valid,
            'pass_rate': (passed_count / total_count * 100) if total_count > 0 else 0
        }
        
        return is_valid, filter_details
    
    def get_regime_recommendation(self, regime_detection: Dict) -> str:
        """Get trading recommendation based on detected regime"""
        regime = regime_detection.get('regime', MarketRegime.UNKNOWN)
        confidence = regime_detection.get('confidence', 0.0)
        
        recommendations = {
            MarketRegime.TRENDING_BULLISH: "Strong bullish trend - look for long setups",
            MarketRegime.TRENDING_BEARISH: "Strong bearish trend - look for short setups",
            MarketRegime.RANGING: "Ranging market - trade range boundaries, stricter criteria",
            MarketRegime.HIGH_VOLATILITY: "High volatility - wider stops, higher volume required",
            MarketRegime.LOW_VOLATILITY: "Low volatility - need strong volume confirmation",
            MarketRegime.BREAKOUT: "Breakout conditions - high volume required",
            MarketRegime.UNKNOWN: "Unclear regime - use standard criteria"
        }
        
        base_recommendation = recommendations.get(regime, "Unknown regime")
        
        if confidence < 0.5:
            return f"{base_recommendation} (low confidence: {confidence:.1%})"
        else:
            return f"{base_recommendation} (confidence: {confidence:.1%})"


# =================================================================
# USAGE EXAMPLE
# =================================================================

if __name__ == "__main__":
    print("ADAPTIVE FILTER - TESTING")
    print("="*60)
    
    adaptive_filter = AdaptiveFilter()
    
    # Example: Create sample data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1H')
    sample_data = {
        'H1': pd.DataFrame({
            'timestamp': dates,
            'open': np.cumsum(np.random.randn(100) * 10) + 43000,
            'high': np.cumsum(np.random.randn(100) * 10) + 43100,
            'low': np.cumsum(np.random.randn(100) * 10) + 42900,
            'close': np.cumsum(np.random.randn(100) * 10) + 43000,
            'volume': np.random.randint(100000, 500000, 100)
        }),
        'H4': pd.DataFrame({
            'timestamp': dates[::4],
            'open': np.cumsum(np.random.randn(25) * 20) + 43000,
            'high': np.cumsum(np.random.randn(25) * 20) + 43100,
            'low': np.cumsum(np.random.randn(25) * 20) + 42900,
            'close': np.cumsum(np.random.randn(25) * 20) + 43000,
            'volume': np.random.randint(100000, 500000, 25)
        })
    }
    
    # Detect regime
    regime = adaptive_filter.detect_market_regime(sample_data)
    print(f"\nDetected Regime: {regime['regime']}")
    print(f"Confidence: {regime.get('confidence', 0):.1%}")
    print(f"Recommendation: {adaptive_filter.get_regime_recommendation(regime)}")
    
    # Get adaptive thresholds
    thresholds = adaptive_filter.get_adaptive_thresholds(regime)
    print(f"\nAdaptive Thresholds:")
    print(f"  Required Criteria: {thresholds['criteria_required']}/20")
    print(f"  RSI Range: {thresholds['rsi_min']}-{thresholds['rsi_max']}")
    print(f"  Volume Ratio Min: {thresholds['volume_ratio_min']}")
    
    print("\n" + "="*60)
    print("Adaptive filter loaded successfully!")

