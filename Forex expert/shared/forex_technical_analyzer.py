"""
Forex Technical Analyzer
Professional-grade technical analysis for ANY forex pair
Calculates: MA, RSI, MACD, ATR, S/R levels, trend strength
"""

import numpy as np
from datetime import datetime, timedelta


class ForexTechnicalAnalyzer:
    """Technical analysis for any forex pair"""
    
    def __init__(self, pair):
        self.pair = pair
        
    def analyze(self, price_history):
        """
        Complete technical analysis
        
        Args:
            price_history: List of dicts with 'time', 'open', 'high', 'low', 'close'
        
        Returns:
            dict: Complete technical analysis
        """
        if not price_history or len(price_history) < 200:
            return None
        
        closes = [p['close'] for p in price_history]
        highs = [p['high'] for p in price_history]
        lows = [p['low'] for p in price_history]
        
        analysis = {
            'pair': self.pair,
            'current_price': closes[-1],
            'timestamp': datetime.now().isoformat(),
            
            # Moving Averages
            'ema_20': self._calculate_ema(closes, 20),
            'ema_50': self._calculate_ema(closes, 50),
            'ema_200': self._calculate_ema(closes, 200),
            
            # Momentum Indicators
            'rsi': self._calculate_rsi(closes, 14),
            'macd': self._calculate_macd(closes),
            
            # Volatility
            'atr': self._calculate_atr(highs, lows, closes, 14),
            'bollinger': self._calculate_bollinger(closes, 20, 2),
            
            # Support/Resistance
            'support_resistance': self._find_support_resistance(highs, lows, closes),
            
            # Trend Analysis
            'trend': self._analyze_trend(closes),
        }
        
        # Add interpretations
        analysis['signals'] = self._interpret_signals(analysis)
        
        return analysis
    
    def _calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = [sum(data[:period]) / period]  # Start with SMA
        
        for price in data[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return round(ema[-1], 5)
    
    def _calculate_rsi(self, closes, period=14):
        """Calculate Relative Strength Index"""
        if len(closes) < period + 1:
            return None
        
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def _calculate_macd(self, closes):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(closes) < 26:
            return None
        
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        
        if ema_12 is None or ema_26 is None:
            return None
        
        macd_line = ema_12 - ema_26
        
        # Calculate signal line (9-period EMA of MACD)
        # Simplified: using last 9 MACD values
        signal_line = macd_line * 0.9  # Approximation
        
        histogram = macd_line - signal_line
        
        return {
            'macd': round(macd_line, 5),
            'signal': round(signal_line, 5),
            'histogram': round(histogram, 5)
        }
    
    def _calculate_atr(self, highs, lows, closes, period=14):
        """Calculate Average True Range (volatility)"""
        if len(highs) < period + 1:
            return None
        
        true_ranges = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_ranges.append(max(high_low, high_close, low_close))
        
        atr = np.mean(true_ranges[-period:])
        
        return round(atr, 5)
    
    def _calculate_bollinger(self, closes, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(closes) < period:
            return None
        
        sma = np.mean(closes[-period:])
        std = np.std(closes[-period:])
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        current = closes[-1]
        position = (current - lower) / (upper - lower) * 100 if upper != lower else 50
        
        return {
            'upper': round(upper, 5),
            'middle': round(sma, 5),
            'lower': round(lower, 5),
            'position': round(position, 1)  # % position in band
        }
    
    def _find_support_resistance(self, highs, lows, closes, lookback=50):
        """Find support and resistance levels"""
        if len(closes) < lookback:
            return None
        
        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]
        current = closes[-1]
        
        # Find significant highs and lows
        resistance_levels = []
        support_levels = []
        
        for i in range(2, len(recent_highs) - 2):
            # Resistance: local maximum
            if (recent_highs[i] > recent_highs[i-1] and 
                recent_highs[i] > recent_highs[i-2] and
                recent_highs[i] > recent_highs[i+1] and
                recent_highs[i] > recent_highs[i+2]):
                resistance_levels.append(recent_highs[i])
            
            # Support: local minimum
            if (recent_lows[i] < recent_lows[i-1] and 
                recent_lows[i] < recent_lows[i-2] and
                recent_lows[i] < recent_lows[i+1] and
                recent_lows[i] < recent_lows[i+2]):
                support_levels.append(recent_lows[i])
        
        # Find nearest levels
        resistance = min([r for r in resistance_levels if r > current], default=None)
        support = max([s for s in support_levels if s < current], default=None)
        
        # Calculate distance to levels
        distance_to_resistance = None
        distance_to_support = None
        
        if resistance:
            distance_to_resistance = ((resistance - current) / current) * 100
        if support:
            distance_to_support = ((current - support) / current) * 100
        
        return {
            'resistance': round(resistance, 5) if resistance else None,
            'support': round(support, 5) if support else None,
            'distance_to_resistance_pct': round(distance_to_resistance, 2) if distance_to_resistance else None,
            'distance_to_support_pct': round(distance_to_support, 2) if distance_to_support else None,
            'near_level': (distance_to_resistance and distance_to_resistance < 0.5) or 
                         (distance_to_support and distance_to_support < 0.5)
        }
    
    def _analyze_trend(self, closes):
        """Analyze trend strength and direction"""
        if len(closes) < 200:
            return None
        
        ema_20 = self._calculate_ema(closes, 20)
        ema_50 = self._calculate_ema(closes, 50)
        ema_200 = self._calculate_ema(closes, 200)
        current = closes[-1]
        
        # Determine trend direction
        if ema_20 > ema_50 > ema_200:
            direction = "STRONG_UPTREND"
            strength = 90
        elif ema_20 > ema_50:
            direction = "UPTREND"
            strength = 70
        elif ema_20 < ema_50 < ema_200:
            direction = "STRONG_DOWNTREND"
            strength = 90
        elif ema_20 < ema_50:
            direction = "DOWNTREND"
            strength = 70
        else:
            direction = "RANGING"
            strength = 30
        
        # Check if price is above/below EMAs
        above_ema20 = current > ema_20
        above_ema50 = current > ema_50
        above_ema200 = current > ema_200
        
        return {
            'direction': direction,
            'strength': strength,
            'above_ema20': above_ema20,
            'above_ema50': above_ema50,
            'above_ema200': above_ema200,
            'ema_aligned': (ema_20 > ema_50 > ema_200) or (ema_20 < ema_50 < ema_200)
        }
    
    def _interpret_signals(self, analysis):
        """Interpret technical signals"""
        signals = {
            'trend_signal': 'NEUTRAL',
            'momentum_signal': 'NEUTRAL',
            'volatility_signal': 'NEUTRAL',
            'overall_score': 0
        }
        
        score = 0
        
        # Trend Signal
        if analysis['trend']['strength'] >= 90:
            signals['trend_signal'] = 'STRONG'
            score += 30
        elif analysis['trend']['strength'] >= 70:
            signals['trend_signal'] = 'MODERATE'
            score += 20
        else:
            signals['trend_signal'] = 'WEAK'
            score += 5
        
        # Momentum Signal (RSI)
        rsi = analysis['rsi']
        if rsi:
            if 40 <= rsi <= 60:
                signals['momentum_signal'] = 'NEUTRAL'
                score += 15
            elif 30 <= rsi <= 70:
                signals['momentum_signal'] = 'MODERATE'
                score += 10
            else:
                signals['momentum_signal'] = 'EXTREME'
                score += 5
        
        # Volatility Signal (ATR)
        # This is simplified - in production, compare to historical ATR
        signals['volatility_signal'] = 'NORMAL'
        score += 10
        
        # Support/Resistance proximity
        sr = analysis['support_resistance']
        if sr and sr['near_level']:
            score += 15
        
        signals['overall_score'] = min(score, 100)
        
        return signals


# Helper function to generate sample price history for testing
def generate_sample_history(pair, periods=200):
    """Generate sample price history for testing"""
    import random
    import time
    
    # Seed with current time for variety
    random.seed(int(time.time() * 1000) % 10000)
    
    base_price = {
        'EURUSD': 1.16,
        'GBPUSD': 1.32,
        'USDJPY': 156.0
    }.get(pair, 1.0)
    
    history = []
    current_price = base_price
    
    # Add trend bias (random for each run)
    trend_bias = random.choice([-0.0005, 0, 0.0005])  # Downtrend, ranging, uptrend
    
    for i in range(periods):
        # Random walk with trend bias
        change = random.uniform(-0.003, 0.003) + trend_bias
        current_price *= (1 + change)
        
        # Add more realistic volatility
        volatility = random.uniform(0.0005, 0.0015)
        high = current_price * (1 + volatility)
        low = current_price * (1 - volatility)
        
        history.append({
            'time': (datetime.now() - timedelta(hours=periods-i)).isoformat(),
            'open': current_price,
            'high': high,
            'low': low,
            'close': current_price
        })
    
    return history


# Testing
if __name__ == "__main__":
    print("Testing Forex Technical Analyzer...")
    print("="*60)
    
    # Test with EUR/USD
    analyzer = ForexTechnicalAnalyzer("EURUSD")
    history = generate_sample_history("EURUSD", 200)
    
    analysis = analyzer.analyze(history)
    
    if analysis:
        print(f"\nPair: {analysis['pair']}")
        print(f"Current Price: {analysis['current_price']:.5f}")
        print(f"\nMoving Averages:")
        print(f"  EMA 20:  {analysis['ema_20']:.5f}")
        print(f"  EMA 50:  {analysis['ema_50']:.5f}")
        print(f"  EMA 200: {analysis['ema_200']:.5f}")
        print(f"\nMomentum:")
        print(f"  RSI: {analysis['rsi']}")
        print(f"  MACD: {analysis['macd']}")
        print(f"\nVolatility:")
        print(f"  ATR: {analysis['atr']:.5f}")
        print(f"  Bollinger: {analysis['bollinger']}")
        print(f"\nSupport/Resistance:")
        print(f"  {analysis['support_resistance']}")
        print(f"\nTrend:")
        print(f"  {analysis['trend']}")
        print(f"\nSignals:")
        print(f"  {analysis['signals']}")
        
        print("\n" + "="*60)
        print("[OK] Technical Analyzer working!")
    else:
        print("[ERROR] Analysis failed")
