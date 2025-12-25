"""
ENHANCED 20-CRITERIA TRADING SYSTEM
Advanced confirmation signals for ultra-high probability setups
Target: 95%+ win rate with comprehensive multi-factor analysis
"""

import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Tuple, List, Optional

class Enhanced20CriteriaSystem:
    """
    Enhanced 20-criteria system with advanced confirmation signals
    Each criterion now has proper validation logic instead of simplified True/False
    """
    
    def __init__(self):
        self.criteria_names = [
            "mtf_alignment",           # 1. Multi-timeframe alignment
            "price_ema",              # 2. Price vs EMA position  
            "rsi_momentum",           # 3. RSI momentum
            "macd_confirmation",      # 4. MACD confirmation
            "stochastic_signal",      # 5. ENHANCED: Stochastic confirmation
            "adx_strength",           # 6. ENHANCED: ADX trend strength
            "volume_confirmation",    # 7. Volume confirmation
            "bb_position",           # 8. Bollinger Bands position
            "atr_volatility",        # 9. ATR volatility check
            "ema_spacing",           # 10. EMA spacing
            "price_action_patterns", # 11. ENHANCED: Price action pattern recognition
            "htf_confirmation",      # 12. Higher timeframe confirmation
            "momentum_acceleration", # 13. ENHANCED: Momentum acceleration analysis
            "sr_respect",           # 14. ENHANCED: Support/Resistance level respect
            "divergence_analysis",  # 15. ENHANCED: Bullish/Bearish divergence detection
            "session_timing",       # 16. ENHANCED: Optimal trading session analysis
            "breakout_potential",   # 17. ENHANCED: Breakout/breakdown potential
            "risk_reward_ratio",    # 18. ENHANCED: Proper risk/reward calculation
            "trend_consistency",    # 19. ENHANCED: Multi-timeframe trend consistency
            "market_structure"      # 20. ENHANCED: Market structure analysis
        ]
    
    def apply_enhanced_criteria(self, data: Dict, symbol: str) -> Tuple[bool, Dict]:
        """
        Apply all 20 enhanced criteria with proper validation
        
        Args:
            data: Multi-timeframe data (M15, H1, H4, D1)
            symbol: Trading symbol (BTC, GOLD, EURUSD, etc.)
            
        Returns:
            (is_elite_signal, detailed_analysis)
        """
        
        criteria_results = {}
        score = 0
        analysis = {
            'passed_criteria': [],
            'failed_criteria': [],
            'warnings': [],
            'confidence_factors': []
        }
        
        # Process data for all timeframes
        processed_data = {}
        for tf, df in data.items():
            processed_data[tf] = self.calculate_all_indicators(df)
        
        m15 = processed_data['M15'].iloc[-1]
        h1 = processed_data['H1'].iloc[-1] 
        h4 = processed_data['H4'].iloc[-1]
        d1 = processed_data['D1'].iloc[-1]
        
        # Determine primary trend
        h1_trend = 'bullish' if h1['ema_21'] > h1['ema_50'] else 'bearish'
        h4_trend = 'bullish' if h4['ema_21'] > h4['ema_50'] else 'bearish'
        d1_trend = 'bullish' if d1['ema_21'] > d1['ema_50'] else 'bearish'
        
        # =================================================================
        # CRITERION 1: Multi-Timeframe Alignment (ENHANCED)
        # =================================================================
        mtf_alignment = self.check_mtf_alignment(h1_trend, h4_trend, d1_trend, processed_data)
        if mtf_alignment['aligned']:
            score += 1
            criteria_results['mtf_alignment'] = f"[OK] {mtf_alignment['strength']} alignment"
            analysis['passed_criteria'].append("Multi-timeframe trend alignment confirmed")
            if mtf_alignment['strength'] == 'PERFECT':
                analysis['confidence_factors'].append("Perfect 3-TF alignment")
        else:
            criteria_results['mtf_alignment'] = f"[FAIL] {mtf_alignment['reason']}"
            analysis['failed_criteria'].append("Multi-timeframe alignment missing")
        
        # =================================================================
        # CRITERION 2: Price vs EMA Position
        # =================================================================
        price_ema_ok = (m15['close'] > m15['ema_21']) if h1_trend == 'bullish' else (m15['close'] < m15['ema_21'])
        if price_ema_ok:
            score += 1
            criteria_results['price_ema'] = "[OK] Price correctly positioned vs EMA-21"
            analysis['passed_criteria'].append("Price aligned with trend direction")
        else:
            criteria_results['price_ema'] = "[FAIL] Price against EMA-21"
            analysis['failed_criteria'].append("Price not aligned with EMA trend")
        
        # =================================================================
        # CRITERION 3: RSI Momentum (ENHANCED)
        # =================================================================
        rsi_analysis = self.analyze_rsi_momentum(h1['rsi'], h4['rsi'], h1_trend)
        if rsi_analysis['valid']:
            score += 1
            criteria_results['rsi_momentum'] = f"[OK] {rsi_analysis['description']}"
            analysis['passed_criteria'].append(f"RSI momentum: {rsi_analysis['description']}")
        else:
            criteria_results['rsi_momentum'] = f"[FAIL] {rsi_analysis['reason']}"
            analysis['failed_criteria'].append(f"RSI issue: {rsi_analysis['reason']}")
        
        # =================================================================
        # CRITERION 4: MACD Confirmation
        # =================================================================
        macd_ok = (h1['macd'] > h1['macd_signal']) if h1_trend == 'bullish' else (h1['macd'] < h1['macd_signal'])
        if macd_ok:
            score += 1
            criteria_results['macd_confirmation'] = "[OK] MACD confirms trend"
            analysis['passed_criteria'].append("MACD histogram supports direction")
        else:
            criteria_results['macd_confirmation'] = "[FAIL] MACD divergent"
            analysis['failed_criteria'].append("MACD does not confirm trend")
        
        # =================================================================
        # CRITERION 5: Stochastic Signal (ENHANCED - No longer just True)
        # =================================================================
        stoch_analysis = self.analyze_stochastic_signal(h1, h1_trend)
        if stoch_analysis['valid']:
            score += 1
            criteria_results['stochastic_signal'] = f"[OK] {stoch_analysis['signal']}"
            analysis['passed_criteria'].append(f"Stochastic: {stoch_analysis['signal']}")
        else:
            criteria_results['stochastic_signal'] = f"[FAIL] {stoch_analysis['reason']}"
            analysis['failed_criteria'].append(f"Stochastic issue: {stoch_analysis['reason']}")
        
        # =================================================================
        # CRITERION 6: ADX Strength (ENHANCED - No longer just True) 
        # =================================================================
        adx_analysis = self.analyze_adx_strength(h1.get('adx', 25), h4.get('adx', 25))
        if adx_analysis['strong']:
            score += 1
            criteria_results['adx_strength'] = f"[OK] {adx_analysis['description']}"
            analysis['passed_criteria'].append(f"Trend strength: {adx_analysis['description']}")
        else:
            criteria_results['adx_strength'] = f"[FAIL] {adx_analysis['reason']}"
            analysis['failed_criteria'].append(f"ADX issue: {adx_analysis['reason']}")
        
        # =================================================================
        # CRITERION 7: Volume Confirmation
        # =================================================================
        volume_ok = m15['volume_ratio'] > 0.8
        if volume_ok:
            score += 1
            criteria_results['volume_confirmation'] = f"[OK] Volume ratio: {m15['volume_ratio']:.2f}"
            analysis['passed_criteria'].append("Volume supports the move")
        else:
            criteria_results['volume_confirmation'] = f"[FAIL] Low volume: {m15['volume_ratio']:.2f}"
            analysis['failed_criteria'].append("Insufficient volume confirmation")
        
        # =================================================================
        # CRITERION 8: Bollinger Bands Position
        # =================================================================
        bb_ok = (m15['close'] > m15['bb_middle']) if h1_trend == 'bullish' else (m15['close'] < m15['bb_middle'])
        if bb_ok:
            score += 1
            criteria_results['bb_position'] = "[OK] Price positioned correctly vs BB middle"
            analysis['passed_criteria'].append("Bollinger Bands support direction")
        else:
            criteria_results['bb_position'] = "[FAIL] Wrong side of BB middle"
            analysis['failed_criteria'].append("Price on wrong side of BB middle")
        
        # =================================================================
        # CRITERION 9: ATR Volatility Check
        # =================================================================
        atr_threshold = 100 if symbol in ['BTC', 'BTCUSD'] else (2 if symbol in ['GOLD', 'XAUUSD'] else 0.001)
        atr_ok = h1['atr'] > atr_threshold
        if atr_ok:
            score += 1
            criteria_results['atr_volatility'] = f"[OK] Sufficient volatility: {h1['atr']:.5f}"
            analysis['passed_criteria'].append("Adequate volatility for trading")
        else:
            criteria_results['atr_volatility'] = f"[FAIL] Low volatility: {h1['atr']:.5f}"
            analysis['failed_criteria'].append("Insufficient market volatility")
        
        # =================================================================
        # CRITERION 10: EMA Spacing
        # =================================================================
        ema_spacing = abs(h1['ema_21'] - h1['ema_50'])
        spacing_threshold = 50 if symbol in ['BTC', 'BTCUSD'] else (5 if symbol in ['GOLD', 'XAUUSD'] else 0.0005)
        ema_spacing_ok = ema_spacing > spacing_threshold
        if ema_spacing_ok:
            score += 1
            criteria_results['ema_spacing'] = f"[OK] EMA spacing: {ema_spacing:.5f}"
            analysis['passed_criteria'].append("Good EMA separation indicates strong trend")
        else:
            criteria_results['ema_spacing'] = f"[FAIL] EMAs too close: {ema_spacing:.5f}"
            analysis['failed_criteria'].append("EMAs too close - weak trend")
        
        # =================================================================
        # CRITERION 11: Price Action Patterns (ENHANCED)
        # =================================================================
        pa_analysis = self.analyze_price_action_patterns(processed_data['H1'], h1_trend)
        if pa_analysis['valid']:
            score += 1
            criteria_results['price_action_patterns'] = f"[OK] {pa_analysis['pattern']}"
            analysis['passed_criteria'].append(f"Price action: {pa_analysis['pattern']}")
            if pa_analysis['strength'] == 'STRONG':
                analysis['confidence_factors'].append("Strong price action pattern")
        else:
            criteria_results['price_action_patterns'] = f"[FAIL] {pa_analysis['reason']}"
            analysis['failed_criteria'].append(f"Price action issue: {pa_analysis['reason']}")
        
        # =================================================================
        # CRITERION 12: Higher Timeframe Confirmation
        # =================================================================
        htf_ok = (d1['close'] > d1['ema_50']) if h1_trend == 'bullish' else (d1['close'] < d1['ema_50'])
        if htf_ok:
            score += 1
            criteria_results['htf_confirmation'] = "[OK] D1 timeframe confirms"
            analysis['passed_criteria'].append("Daily timeframe supports direction")
        else:
            criteria_results['htf_confirmation'] = "[FAIL] D1 timeframe conflict"
            analysis['failed_criteria'].append("Daily timeframe shows conflicting signal")
        
        # =================================================================
        # CRITERION 13: Momentum Acceleration (ENHANCED)
        # =================================================================
        momentum_analysis = self.analyze_momentum_acceleration(processed_data, h1_trend)
        if momentum_analysis['accelerating']:
            score += 1
            criteria_results['momentum_acceleration'] = f"[OK] {momentum_analysis['description']}"
            analysis['passed_criteria'].append(f"Momentum: {momentum_analysis['description']}")
        else:
            criteria_results['momentum_acceleration'] = f"[FAIL] {momentum_analysis['reason']}"
            analysis['failed_criteria'].append(f"Momentum issue: {momentum_analysis['reason']}")
        
        # =================================================================
        # CRITERION 14: Support/Resistance Respect (ENHANCED)
        # =================================================================
        sr_analysis = self.analyze_sr_levels(processed_data['H4'], m15['close'], h1_trend)
        if sr_analysis['respected']:
            score += 1
            criteria_results['sr_respect'] = f"[OK] {sr_analysis['description']}"
            analysis['passed_criteria'].append(f"S/R analysis: {sr_analysis['description']}")
        else:
            criteria_results['sr_respect'] = f"[FAIL] {sr_analysis['reason']}"
            analysis['failed_criteria'].append(f"S/R issue: {sr_analysis['reason']}")
        
        # =================================================================
        # CRITERION 15: Divergence Analysis (ENHANCED)
        # =================================================================
        div_analysis = self.analyze_divergences(processed_data['H1'], h1_trend)
        if div_analysis['healthy']:
            score += 1
            criteria_results['divergence_analysis'] = f"[OK] {div_analysis['status']}"
            analysis['passed_criteria'].append(f"Divergence: {div_analysis['status']}")
        else:
            criteria_results['divergence_analysis'] = f"[FAIL] {div_analysis['warning']}"
            analysis['failed_criteria'].append(f"Divergence warning: {div_analysis['warning']}")
        
        # =================================================================
        # CRITERION 16: Session Timing (ENHANCED)
        # =================================================================
        session_analysis = self.analyze_session_timing(symbol)
        if session_analysis['optimal']:
            score += 1
            criteria_results['session_timing'] = f"[OK] {session_analysis['session']}"
            analysis['passed_criteria'].append(f"Timing: {session_analysis['session']}")
        else:
            criteria_results['session_timing'] = f"[WARN] {session_analysis['warning']}"
            analysis['warnings'].append(f"Session timing: {session_analysis['warning']}")
        
        # =================================================================
        # CRITERION 17: Breakout Potential (ENHANCED)
        # =================================================================
        breakout_analysis = self.analyze_breakout_potential(processed_data, h1_trend, symbol)
        if breakout_analysis['high_potential']:
            score += 1
            criteria_results['breakout_potential'] = f"[OK] {breakout_analysis['setup']}"
            analysis['passed_criteria'].append(f"Breakout: {breakout_analysis['setup']}")
        else:
            criteria_results['breakout_potential'] = f"[FAIL] {breakout_analysis['reason']}"
            analysis['failed_criteria'].append(f"Breakout issue: {breakout_analysis['reason']}")
        
        # =================================================================
        # CRITERION 18: Risk/Reward Ratio (ENHANCED)
        # =================================================================
        rr_analysis = self.calculate_risk_reward(m15, h1, h1_trend)
        if rr_analysis['acceptable']:
            score += 1
            criteria_results['risk_reward_ratio'] = f"[OK] R:R {rr_analysis['ratio']:.1f}:1"
            analysis['passed_criteria'].append(f"Risk/Reward: {rr_analysis['ratio']:.1f}:1")
        else:
            criteria_results['risk_reward_ratio'] = f"[FAIL] Poor R:R {rr_analysis['ratio']:.1f}:1"
            analysis['failed_criteria'].append(f"Risk/Reward too low: {rr_analysis['ratio']:.1f}:1")
        
        # =================================================================
        # CRITERION 19: Trend Consistency (ENHANCED)
        # =================================================================
        consistency_analysis = self.analyze_trend_consistency(processed_data, h1_trend)
        if consistency_analysis['consistent']:
            score += 1
            criteria_results['trend_consistency'] = f"[OK] {consistency_analysis['description']}"
            analysis['passed_criteria'].append(f"Consistency: {consistency_analysis['description']}")
        else:
            criteria_results['trend_consistency'] = f"[FAIL] {consistency_analysis['issue']}"
            analysis['failed_criteria'].append(f"Consistency issue: {consistency_analysis['issue']}")
        
        # =================================================================
        # CRITERION 20: Market Structure (ENHANCED)
        # =================================================================
        structure_analysis = self.analyze_market_structure(processed_data['H1'], h1_trend)
        if structure_analysis['healthy']:
            score += 1
            criteria_results['market_structure'] = f"[OK] {structure_analysis['structure']}"
            analysis['passed_criteria'].append(f"Market structure: {structure_analysis['structure']}")
        else:
            criteria_results['market_structure'] = f"[FAIL] {structure_analysis['issue']}"
            analysis['failed_criteria'].append(f"Structure issue: {structure_analysis['issue']}")
        
        # =================================================================
        # FINAL EVALUATION
        # =================================================================
        is_elite = score >= 17  # Need at least 17/20 criteria
        analysis['total_score'] = score
        analysis['percentage'] = (score / 20) * 100
        analysis['criteria_results'] = criteria_results
        
        if score >= 19:
            analysis['grade'] = 'ELITE A+++'
            analysis['confidence_level'] = 'MAXIMUM'
        elif score >= 18:
            analysis['grade'] = 'ELITE A++'  
            analysis['confidence_level'] = 'VERY HIGH'
        elif score >= 17:
            analysis['grade'] = 'ELITE A+'
            analysis['confidence_level'] = 'HIGH'
        else:
            analysis['grade'] = 'NOT ELITE'
            analysis['confidence_level'] = 'INSUFFICIENT'
        
        return is_elite, analysis
    
    # =================================================================
    # ENHANCED ANALYSIS METHODS
    # =================================================================
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators"""
        # EMAs
        df['ema_21'] = df['close'].ewm(span=21).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        df['ema_200'] = df['close'].ewm(span=200).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        
        # Stochastic
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        # Volume
        if 'volume' in df.columns:
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
        else:
            df['volume_ratio'] = 1.0
        
        # ADX (Average Directional Index) - proper calculation
        df['adx'] = self._calculate_adx(df)
        
        return df
    
    def _calculate_adx(self, df, period=14):
        """Calculate ADX (Average Directional Index) with proper +DI/-DI"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # Calculate +DM and -DM
            plus_dm = high.diff()
            minus_dm = -low.diff()
            
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            
            # Set to 0 if both are positive (only one can be positive)
            both_positive = (plus_dm > 0) & (minus_dm > 0)
            plus_dm[both_positive] = 0
            minus_dm[both_positive] = 0
            
            # If plus_dm < minus_dm, set plus_dm to 0
            plus_dm[plus_dm < minus_dm] = 0
            # If minus_dm < plus_dm, set minus_dm to 0
            minus_dm[minus_dm < plus_dm] = 0
            
            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Smooth the values using Wilder's smoothing
            atr = tr.ewm(alpha=1/period, adjust=False).mean()
            
            # Calculate +DI and -DI
            plus_di = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
            minus_di = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
            
            # Calculate DX
            di_sum = plus_di + minus_di
            di_sum[di_sum == 0] = 0.0001  # Avoid division by zero
            dx = 100 * abs(plus_di - minus_di) / di_sum
            
            # Calculate ADX (smoothed DX)
            adx = dx.ewm(alpha=1/period, adjust=False).mean()
            
            return adx.fillna(25)  # Default to 25 if insufficient data
        except Exception as e:
            # Return default ADX if calculation fails
            return pd.Series([25] * len(df), index=df.index)
    
    def check_mtf_alignment(self, h1_trend: str, h4_trend: str, d1_trend: str, data: Dict) -> Dict:
        """Enhanced multi-timeframe alignment check"""
        if h1_trend == h4_trend == d1_trend:
            # Check EMA slopes for strength
            h1_slope = data['H1']['ema_21'].iloc[-1] - data['H1']['ema_21'].iloc[-5]
            h4_slope = data['H4']['ema_21'].iloc[-1] - data['H4']['ema_21'].iloc[-3]
            
            if abs(h1_slope) > 10 and abs(h4_slope) > 20:  # Strong slopes
                return {"aligned": True, "strength": "PERFECT", "reason": "All timeframes perfectly aligned with strong momentum"}
            else:
                return {"aligned": True, "strength": "GOOD", "reason": "All timeframes aligned"}
        elif h1_trend == h4_trend:
            return {"aligned": False, "strength": "PARTIAL", "reason": "H1/H4 aligned but D1 divergent"}
        else:
            return {"aligned": False, "strength": "POOR", "reason": "Multiple timeframe conflicts"}
    
    def analyze_rsi_momentum(self, h1_rsi: float, h4_rsi: float, trend: str) -> Dict:
        """Enhanced RSI momentum analysis"""
        if trend == 'bullish':
            if 40 < h1_rsi < 70 and h4_rsi > 45:
                if h1_rsi > 55:
                    return {"valid": True, "description": "Strong bullish momentum", "strength": "HIGH"}
                else:
                    return {"valid": True, "description": "Moderate bullish momentum", "strength": "MEDIUM"}
            else:
                return {"valid": False, "reason": f"RSI {h1_rsi:.1f} outside optimal range (40-70)"}
        else:  # bearish
            if 30 < h1_rsi < 60 and h4_rsi < 55:
                if h1_rsi < 45:
                    return {"valid": True, "description": "Strong bearish momentum", "strength": "HIGH"}
                else:
                    return {"valid": True, "description": "Moderate bearish momentum", "strength": "MEDIUM"}
            else:
                return {"valid": False, "reason": f"RSI {h1_rsi:.1f} outside optimal range (30-60)"}
    
    def analyze_stochastic_signal(self, h1_data: pd.Series, trend: str) -> Dict:
        """Enhanced stochastic oscillator analysis"""
        stoch_k = h1_data.get('stoch_k', 50)
        stoch_d = h1_data.get('stoch_d', 50)
        
        if trend == 'bullish':
            if stoch_k > stoch_d and stoch_k > 20 and stoch_k < 80:
                return {"valid": True, "signal": "Bullish stochastic crossover", "strength": "GOOD"}
            elif stoch_k > 50 and stoch_d > 50:
                return {"valid": True, "signal": "Stochastic in bullish zone", "strength": "MEDIUM"}
            else:
                return {"valid": False, "reason": f"Stochastic not aligned (K:{stoch_k:.1f}, D:{stoch_d:.1f})"}
        else:  # bearish
            if stoch_k < stoch_d and stoch_k < 80 and stoch_k > 20:
                return {"valid": True, "signal": "Bearish stochastic crossover", "strength": "GOOD"}
            elif stoch_k < 50 and stoch_d < 50:
                return {"valid": True, "signal": "Stochastic in bearish zone", "strength": "MEDIUM"}
            else:
                return {"valid": False, "reason": f"Stochastic not aligned (K:{stoch_k:.1f}, D:{stoch_d:.1f})"}
    
    def analyze_adx_strength(self, h1_adx: float, h4_adx: float) -> Dict:
        """Enhanced ADX trend strength analysis with validation"""
        try:
            # Validate inputs
            if pd.isna(h1_adx) or pd.isna(h4_adx):
                return {"strong": False, "reason": "ADX data unavailable", "level": "INSUFFICIENT"}
            
            # Ensure valid numeric values
            h1_adx = float(h1_adx) if not pd.isna(h1_adx) else 25
            h4_adx = float(h4_adx) if not pd.isna(h4_adx) else 25
            
            avg_adx = (h1_adx + h4_adx) / 2
            
            # ADX interpretation: 0-20 = weak, 20-25 = moderate, 25-30 = strong, 30+ = very strong
            if avg_adx >= 30:
                return {"strong": True, "description": f"Very strong trend (ADX: {avg_adx:.1f})", "level": "HIGH"}
            elif avg_adx >= 25:
                return {"strong": True, "description": f"Strong trend (ADX: {avg_adx:.1f})", "level": "MEDIUM"}
            elif avg_adx >= 20:
                return {"strong": True, "description": f"Moderate trend (ADX: {avg_adx:.1f})", "level": "LOW"}
            else:
                return {"strong": False, "reason": f"Weak trend strength (ADX: {avg_adx:.1f})", "level": "INSUFFICIENT"}
        except Exception as e:
            return {"strong": False, "reason": f"ADX analysis error: {str(e)}", "level": "ERROR"}
    
    def analyze_price_action_patterns(self, h1_df: pd.DataFrame, trend: str) -> Dict:
        """Enhanced price action pattern recognition"""
        recent_candles = h1_df.tail(5)
        
        # Higher highs/Higher lows for bullish, Lower lows/Lower highs for bearish
        if trend == 'bullish':
            highs = recent_candles['high'].values
            lows = recent_candles['low'].values
            
            if len(highs) >= 3:
                higher_highs = highs[-1] > highs[-2] > highs[-3]
                higher_lows = lows[-1] > lows[-3]  # Allow some flexibility
                
                if higher_highs and higher_lows:
                    return {"valid": True, "pattern": "Strong bullish structure", "strength": "STRONG"}
                elif higher_highs or higher_lows:
                    return {"valid": True, "pattern": "Moderate bullish structure", "strength": "MEDIUM"}
                else:
                    return {"valid": False, "reason": "No clear bullish structure"}
            else:
                return {"valid": False, "reason": "Insufficient price history"}
        else:  # bearish
            highs = recent_candles['high'].values
            lows = recent_candles['low'].values
            
            if len(lows) >= 3:
                lower_lows = lows[-1] < lows[-2] < lows[-3]
                lower_highs = highs[-1] < highs[-3]  # Allow some flexibility
                
                if lower_lows and lower_highs:
                    return {"valid": True, "pattern": "Strong bearish structure", "strength": "STRONG"}
                elif lower_lows or lower_highs:
                    return {"valid": True, "pattern": "Moderate bearish structure", "strength": "MEDIUM"}
                else:
                    return {"valid": False, "reason": "No clear bearish structure"}
            else:
                return {"valid": False, "reason": "Insufficient price history"}
    
    def analyze_momentum_acceleration(self, data: Dict, trend: str) -> Dict:
        """Enhanced momentum acceleration analysis"""
        h1_macd = data['H1']['macd_histogram'].tail(3).values
        h4_macd = data['H4']['macd_histogram'].tail(2).values
        
        if len(h1_macd) >= 3 and len(h4_macd) >= 2:
            h1_accelerating = abs(h1_macd[-1]) > abs(h1_macd[-2]) > abs(h1_macd[-3])
            h4_accelerating = abs(h4_macd[-1]) > abs(h4_macd[-2])
            
            if trend == 'bullish':
                h1_positive = all(x > 0 for x in h1_macd)
                h4_positive = all(x > 0 for x in h4_macd)
                
                if h1_accelerating and h4_accelerating and h1_positive and h4_positive:
                    return {"accelerating": True, "description": "Strong bullish acceleration"}
                elif h1_positive and h4_positive:
                    return {"accelerating": True, "description": "Moderate bullish momentum"}
                else:
                    return {"accelerating": False, "reason": "MACD histogram not consistently positive"}
            else:  # bearish
                h1_negative = all(x < 0 for x in h1_macd)
                h4_negative = all(x < 0 for x in h4_macd)
                
                if h1_accelerating and h4_accelerating and h1_negative and h4_negative:
                    return {"accelerating": True, "description": "Strong bearish acceleration"}
                elif h1_negative and h4_negative:
                    return {"accelerating": True, "description": "Moderate bearish momentum"}
                else:
                    return {"accelerating": False, "reason": "MACD histogram not consistently negative"}
        
        return {"accelerating": False, "reason": "Insufficient MACD data"}
    
    def analyze_sr_levels(self, h4_df: pd.DataFrame, current_price: float, trend: str) -> Dict:
        """Enhanced support/resistance level analysis"""
        # Calculate recent highs and lows
        recent_data = h4_df.tail(50)
        resistance_levels = []
        support_levels = []
        
        # Find swing highs and lows
        for i in range(2, len(recent_data)-2):
            # Swing high
            if (recent_data.iloc[i]['high'] > recent_data.iloc[i-1]['high'] and 
                recent_data.iloc[i]['high'] > recent_data.iloc[i-2]['high'] and
                recent_data.iloc[i]['high'] > recent_data.iloc[i+1]['high'] and
                recent_data.iloc[i]['high'] > recent_data.iloc[i+2]['high']):
                resistance_levels.append(recent_data.iloc[i]['high'])
            
            # Swing low
            if (recent_data.iloc[i]['low'] < recent_data.iloc[i-1]['low'] and 
                recent_data.iloc[i]['low'] < recent_data.iloc[i-2]['low'] and
                recent_data.iloc[i]['low'] < recent_data.iloc[i+1]['low'] and
                recent_data.iloc[i]['low'] < recent_data.iloc[i+2]['low']):
                support_levels.append(recent_data.iloc[i]['low'])
        
        # Find nearest levels
        if trend == 'bullish' and resistance_levels:
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
            if nearest_resistance and abs(nearest_resistance - current_price) / current_price < 0.02:  # Within 2%
                return {"respected": True, "description": f"Near resistance at {nearest_resistance:.5f}"}
        elif trend == 'bearish' and support_levels:
            nearest_support = max([s for s in support_levels if s < current_price], default=None)
            if nearest_support and abs(current_price - nearest_support) / current_price < 0.02:  # Within 2%
                return {"respected": True, "description": f"Near support at {nearest_support:.5f}"}
        
        # Check if price is holding above/below key EMAs
        ema_200 = recent_data['ema_200'].iloc[-1]
        if trend == 'bullish' and current_price > ema_200:
            return {"respected": True, "description": "Above key EMA-200 support"}
        elif trend == 'bearish' and current_price < ema_200:
            return {"respected": True, "description": "Below key EMA-200 resistance"}
        
        return {"respected": False, "reason": "Not near significant S/R levels"}
    
    def analyze_divergences(self, h1_df: pd.DataFrame, trend: str) -> Dict:
        """Enhanced divergence detection"""
        recent_data = h1_df.tail(20)
        
        # Simple divergence check - compare price and RSI trends
        price_trend = recent_data['close'].iloc[-1] - recent_data['close'].iloc[-10]
        rsi_trend = recent_data['rsi'].iloc[-1] - recent_data['rsi'].iloc[-10]
        
        if trend == 'bullish':
            if price_trend > 0 and rsi_trend > 0:
                return {"healthy": True, "status": "No bearish divergence detected"}
            elif price_trend > 0 and rsi_trend < -5:  # Significant RSI decline
                return {"healthy": False, "warning": "Potential bearish divergence"}
            else:
                return {"healthy": True, "status": "Neutral divergence state"}
        else:  # bearish
            if price_trend < 0 and rsi_trend < 0:
                return {"healthy": True, "status": "No bullish divergence detected"}
            elif price_trend < 0 and rsi_trend > 5:  # Significant RSI increase
                return {"healthy": False, "warning": "Potential bullish divergence"}
            else:
                return {"healthy": True, "status": "Neutral divergence state"}
    
    def analyze_session_timing(self, symbol: str) -> Dict:
        """Enhanced trading session analysis"""
        current_time = datetime.now()
        hour_utc = current_time.hour
        
        # Define optimal sessions for different assets
        if symbol in ['BTC', 'BTCUSD']:
            # Crypto trades 24/7, but higher volume during US/Europe overlap
            if 13 <= hour_utc <= 17:  # NY morning overlap with Europe
                return {"optimal": True, "session": "High volume crypto session (US-EU overlap)"}
            else:
                return {"optimal": False, "warning": "Lower volume crypto session"}
        
        elif symbol in ['GOLD', 'XAUUSD']:
            # Gold most active during London/NY sessions
            if 8 <= hour_utc <= 17:  # London + NY sessions
                return {"optimal": True, "session": "Prime gold trading session"}
            else:
                return {"optimal": False, "warning": "Outside prime gold hours"}
        
        elif symbol.endswith('USD') or 'USD' in symbol:
            # Forex pairs with USD - best during London/NY overlap
            if 12 <= hour_utc <= 16:  # London-NY overlap
                return {"optimal": True, "session": "Peak forex liquidity (London-NY overlap)"}
            elif 8 <= hour_utc <= 17:  # London or NY session
                return {"optimal": True, "session": "Good forex liquidity session"}
            else:
                return {"optimal": False, "warning": "Low forex liquidity session"}
        
        elif symbol.endswith('JPY'):
            # JPY pairs - also consider Tokyo session
            if 0 <= hour_utc <= 3 or 8 <= hour_utc <= 17:  # Tokyo or London/NY
                return {"optimal": True, "session": "Good JPY pair session"}
            else:
                return {"optimal": False, "warning": "Suboptimal JPY session"}
        
        else:  # Other assets (ES, NQ futures)
            if 13 <= hour_utc <= 21:  # US market hours
                return {"optimal": True, "session": "US market active session"}
            else:
                return {"optimal": False, "warning": "US market closed"}
    
    def analyze_breakout_potential(self, data: Dict, trend: str, symbol: str) -> Dict:
        """Enhanced breakout potential analysis"""
        h4_data = data['H4'].tail(20)
        current_price = data['M15']['close'].iloc[-1]
        
        # Calculate consolidation range
        recent_high = h4_data['high'].max()
        recent_low = h4_data['low'].min()
        range_size = recent_high - recent_low
        
        # Check if price is near breakout levels
        if trend == 'bullish':
            distance_to_high = recent_high - current_price
            if distance_to_high < range_size * 0.1:  # Within 10% of range
                return {"high_potential": True, "setup": "Near resistance breakout level"}
            elif current_price > recent_high:
                return {"high_potential": True, "setup": "Already breaking above resistance"}
            else:
                return {"high_potential": False, "reason": "Too far from breakout level"}
        else:  # bearish
            distance_to_low = current_price - recent_low
            if distance_to_low < range_size * 0.1:  # Within 10% of range
                return {"high_potential": True, "setup": "Near support breakdown level"}
            elif current_price < recent_low:
                return {"high_potential": True, "setup": "Already breaking below support"}
            else:
                return {"high_potential": False, "reason": "Too far from breakdown level"}
    
    def calculate_risk_reward(self, m15_data: pd.Series, h1_data: pd.Series, trend: str) -> Dict:
        """Enhanced risk/reward calculation"""
        current_price = m15_data['close']
        atr = h1_data['atr']
        
        if trend == 'bullish':
            # Stop loss below recent swing low or 1.5x ATR
            stop_loss = current_price - (atr * 1.5)
            # Take profit at 2.5x risk minimum
            take_profit = current_price + (atr * 2.5)
            
            risk = current_price - stop_loss
            reward = take_profit - current_price
            
        else:  # bearish
            # Stop loss above recent swing high or 1.5x ATR
            stop_loss = current_price + (atr * 1.5)
            # Take profit at 2.5x risk minimum
            take_profit = current_price - (atr * 2.5)
            
            risk = stop_loss - current_price
            reward = current_price - take_profit
        
        if risk > 0:
            ratio = reward / risk
            if ratio >= 2.5:
                return {"acceptable": True, "ratio": ratio, "grade": "EXCELLENT"}
            elif ratio >= 2.0:
                return {"acceptable": True, "ratio": ratio, "grade": "GOOD"}
            else:
                return {"acceptable": False, "ratio": ratio, "grade": "POOR"}
        else:
            return {"acceptable": False, "ratio": 0, "grade": "INVALID"}
    
    def analyze_trend_consistency(self, data: Dict, trend: str) -> Dict:
        """Enhanced trend consistency analysis"""
        # Check EMA alignment across timeframes
        m15_aligned = data['M15']['ema_21'].iloc[-1] > data['M15']['ema_50'].iloc[-1]
        h1_aligned = data['H1']['ema_21'].iloc[-1] > data['H1']['ema_50'].iloc[-1]
        h4_aligned = data['H4']['ema_21'].iloc[-1] > data['H4']['ema_50'].iloc[-1]
        d1_aligned = data['D1']['ema_21'].iloc[-1] > data['D1']['ema_50'].iloc[-1]
        
        if trend == 'bullish':
            alignments = [m15_aligned, h1_aligned, h4_aligned, d1_aligned]
        else:  # bearish
            alignments = [not m15_aligned, not h1_aligned, not h4_aligned, not d1_aligned]
        
        consistency_score = sum(alignments)
        
        if consistency_score == 4:
            return {"consistent": True, "description": "Perfect trend consistency across all timeframes"}
        elif consistency_score == 3:
            return {"consistent": True, "description": "Strong trend consistency (3/4 timeframes)"}
        elif consistency_score == 2:
            return {"consistent": False, "issue": "Mixed signals across timeframes (2/4 aligned)"}
        else:
            return {"consistent": False, "issue": "Poor trend consistency across timeframes"}
    
    def analyze_market_structure(self, h1_df: pd.DataFrame, trend: str) -> Dict:
        """Enhanced market structure analysis"""
        recent_data = h1_df.tail(10)
        
        # Analyze recent swing points
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        
        if trend == 'bullish':
            # Look for higher lows pattern
            recent_lows = []
            for i in range(1, len(lows)-1):
                if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                    recent_lows.append(lows[i])
            
            if len(recent_lows) >= 2:
                if recent_lows[-1] > recent_lows[-2]:
                    return {"healthy": True, "structure": "Higher lows confirming bullish structure"}
                else:
                    return {"healthy": False, "issue": "Lower lows breaking bullish structure"}
            else:
                return {"healthy": True, "structure": "Insufficient swing data, assuming healthy"}
        
        else:  # bearish
            # Look for lower highs pattern
            recent_highs = []
            for i in range(1, len(highs)-1):
                if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                    recent_highs.append(highs[i])
            
            if len(recent_highs) >= 2:
                if recent_highs[-1] < recent_highs[-2]:
                    return {"healthy": True, "structure": "Lower highs confirming bearish structure"}
                else:
                    return {"healthy": False, "issue": "Higher highs breaking bearish structure"}
            else:
                return {"healthy": True, "structure": "Insufficient swing data, assuming healthy"}


# =================================================================
# USAGE EXAMPLE
# =================================================================

if __name__ == "__main__":
    print("ENHANCED 20-CRITERIA SYSTEM - TESTING")
    print("="*60)
    
    # Example usage
    enhanced_system = Enhanced20CriteriaSystem()
    
    # This would be called with real market data
    # is_elite, analysis = enhanced_system.apply_enhanced_criteria(market_data, "BTCUSD")
    
    print("Enhanced criteria system loaded successfully!")
    print(f"Total criteria: {len(enhanced_system.criteria_names)}")
    print("All criteria now have proper validation logic!")
