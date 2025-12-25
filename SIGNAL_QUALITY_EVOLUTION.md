"""
ULTRA ELITE Signal System - Beyond Elite Only
Requires 19-20/20 criteria + additional confirmations
Target: 95-98% win rate with ultra-rare signals
"""

from enhanced_criteria_system import Enhanced20CriteriaSystem
import numpy as np
from datetime import datetime

class UltraEliteCriteriaSystem(Enhanced20CriteriaSystem):
    """
    Ultra Elite system requiring 19-20/20 criteria plus additional confirmations
    """
    
    def __init__(self):
        super().__init__()
        self.ultra_threshold = 19  # Require 19+/20 (vs 17+ for Elite)
        
    def apply_ultra_elite_filter(self, data: dict, symbol: str) -> tuple:
        """
        Apply Ultra Elite filter - even stricter than Elite
        
        Returns:
            (is_ultra_elite, detailed_analysis)
        """
        
        # First run standard enhanced criteria
        is_elite, analysis = self.apply_enhanced_criteria(data, symbol)
        
        # Ultra Elite requires higher score
        if analysis['total_score'] < self.ultra_threshold:
            analysis['grade'] = 'NOT ULTRA ELITE'
            analysis['confidence_level'] = 'INSUFFICIENT FOR ULTRA'
            return False, analysis
        
        # Additional Ultra Elite confirmations
        ultra_confirmations = self.check_ultra_confirmations(data, symbol, analysis)
        
        # Must pass ALL ultra confirmations
        if not all(ultra_confirmations.values()):
            analysis['grade'] = 'ELITE BUT NOT ULTRA'
            analysis['confidence_level'] = 'HIGH BUT LACKS ULTRA CONFIRMATIONS'
            analysis['ultra_failures'] = [k for k, v in ultra_confirmations.items() if not v]
            return False, analysis
        
        # Update grading for Ultra Elite
        if analysis['total_score'] == 20:
            analysis['grade'] = 'ULTRA ELITE PERFECTION'
            analysis['confidence_level'] = 'MAXIMUM ULTRA'
        else:
            analysis['grade'] = 'ULTRA ELITE A+++'
            analysis['confidence_level'] = 'VERY HIGH ULTRA'
        
        analysis['ultra_confirmations'] = ultra_confirmations
        
        return True, analysis
    
    def check_ultra_confirmations(self, data: dict, symbol: str, base_analysis: dict) -> dict:
        """
        Additional confirmations required for Ultra Elite status
        """
        confirmations = {}
        
        # 1. Multi-timeframe Volume Confluence
        confirmations['volume_confluence'] = self.check_volume_confluence(data)
        
        # 2. Smart Money Alignment
        confirmations['smart_money'] = self.check_smart_money_alignment(data)
        
        # 3. Market Structure Perfection
        confirmations['perfect_structure'] = self.check_perfect_market_structure(data)
        
        # 4. Institutional Order Flow
        confirmations['institutional_flow'] = self.check_institutional_flow(data)
        
        # 5. Volatility Regime Optimal
        confirmations['optimal_volatility'] = self.check_optimal_volatility(data, symbol)
        
        return confirmations
    
    def check_volume_confluence(self, data: dict) -> bool:
        """Check for volume confluence across multiple timeframes"""
        try:
            # Get volume data for multiple timeframes
            m15_vol_ratio = data['M15']['volume'].iloc[-1] / data['M15']['volume'].iloc[-20:].mean()
            h1_vol_ratio = data['H1']['volume'].iloc[-1] / data['H1']['volume'].iloc[-20:].mean()
            h4_vol_ratio = data['H4']['volume'].iloc[-1] / data['H4']['volume'].iloc[-10:].mean()
            
            # Require above-average volume across timeframes
            return m15_vol_ratio > 1.2 and h1_vol_ratio > 1.1 and h4_vol_ratio > 1.0
        except:
            return False
    
    def check_smart_money_alignment(self, data: dict) -> bool:
        """Check if smart money indicators align with signal"""
        try:
            h4_data = data['H4']
            d1_data = data['D1']
            
            # Check for institutional footprint patterns
            h4_close = h4_data['close'].iloc[-1]
            h4_open = h4_data['open'].iloc[-1]
            daily_range = d1_data['high'].iloc[-1] - d1_data['low'].iloc[-1]
            
            # Smart money typically trades with strong conviction (large candles)
            candle_size = abs(h4_close - h4_open)
            relative_size = candle_size / daily_range
            
            return relative_size > 0.3  # Significant move relative to daily range
        except:
            return False
    
    def check_perfect_market_structure(self, data: dict) -> bool:
        """Check for perfect market structure across timeframes"""
        try:
            h1_data = data['H1']
            h4_data = data['H4']
            d1_data = data['D1']
            
            # Check for clean trend structure
            h1_trend_clean = self.is_trend_clean(h1_data.tail(10))
            h4_trend_clean = self.is_trend_clean(h4_data.tail(6))
            d1_trend_clean = self.is_trend_clean(d1_data.tail(5))
            
            return h1_trend_clean and h4_trend_clean and d1_trend_clean
        except:
            return False
    
    def is_trend_clean(self, data) -> bool:
        """Check if trend shows clean structure without choppy movement"""
        try:
            closes = data['close'].values
            highs = data['high'].values
            lows = data['low'].values
            
            # Calculate trend consistency
            trend_consistency = 0
            for i in range(1, len(closes)):
                if closes[i] > closes[i-1]:  # Uptrend
                    if lows[i] >= lows[i-1] * 0.995:  # Higher lows (allow small variance)
                        trend_consistency += 1
                elif closes[i] < closes[i-1]:  # Downtrend
                    if highs[i] <= highs[i-1] * 1.005:  # Lower highs (allow small variance)
                        trend_consistency += 1
            
            # Require 70%+ trend consistency
            return (trend_consistency / (len(closes) - 1)) > 0.7
        except:
            return False
    
    def check_institutional_flow(self, data: dict) -> bool:
        """Check for institutional order flow patterns"""
        try:
            h1_data = data['H1'].tail(5)
            
            # Look for institutional absorption patterns
            total_volume = h1_data['volume'].sum()
            avg_volume = h1_data['volume'].mean()
            
            # Check for volume distribution
            high_vol_candles = (h1_data['volume'] > avg_volume * 1.5).sum()
            
            # Institutional flow shows concentrated volume
            return high_vol_candles >= 2 and total_volume > avg_volume * 5
        except:
            return False
    
    def check_optimal_volatility(self, data: dict, symbol: str) -> bool:
        """Check if volatility is in optimal range for the asset"""
        try:
            h1_data = data['H1']
            
            # Calculate recent volatility
            processed_data = self.calculate_all_indicators(h1_data)
            current_atr = processed_data['atr'].iloc[-1]
            avg_atr = processed_data['atr'].iloc[-20:].mean()
            
            # Define optimal volatility ranges by asset
            if symbol in ['BTC', 'BTCUSD']:
                # Bitcoin optimal ATR range
                return 0.8 <= (current_atr / avg_atr) <= 1.5
            elif symbol in ['GOLD', 'XAUUSD']:
                # Gold optimal ATR range  
                return 0.9 <= (current_atr / avg_atr) <= 1.3
            else:
                # Forex/Futures optimal range
                return 0.85 <= (current_atr / avg_atr) <= 1.4
        except:
            return False


# Testing Ultra Elite System
if __name__ == "__main__":
    print("="*80)
    print("🔥 ULTRA ELITE CRITERIA SYSTEM - TESTING")
    print("="*80)
    
    ultra_system = UltraEliteCriteriaSystem()
    print(f"✅ Ultra Elite system initialized")
    print(f"📊 Threshold: {ultra_system.ultra_threshold}/20 criteria required")
    print(f"🎯 Target win rate: 95-98%")
    print(f"⚡ Signal frequency: Ultra rare (perfect setups only)")
    
    print("\n" + "="*80)
    print("🚀 ULTRA ELITE SYSTEM READY!")
    print("="*80)
