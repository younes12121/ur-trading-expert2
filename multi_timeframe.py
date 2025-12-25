"""
Multi-Timeframe Analyzer
Analyze multiple timeframes for signal confirmation
"""

import pandas as pd
from typing import Dict, List
from data_fetcher import BinanceDataFetcher

class MultiTimeframeAnalyzer:
    """Analyze multiple timeframes for better signals"""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.data_fetcher = BinanceDataFetcher(symbol=symbol)
        self.timeframes = ['5m', '15m', '1h', '4h']
    
    def get_multi_timeframe_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple timeframes"""
        data = {}
        
        for tf in self.timeframes:
            print(f"Fetching {tf} data...")
            df = self.data_fetcher.get_klines(interval=tf, limit=100)
            
            if df is not None:
                data[tf] = df
        
        return data
    
    def analyze_trend_alignment(self, mtf_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Check if trends align across timeframes
        
        Returns:
            Dictionary with trend analysis
        """
        trends = {}
        
        for tf, df in mtf_data.items():
            if len(df) < 20:
                continue
            
            # Calculate trend using moving averages
            sma_short = df['close'].iloc[-10:].mean()
            sma_long = df['close'].iloc[-20:].mean()
            current_price = df['close'].iloc[-1]
            
            if sma_short > sma_long and current_price > sma_short:
                trends[tf] = 'BULLISH'
            elif sma_short < sma_long and current_price < sma_short:
                trends[tf] = 'BEARISH'
            else:
                trends[tf] = 'NEUTRAL'
        
        # Check alignment
        bullish_count = sum(1 for t in trends.values() if t == 'BULLISH')
        bearish_count = sum(1 for t in trends.values() if t == 'BEARISH')
        
        if bullish_count >= 3:
            overall_trend = 'BULLISH'
            alignment_score = (bullish_count / len(trends)) * 100
        elif bearish_count >= 3:
            overall_trend = 'BEARISH'
            alignment_score = (bearish_count / len(trends)) * 100
        else:
            overall_trend = 'MIXED'
            alignment_score = 50
        
        return {
            'trends': trends,
            'overall_trend': overall_trend,
            'alignment_score': alignment_score,
            'bullish_timeframes': bullish_count,
            'bearish_timeframes': bearish_count
        }
    
    def get_higher_timeframe_confirmation(self, signal_direction: str) -> bool:
        """
        Check if higher timeframes confirm the signal
        
        Args:
            signal_direction: 'BUY' or 'SELL'
        
        Returns:
            True if confirmed, False otherwise
        """
        mtf_data = self.get_multi_timeframe_data()
        trend_analysis = self.analyze_trend_alignment(mtf_data)
        
        if signal_direction == 'BUY':
            # Need bullish trend on higher timeframes
            return trend_analysis['overall_trend'] == 'BULLISH'
        elif signal_direction == 'SELL':
            # Need bearish trend on higher timeframes
            return trend_analysis['overall_trend'] == 'BEARISH'
        else:
            return False
    
    def calculate_mtf_score(self) -> float:
        """
        Calculate multi-timeframe alignment score (0-100)
        
        Returns:
            Score indicating how well timeframes align
        """
        mtf_data = self.get_multi_timeframe_data()
        trend_analysis = self.analyze_trend_alignment(mtf_data)
        
        return trend_analysis['alignment_score']
    
    def print_mtf_analysis(self):
        """Print multi-timeframe analysis"""
        mtf_data = self.get_multi_timeframe_data()
        trend_analysis = self.analyze_trend_alignment(mtf_data)
        
        print("=" * 70)
        print("📊 MULTI-TIMEFRAME ANALYSIS")
        print("=" * 70)
        
        for tf, trend in trend_analysis['trends'].items():
            emoji = "📈" if trend == "BULLISH" else "📉" if trend == "BEARISH" else "➡️"
            print(f"{tf:6s} {emoji} {trend}")
        
        print()
        print(f"Overall Trend:     {trend_analysis['overall_trend']}")
        print(f"Alignment Score:   {trend_analysis['alignment_score']:.1f}%")
        print(f"Bullish TFs:       {trend_analysis['bullish_timeframes']}/{len(trend_analysis['trends'])}")
        print(f"Bearish TFs:       {trend_analysis['bearish_timeframes']}/{len(trend_analysis['trends'])}")
        print("=" * 70)


class AdaptiveParameterManager:
    """Adjust strategy parameters based on market regime"""
    
    def __init__(self):
        self.current_regime = 'NORMAL'
        self.regime_params = {
            'TRENDING': {
                'risk_per_trade': 0.015,  # Increase risk in trends
                'tp_multiplier': 3.0,      # Larger targets
                'confidence_threshold': 60
            },
            'RANGING': {
                'risk_per_trade': 0.008,  # Reduce risk in ranges
                'tp_multiplier': 1.5,      # Smaller targets
                'confidence_threshold': 70  # Higher confidence needed
            },
            'VOLATILE': {
                'risk_per_trade': 0.005,  # Very low risk
                'tp_multiplier': 2.0,
                'confidence_threshold': 75
            },
            'NORMAL': {
                'risk_per_trade': 0.01,
                'tp_multiplier': 2.5,
                'confidence_threshold': 65
            }
        }
    
    def detect_market_regime(self, market_data: Dict) -> str:
        """
        Detect current market regime
        
        Returns:
            'TRENDING', 'RANGING', 'VOLATILE', or 'NORMAL'
        """
        volatility = market_data.get('btc_volatility', 0.03)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        # High volatility regime
        if volatility > 0.06:
            return 'VOLATILE'
        
        # Trending regime (high volume, moderate volatility)
        if volume_ratio > 1.5 and 0.03 <= volatility <= 0.05:
            return 'TRENDING'
        
        # Ranging regime (low volatility, normal volume)
        if volatility < 0.025:
            return 'RANGING'
        
        return 'NORMAL'
    
    def get_adaptive_parameters(self, market_data: Dict) -> Dict:
        """Get parameters adapted to current market regime"""
        regime = self.detect_market_regime(market_data)
        self.current_regime = regime
        
        params = self.regime_params[regime].copy()
        params['regime'] = regime
        
        return params
    
    def should_trade_in_regime(self, regime: str = None) -> bool:
        """Check if we should trade in current regime"""
        if regime is None:
            regime = self.current_regime
        
        # Don't trade in extremely volatile markets
        if regime == 'VOLATILE':
            return False
        
        return True


# Test
if __name__ == "__main__":
    print("Multi-Timeframe Analyzer ready!")
    print("\nExample usage:")
    print("  mtf = MultiTimeframeAnalyzer()")
    print("  mtf.print_mtf_analysis()")
    print("\n  adaptive = AdaptiveParameterManager()")
    print("  params = adaptive.get_adaptive_parameters(market_data)")
