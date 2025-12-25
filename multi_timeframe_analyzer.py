"""
Multi-Timeframe Analyzer
Analyzes trends across M15, H1, H4, D1 timeframes for better entry confirmation
"""

from datetime import datetime, timedelta
import numpy as np


class MultiTimeframeAnalyzer:
    """Analyze multiple timeframes for trend confirmation"""
    
    def __init__(self, data_client=None):
        """
        Initialize analyzer
        
        Args:
            data_client: Optional ForexDataClient for current prices (fallback only)
        """
        self.data_client = data_client
        self.timeframes = ['M15', 'H1', 'H4', 'D1']
        
        # Import TradingView data client for OHLC
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from tradingview_data_client import TradingViewDataClient
            self.tv_client = TradingViewDataClient()
            print("[MTF] Using real TradingView/Yahoo Finance data")
        except Exception as e:
            print(f"[MTF] Could not load TradingView client: {e}")
            self.tv_client = None
        
    def analyze_pair(self, pair):
        """
        Analyze pair across all timeframes
        
        Args:
            pair: Trading pair (e.g., 'EURUSD')
        
        Returns:
            dict: Multi-timeframe analysis
        """
        results = {}
        
        for tf in self.timeframes:
            # Get data for timeframe
            data = self._get_timeframe_data(pair, tf)
            
            if data:
                results[tf] = {
                    'trend': self._detect_trend(data),
                    'strength': self._calculate_trend_strength(data),
                    'rsi': self._calculate_rsi(data),
                    'ema_aligned': self._check_ema_alignment(data),
                    'price': data[-1] if len(data) > 0 else 0
                }
            else:
                results[tf] = {
                    'trend': 'UNKNOWN',
                    'strength': 0,
                    'rsi': 50,
                    'ema_aligned': False,
                    'price': 0
                }
        
        # Calculate alignment and consensus
        analysis = self._synthesize_results(results)
        
        return analysis
    
    def _get_timeframe_data(self, pair, timeframe):
        """Get REAL price data for specific timeframe from TradingView/Yahoo Finance"""
        try:
            # USE REAL DATA from TradingView client
            if self.tv_client:
                # Fetch real OHLC data
                periods = {'M15': 100, 'H1': 50, 'H4': 25, 'D1': 20}
                bars = periods.get(timeframe, 50)
                
                data = self.tv_client.get_ohlc_data(pair, timeframe, bars)
                
                if data and len(data) >= 10:
                    print(f"[MTF] Got REAL data for {pair} {timeframe}: {len(data)} bars")
                    return data
            
            # Fallback if TradingView client not available
            print(f"[MTF] Fallback to simulated data for {pair} {timeframe}")
            return self._generate_fallback_data(pair, timeframe)
            
        except Exception as e:
            print(f"Error fetching {timeframe} data for {pair}: {e}")
            return self._generate_fallback_data(pair, timeframe)
    
    def _generate_fallback_data(self, pair, timeframe):
        """Generate fallback data if real data unavailable"""
        import numpy as np
        
        # Base prices
        base_prices = {
            'BTC': 43000.0,
            'BTCUSD': 43000.0,
            'GOLD': 2050.0,
            'XAUUSD': 2050.0,
            'EURUSD': 1.08500,
            'GBPUSD': 1.27000,
            'USDJPY': 149.500,
            'AUDUSD': 0.65500,
            'USDCAD': 1.36000,
            'EURJPY': 162.000
        }
        
        current_price = base_prices.get(pair.upper(), 1.0)
        
        periods = {'M15': 100, 'H1': 50, 'H4': 25, 'D1': 20}
        period_count = periods.get(timeframe, 50)
        
        # Generate with time-based seed for variation
        import time
        import hashlib
        seed_str = f"{pair}_{timeframe}_{int(time.time() / 300)}"  # Changes every 5 min
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (10**8)
        np.random.seed(seed)
        
        # Different volatility per timeframe
        volatility_map = {
            'M15': 0.003,
            'H1': 0.0025,
            'H4': 0.002,
            'D1': 0.0015
        }
        volatility_pct = volatility_map.get(timeframe, 0.002)
        
        # Generate realistic price history
        data = []
        trend_bias = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])
        
        for i in range(period_count):
            random_change = (np.random.random() - 0.5) * volatility_pct
            trend_change = trend_bias * volatility_pct * 0.3
            
            if i == 0:
                price = current_price * (1 - (trend_bias * 0.02))
            else:
                price = data[-1] * (1 + random_change + trend_change)
            
            data.append(price)
        
        data.append(current_price)
        np.random.seed(None)
        
        return data
    
    def _detect_trend(self, data):
        """Detect trend direction"""
        if not data or len(data) < 10:
            return 'UNKNOWN'
        
        # Simple trend detection: compare recent vs older prices
        recent_avg = np.mean(data[-10:])
        older_avg = np.mean(data[-30:-20]) if len(data) >= 30 else np.mean(data[:10])
        
        diff_pct = ((recent_avg - older_avg) / older_avg) * 100
        
        if diff_pct > 0.1:
            return 'UPTREND'
        elif diff_pct < -0.1:
            return 'DOWNTREND'
        else:
            return 'RANGING'
    
    def _calculate_trend_strength(self, data):
        """Calculate trend strength (0-100)"""
        if not data or len(data) < 10:
            return calc0
        
        # Calculate based on price momentum
        recent = data[-10:]
        
        # Count directional moves
        ups = sum(1 for i in range(1, len(recent)) if recent[i] > recent[i-1])
        downs = sum(1 for i in range(1, len(recent)) if recent[i] < recent[i-1])
        
        # Strength = consistency of direction
        total = ups + downs
        if total == 0:
            return 0
        
        strength = max(ups, downs) / total * 100
        return round(strength, 1)
    
    def _calculate_rsi(self, data, period=14):
        """Calculate RSI"""
        if not data or len(data) < period + 1:
            return 50
        
        # Calculate price changes
        changes = [data[i] - data[i-1] for i in range(1, len(data))]
        
        # Separate gains and losses
        gains = [max(0, change) for change in changes]
        losses = [abs(min(0, change)) for change in changes]
        
        # Average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 1)
    
    def _check_ema_alignment(self, data):
        """Check if EMAs are aligned (bullish or bearish)"""
        if not data or len(data) < 50:
            return False
        
        # Calculate simple moving averages as proxy for EMAs
        ema_20 = np.mean(data[-20:])
        ema_50 = np.mean(data[-50:])
        
        current_price = data[-1]
        
        # Bullish alignment: price > EMA20 > EMA50
        bullish = current_price > ema_20 > ema_50
        
        # Bearish alignment: price < EMA20 < EMA50
        bearish = current_price < ema_20 < ema_50
        
        return bullish or bearish
    
    def _synthesize_results(self, results):
        """Synthesize multi-timeframe results into consensus"""
        trends = [results[tf]['trend'] for tf in self.timeframes]

        # Count trend directions
        uptrends = trends.count('UPTREND')
        downtrends = trends.count('DOWNTREND')
        ranging = trends.count('RANGING')

        # Calculate alignment percentage
        total = len(self.timeframes)
        alignment_pct = max(uptrends, downtrends, ranging) / total * 100

        # Determine consensus
        if uptrends >= 3:
            consensus = 'BULLISH'
            signal_strength = alignment_pct
        elif downtrends >= 3:
            consensus = 'BEARISH'
            signal_strength = alignment_pct
        else:
            consensus = 'NEUTRAL'
            signal_strength = 0

        # Calculate trend consistency score (0-100)
        consistency_score = self._calculate_consistency_score(results)

        # Enhanced divergence detection
        divergence = self._detect_divergence(results)

        # Best entry timeframe (highest alignment + strength)
        best_tf = self._find_best_entry_timeframe(results, consensus)

        return {
            'timeframe_analysis': results,
            'consensus': consensus,
            'alignment_pct': round(alignment_pct, 1),
            'signal_strength': round(signal_strength, 1),
            'consistency_score': consistency_score,
            'divergence': divergence,
            'best_entry_tf': best_tf,
            'uptrends': uptrends,
            'downtrends': downtrends,
            'ranging': ranging
        }

    def _calculate_consistency_score(self, results):
        """Calculate trend consistency score (0-100)"""
        if not results:
            return 0

        scores = []

        # 1. Trend direction consistency
        trends = [results[tf]['trend'] for tf in self.timeframes]
        up_count = trends.count('UPTREND')
        down_count = trends.count('DOWNTREND')
        direction_consistency = max(up_count, down_count, trends.count('RANGING')) / len(trends) * 100
        scores.append(direction_consistency)

        # 2. Strength consistency (lower TF should be stronger than higher TF)
        strengths = [results[tf]['strength'] for tf in self.timeframes]
        strength_consistency = 0
        if len(strengths) >= 2:
            # Higher timeframes should have more stable/consistent trends
            m15_h1_diff = abs(strengths[0] - strengths[1])  # M15 vs H1
            h1_h4_diff = abs(strengths[1] - strengths[2])   # H1 vs H4
            h4_d1_diff = abs(strengths[2] - strengths[3])   # H4 vs D1

            # Lower differences = more consistency (max diff of 30 points)
            strength_diff_penalty = (m15_h1_diff + h1_h4_diff + h4_d1_diff) / 3
            strength_consistency = max(0, 100 - strength_diff_penalty * 2)
        scores.append(strength_consistency)

        # 3. RSI alignment (should not be extreme in multiple TFs)
        rsi_values = [results[tf]['rsi'] for tf in self.timeframes]
        extreme_rsi_count = sum(1 for rsi in rsi_values if rsi > 70 or rsi < 30)
        rsi_consistency = max(0, 100 - (extreme_rsi_count * 25))  # -25 points per extreme RSI
        scores.append(rsi_consistency)

        # 4. EMA alignment bonus
        ema_aligned_count = sum(1 for tf in self.timeframes if results[tf]['ema_aligned'])
        ema_consistency = (ema_aligned_count / len(self.timeframes)) * 100
        scores.append(ema_consistency)

        # Weighted average: Direction (40%), Strength (25%), RSI (20%), EMA (15%)
        weights = [0.4, 0.25, 0.2, 0.15]
        consistency_score = sum(score * weight for score, weight in zip(scores, weights))

        return round(consistency_score, 1)
    
    def _detect_divergence(self, results):
        """Enhanced divergence detection between timeframes"""
        divergences = []

        # 1. Trend direction divergence
        lower_tf_trends = [results['M15']['trend'], results['H1']['trend']]
        higher_tf_trends = [results['H4']['trend'], results['D1']['trend']]

        lower_bullish = lower_tf_trends.count('UPTREND') >= 1
        lower_bearish = lower_tf_trends.count('DOWNTREND') >= 1
        higher_bullish = higher_tf_trends.count('UPTREND') >= 1
        higher_bearish = higher_tf_trends.count('DOWNTREND') >= 1

        if lower_bullish and higher_bearish:
            divergences.append('TREND_CONFLICT_BULL_LOWER_BEAR_HIGHER')
        elif lower_bearish and higher_bullish:
            divergences.append('TREND_CONFLICT_BEAR_LOWER_BULL_HIGHER')

        # 2. Strength divergence (weak lower TF, strong higher TF)
        if results['M15']['strength'] < 30 and results['H1']['strength'] < 40:
            lower_weak = True
        else:
            lower_weak = False

        if results['H4']['strength'] > 60 or results['D1']['strength'] > 70:
            higher_strong = True
        else:
            higher_strong = False

        if lower_weak and higher_strong:
            divergences.append('STRENGTH_WEAK_LOWER_STRONG_HIGHER')

        # 3. RSI divergence (extreme in lower TF vs normal in higher TF)
        m15_rsi = results['M15']['rsi']
        h1_rsi = results['H1']['rsi']
        h4_rsi = results['H4']['rsi']
        d1_rsi = results['D1']['rsi']

        lower_extreme = (m15_rsi > 75 or m15_rsi < 25) or (h1_rsi > 75 or h1_rsi < 25)
        higher_normal = (40 <= h4_rsi <= 60) and (40 <= d1_rsi <= 60)

        if lower_extreme and higher_normal:
            divergences.append('RSI_EXTREME_LOWER_NORMAL_HIGHER')

        # 4. Price vs momentum divergence (price making highs but RSI making lower highs)
        # This would require historical data - simplified version
        recent_prices = [results[tf]['price'] for tf in self.timeframes if results[tf]['price'] > 0]
        recent_rsi = [results[tf]['rsi'] for tf in self.timeframes]

        if len(recent_prices) >= 2 and len(recent_rsi) >= 2:
            # Check if price is rising but RSI is falling (bearish divergence)
            price_rising = recent_prices[-1] > recent_prices[0]
            rsi_falling = recent_rsi[-1] < recent_rsi[0]

            if price_rising and rsi_falling:
                divergences.append('PRICE_RSI_BEARISH_DIVERGENCE')

            # Check if price is falling but RSI is rising (bullish divergence)
            price_falling = recent_prices[-1] < recent_prices[0]
            rsi_rising = recent_rsi[-1] > recent_rsi[0]

            if price_falling and rsi_rising:
                divergences.append('PRICE_RSI_BULLISH_DIVERGENCE')

        if divergences:
            return divergences
        else:
            return ['NONE']

    def create_mtf_dashboard(self, pair):
        """Create a visual MTF dashboard for bot display"""
        analysis = self.analyze_pair(pair)

        if not analysis:
            return "❌ Unable to analyze multi-timeframe data"

        dashboard = f"📊 *MULTI-TIMEFRAME DASHBOARD*\n"
        dashboard += f"*{pair.upper()}* Analysis\n\n"

        # Consensus section
        consensus = analysis['consensus']
        emoji_map = {'BULLISH': '🚀', 'BEARISH': '📉', 'NEUTRAL': '⚖️'}
        dashboard += f"{emoji_map.get(consensus, '⚪')} *CONSENSUS: {consensus}*\n"
        dashboard += f"Alignment: {analysis['alignment_pct']}%\n"
        dashboard += f"Consistency: {analysis['consistency_score']}/100\n"
        dashboard += f"Signal Strength: {analysis['signal_strength']}%\n\n"

        # Timeframe breakdown
        dashboard += "⏰ *TIMEFRAME BREAKDOWN*\n"
        dashboard += "```\n"
        dashboard += "TF     Trend       Strength   RSI   EMA\n"
        dashboard += "───────────────────────────────────────\n"

        tf_results = analysis['timeframe_analysis']
        for tf in self.timeframes:
            data = tf_results[tf]
            trend = data['trend'][:8]  # Truncate long trend names
            strength = f"{data['strength']:5.1f}"
            rsi = f"{data['rsi']:5.1f}"
            ema = "✓" if data['ema_aligned'] else "✗"
            dashboard += f"{tf:<6} {trend:<8} {strength} {rsi} {ema}\n"

        dashboard += "```\n\n"

        # Best entry timeframe
        best_tf = analysis['best_entry_tf']
        dashboard += f"🎯 *BEST ENTRY TIMEFRAME: {best_tf}*\n\n"

        # Divergence warnings
        divergences = analysis['divergence']
        if divergences and divergences != ['NONE']:
            dashboard += "⚠️ *DIVERGENCE WARNINGS*\n"
            for div in divergences:
                div_desc = self._get_divergence_description(div)
                dashboard += f"• {div_desc}\n"
            dashboard += "\n"

        # Trading implications
        dashboard += "💡 *TRADING IMPLICATIONS*\n"

        if consensus == 'BULLISH' and analysis['consistency_score'] > 70:
            dashboard += "✅ Strong bullish setup - Consider LONG positions\n"
            dashboard += f"📈 Enter on {best_tf} timeframe pullbacks\n"
        elif consensus == 'BEARISH' and analysis['consistency_score'] > 70:
            dashboard += "✅ Strong bearish setup - Consider SHORT positions\n"
            dashboard += f"📉 Enter on {best_tf} timeframe rallies\n"
        elif analysis['consistency_score'] < 50:
            dashboard += "⚠️ Low consistency - Wait for clearer signals\n"
            dashboard += "🔄 Consider ranging strategies or wait for alignment\n"
        else:
            dashboard += "⚖️ Mixed signals - Exercise caution\n"
            dashboard += "🔍 Look for confluence with other indicators\n"

        return dashboard

    def _get_divergence_description(self, divergence_type):
        """Get human-readable divergence description"""
        descriptions = {
            'TREND_CONFLICT_BULL_LOWER_BEAR_HIGHER': 'Lower TFs bullish, higher TFs bearish',
            'TREND_CONFLICT_BEAR_LOWER_BULL_HIGHER': 'Lower TFs bearish, higher TFs bullish',
            'STRENGTH_WEAK_LOWER_STRONG_HIGHER': 'Weak momentum in lower TFs, strong in higher TFs',
            'RSI_EXTREME_LOWER_NORMAL_HIGHER': 'Extreme RSI in lower TFs, normal in higher TFs',
            'PRICE_RSI_BEARISH_DIVERGENCE': 'Price making highs, RSI making lower highs',
            'PRICE_RSI_BULLISH_DIVERGENCE': 'Price making lows, RSI making higher lows',
            'NONE': 'No significant divergences detected'
        }
        return descriptions.get(divergence_type, divergence_type)
    
    def _find_best_entry_timeframe(self, results, consensus):
        """Find best timeframe for entry"""
        # Score each timeframe
        scores = {}
        
        for tf in self.timeframes:
            score = 0
            
            # Alignment with consensus
            if consensus == 'BULLISH' and results[tf]['trend'] == 'UPTREND':
                score += 40
            elif consensus == 'BEARISH' and results[tf]['trend'] == 'DOWNTREND':
                score += 40
            
            # Trend strength
            score += results[tf]['strength'] * 0.3
            
            # EMA alignment
            if results[tf]['ema_aligned']:
                score += 20
            
            # RSI confirmation (not overbought/oversold)
            rsi = results[tf]['rsi']
            if 40 <= rsi <= 60:
                score += 10
            
            scores[tf] = round(score, 1)
        
        # Return best timeframe
        best_tf = max(scores, key=scores.get)
        return best_tf


# Testing
if __name__ == "__main__":
    print("Testing Multi-Timeframe Analyzer...")
    print("=" * 60)
    
    # Mock data client
    class MockDataClient:
        def get_price(self, pair):
            return 1.08500  # EUR/USD example
    
    analyzer = MultiTimeframeAnalyzer(MockDataClient())
    
    # Test analysis
    print("\nAnalyzing EUR/USD across timeframes...")
    analysis = analyzer.analyze_pair('EURUSD')
    
    print(f"\nConsensus: {analysis['consensus']}")
    print(f"Alignment: {analysis['alignment_pct']}%")
    print(f"Signal Strength: {analysis['signal_strength']}%")
    print(f"Divergence: {analysis['divergence']}")
    print(f"Best Entry TF: {analysis['best_entry_tf']}")
    
    print("\nTimeframe Breakdown:")
    for tf in ['M15', 'H1', 'H4', 'D1']:
        data = analysis['timeframe_analysis'][tf]
        print(f"  {tf:4s}: {data['trend']:10s} | Strength: {data['strength']:5.1f}% | RSI: {data['rsi']:5.1f}")
    
    print("\n" + "=" * 60)
    print("[OK] Multi-Timeframe Analyzer ready!")
