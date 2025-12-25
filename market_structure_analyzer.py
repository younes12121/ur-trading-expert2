"""
Advanced Market Structure Analyzer
Identifies key levels, market phases, and structural patterns for enhanced trading decisions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import requests


class MarketStructureAnalyzer:
    """Advanced market structure analysis with support/resistance and trend identification"""
    
    def __init__(self):
        self.support_levels = {}
        self.resistance_levels = {}
        self.market_phases = {}
        self.session_data = {}
        
        # Market sessions (UTC times)
        self.sessions = {
            'sydney': {'start': '21:00', 'end': '06:00', 'active_pairs': ['AUDUSD', 'NZDUSD', 'AUDJPY']},
            'tokyo': {'start': '00:00', 'end': '09:00', 'active_pairs': ['USDJPY', 'EURJPY', 'GBPJPY', 'AUDJPY']},
            'london': {'start': '08:00', 'end': '17:00', 'active_pairs': ['EURUSD', 'GBPUSD', 'EURGBP', 'EURJPY']},
            'new_york': {'start': '13:00', 'end': '22:00', 'active_pairs': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD']}
        }
    
    def get_current_market_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Fetch current market data for analysis
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT', 'EURUSD')
            timeframe: Timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            # For demonstration, we'll use Binance API for crypto symbols
            # In practice, you'd integrate with your data provider
            if 'BTC' in symbol or 'ETH' in symbol or symbol.endswith('USDT'):
                url = "https://api.binance.com/api/v3/klines"
                params = {
                    'symbol': symbol,
                    'interval': timeframe,
                    'limit': limit
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                    ])
                    
                    # Convert to proper types
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col])
                    
                    df.set_index('timestamp', inplace=True)
                    return df[['open', 'high', 'low', 'close', 'volume']]
            
            else:
                # For Forex pairs, generate mock data for demonstration
                # In practice, integrate with forex data provider
                dates = pd.date_range(end=datetime.now(), periods=limit, freq='h')
                
                # Generate realistic price movements
                np.random.seed(42)  # For reproducible results
                base_price = 1.1000 if 'EUR' in symbol else 1.2500 if 'GBP' in symbol else 110.0 if 'JPY' in symbol else 0.7500
                
                price_changes = np.random.normal(0, 0.001, limit)  # Small random changes
                prices = base_price + np.cumsum(price_changes)
                
                # Create OHLCV data
                data = []
                for i, price in enumerate(prices):
                    high = price + abs(np.random.normal(0, 0.0005))
                    low = price - abs(np.random.normal(0, 0.0005))
                    open_price = prices[i-1] if i > 0 else price
                    volume = np.random.uniform(1000, 5000)
                    
                    data.append({
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'close': price,
                        'volume': volume
                    })
                
                df = pd.DataFrame(data, index=dates)
                return df
                
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def identify_support_resistance_levels(self, data: pd.DataFrame, 
                                         lookback: int = 20, 
                                         min_touches: int = 2) -> Dict:
        """
        Identify key support and resistance levels using pivot points and volume
        
        Args:
            data: OHLCV DataFrame
            lookback: Periods to look back for pivot identification
            min_touches: Minimum number of touches to confirm level
            
        Returns:
            Dictionary with support and resistance levels
        """
        if len(data) < lookback * 2:
            return {'support': [], 'resistance': [], 'pivot_points': []}
        
        highs = data['high'].values
        lows = data['low'].values
        volumes = data['volume'].values if 'volume' in data.columns else np.ones(len(data))
        
        # Find pivot highs and lows
        pivot_highs = []
        pivot_lows = []
        
        for i in range(lookback, len(data) - lookback):
            # Check if current point is a pivot high
            is_pivot_high = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and highs[j] >= highs[i]:
                    is_pivot_high = False
                    break
            
            if is_pivot_high:
                pivot_highs.append({
                    'index': i,
                    'price': highs[i],
                    'timestamp': data.index[i],
                    'volume': volumes[i]
                })
            
            # Check if current point is a pivot low
            is_pivot_low = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and lows[j] <= lows[i]:
                    is_pivot_low = False
                    break
            
            if is_pivot_low:
                pivot_lows.append({
                    'index': i,
                    'price': lows[i],
                    'timestamp': data.index[i],
                    'volume': volumes[i]
                })
        
        # Group similar levels and count touches
        def group_levels(pivots, tolerance=0.001):
            if not pivots:
                return []
            
            levels = []
            for pivot in pivots:
                price = pivot['price']
                
                # Find existing level within tolerance
                found_level = None
                for level in levels:
                    if abs(level['price'] - price) / price <= tolerance:
                        found_level = level
                        break
                
                if found_level:
                    found_level['touches'] += 1
                    found_level['volume'] += pivot['volume']
                    found_level['last_touch'] = pivot['timestamp']
                else:
                    levels.append({
                        'price': price,
                        'touches': 1,
                        'volume': pivot['volume'],
                        'first_touch': pivot['timestamp'],
                        'last_touch': pivot['timestamp'],
                        'strength': 0  # Will calculate later
                    })
            
            # Calculate strength based on touches and volume
            for level in levels:
                level['strength'] = level['touches'] * np.log(level['volume'] + 1)
            
            # Filter by minimum touches and sort by strength
            filtered_levels = [l for l in levels if l['touches'] >= min_touches]
            return sorted(filtered_levels, key=lambda x: x['strength'], reverse=True)
        
        resistance_levels = group_levels(pivot_highs)
        support_levels = group_levels(pivot_lows)
        
        return {
            'support': support_levels[:10],  # Top 10 support levels
            'resistance': resistance_levels[:10],  # Top 10 resistance levels
            'pivot_points': {
                'pivot_highs': len(pivot_highs),
                'pivot_lows': len(pivot_lows),
                'total_pivots': len(pivot_highs) + len(pivot_lows)
            }
        }
    
    def analyze_market_phase(self, data: pd.DataFrame) -> Dict:
        """
        Determine current market phase (trending, ranging, breakout)
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dictionary with market phase analysis
        """
        if len(data) < 20:
            return {'phase': 'insufficient_data', 'confidence': 0}
        
        # Calculate various indicators
        closes = data['close'].values
        highs = data['high'].values
        lows = data['low'].values
        
        # Simple moving averages
        ma_short = pd.Series(closes).rolling(window=10).mean().values
        ma_long = pd.Series(closes).rolling(window=20).mean().values
        
        # Average True Range (volatility measure)
        atr = self._calculate_atr(data)
        current_atr = atr[-1] if len(atr) > 0 else 0
        avg_atr = np.mean(atr) if len(atr) > 0 else 0
        
        # Recent price range
        recent_high = np.max(highs[-20:])
        recent_low = np.min(lows[-20:])
        price_range = recent_high - recent_low
        current_price = closes[-1]
        
        # Trend analysis
        trend_strength = 0
        if len(ma_short) > 5 and len(ma_long) > 5:
            # Check if moving averages are aligned
            ma_diff = ma_short[-1] - ma_long[-1]
            trend_strength = abs(ma_diff) / current_price
            trend_direction = 'bullish' if ma_diff > 0 else 'bearish'
        else:
            trend_direction = 'neutral'
        
        # Range analysis
        range_strength = price_range / current_price
        
        # Phase determination logic
        phase_scores = {
            'trending': 0,
            'ranging': 0,
            'breakout': 0
        }
        
        # Trending phase indicators
        if trend_strength > 0.01:  # Strong MA separation
            phase_scores['trending'] += 3
        elif trend_strength > 0.005:  # Moderate MA separation
            phase_scores['trending'] += 1
        
        # Ranging phase indicators
        if current_atr < avg_atr * 0.8:  # Low volatility
            phase_scores['ranging'] += 2
        
        if range_strength < 0.02:  # Tight range
            phase_scores['ranging'] += 2
        
        # Breakout phase indicators
        if current_atr > avg_atr * 1.5:  # High volatility
            phase_scores['breakout'] += 3
        
        # Check if price is near range boundaries
        if current_price > recent_high * 0.98 or current_price < recent_low * 1.02:
            phase_scores['breakout'] += 2
        
        # Determine phase
        max_score = max(phase_scores.values())
        if max_score == 0:
            phase = 'uncertain'
            confidence = 0
        else:
            phase = max(phase_scores.items(), key=lambda x: x[1])[0]
            confidence = min(max_score * 10, 100)  # Convert to percentage
        
        return {
            'phase': phase,
            'confidence': confidence,
            'trend_direction': trend_direction,
            'trend_strength': round(trend_strength * 100, 2),  # As percentage
            'volatility_ratio': round(current_atr / avg_atr if avg_atr > 0 else 1, 2),
            'price_position': {
                'in_range': recent_low < current_price < recent_high,
                'near_high': current_price > recent_high * 0.95,
                'near_low': current_price < recent_low * 1.05,
                'range_size': round(range_strength * 100, 2)
            }
        }
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Average True Range"""
        if len(data) < period:
            return np.array([])
        
        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values
        
        # Calculate True Range
        tr = np.zeros(len(data))
        for i in range(1, len(data)):
            tr[i] = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
        
        # Calculate ATR
        atr = np.zeros(len(data))
        atr[period-1] = np.mean(tr[1:period])
        
        for i in range(period, len(data)):
            atr[i] = (atr[i-1] * (period-1) + tr[i]) / period
        
        return atr[period-1:]
    
    def get_active_session(self, current_time: datetime = None) -> Dict:
        """
        Determine currently active trading session
        
        Args:
            current_time: Current UTC time (defaults to now)
            
        Returns:
            Dictionary with active session information
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        current_hour = current_time.strftime('%H:%M')
        
        active_sessions = []
        for session_name, session_info in self.sessions.items():
            start = session_info['start']
            end = session_info['end']
            
            # Handle sessions that cross midnight
            if start > end:  # e.g., Sydney: 21:00 to 06:00
                if current_hour >= start or current_hour <= end:
                    active_sessions.append(session_name)
            else:  # Normal sessions
                if start <= current_hour <= end:
                    active_sessions.append(session_name)
        
        # Determine volatility expectation based on session overlaps
        volatility_level = 'low'
        if len(active_sessions) >= 2:
            volatility_level = 'high'
        elif len(active_sessions) == 1:
            volatility_level = 'medium'
        
        return {
            'active_sessions': active_sessions,
            'volatility_expectation': volatility_level,
            'recommended_pairs': list(set(
                pair for session in active_sessions
                for pair in self.sessions[session]['active_pairs']
            )),
            'session_overlaps': len(active_sessions) > 1
        }
    
    def analyze_economic_impact(self, events: List[Dict]) -> Dict:
        """
        Analyze potential impact of economic events on market structure
        
        Args:
            events: List of economic events with impact ratings
            
        Returns:
            Dictionary with impact analysis
        """
        if not events:
            return {
                'risk_level': 'low',
                'affected_pairs': [],
                'recommendations': ['Normal trading conditions']
            }
        
        impact_scores = {'low': 1, 'medium': 3, 'high': 5}
        total_impact = sum(impact_scores.get(event.get('impact', 'low'), 1) for event in events)
        
        # Categorize overall risk
        if total_impact >= 15:
            risk_level = 'very_high'
            recommendations = [
                'Consider reducing position sizes',
                'Widen stop losses',
                'Avoid trading 30 minutes before/after major events'
            ]
        elif total_impact >= 10:
            risk_level = 'high'
            recommendations = [
                'Reduce position sizes by 50%',
                'Monitor news feeds closely',
                'Be prepared for increased volatility'
            ]
        elif total_impact >= 5:
            risk_level = 'medium'
            recommendations = [
                'Standard risk management applies',
                'Monitor key economic releases',
                'Adjust stop losses if needed'
            ]
        else:
            risk_level = 'low'
            recommendations = ['Normal trading conditions']
        
        # Identify affected currency pairs
        affected_currencies = set()
        for event in events:
            currency = event.get('currency', '')
            if currency:
                affected_currencies.add(currency)
        
        # Map to trading pairs
        affected_pairs = []
        for currency in affected_currencies:
            for pair in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']:
                if currency in pair:
                    affected_pairs.append(pair)
        
        return {
            'risk_level': risk_level,
            'total_impact_score': total_impact,
            'affected_pairs': list(set(affected_pairs)),
            'high_impact_events': [e for e in events if e.get('impact') == 'high'],
            'recommendations': recommendations
        }
    
    def generate_structure_report(self, symbol: str, timeframe: str = '1h') -> Dict:
        """
        Generate comprehensive market structure report for a symbol
        
        Args:
            symbol: Trading symbol to analyze
            timeframe: Analysis timeframe
            
        Returns:
            Comprehensive market structure report
        """
        # Fetch market data
        data = self.get_current_market_data(symbol, timeframe)
        if data is None:
            return {'error': 'Failed to fetch market data'}
        
        # Perform all analyses
        levels = self.identify_support_resistance_levels(data)
        phase = self.analyze_market_phase(data)
        session = self.get_active_session()
        
        # Calculate additional metrics
        current_price = data['close'].iloc[-1]
        price_change = ((current_price - data['close'].iloc[-2]) / data['close'].iloc[-2]) * 100
        
        # Find nearest support/resistance
        nearest_resistance = None
        nearest_support = None
        
        for level in levels['resistance']:
            if level['price'] > current_price:
                if nearest_resistance is None or level['price'] < nearest_resistance['price']:
                    nearest_resistance = level
        
        for level in levels['support']:
            if level['price'] < current_price:
                if nearest_support is None or level['price'] > nearest_support['price']:
                    nearest_support = level
        
        # Generate trading recommendations
        recommendations = []
        
        if phase['phase'] == 'trending':
            if phase['trend_direction'] == 'bullish':
                recommendations.append("Consider long positions on pullbacks to support")
            else:
                recommendations.append("Consider short positions on rallies to resistance")
        
        elif phase['phase'] == 'ranging':
            recommendations.append("Trade between support and resistance levels")
            recommendations.append("Wait for breakout confirmation before trend trading")
        
        elif phase['phase'] == 'breakout':
            recommendations.append("High volatility - use tighter stops")
            recommendations.append("Wait for breakout confirmation and retest")
        
        if session['volatility_expectation'] == 'high':
            recommendations.append("Session overlap detected - expect higher volatility")
        
        # Compile report
        report = {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'current_price': round(current_price, 5),
            'price_change_pct': round(price_change, 2),
            'market_structure': {
                'support_levels': levels['support'][:5],  # Top 5
                'resistance_levels': levels['resistance'][:5],  # Top 5
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance
            },
            'market_phase': phase,
            'session_info': session,
            'key_levels_summary': {
                'total_support_levels': len(levels['support']),
                'total_resistance_levels': len(levels['resistance']),
                'strong_levels': len([l for l in levels['support'] + levels['resistance'] if l.get('touches', 0) >= 3])
            },
            'recommendations': recommendations,
            'analysis_quality': {
                'data_points': len(data),
                'pivot_points_found': levels['pivot_points']['total_pivots'],
                'phase_confidence': phase['confidence']
            }
        }
        
        return report
    
    def export_structure_analysis(self, symbols: List[str], filename: str = None) -> str:
        """
        Export market structure analysis for multiple symbols
        
        Args:
            symbols: List of symbols to analyze
            filename: Optional filename for the export
            
        Returns:
            Filename of the exported analysis
        """
        if filename is None:
            filename = f"market_structure_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        analysis_results = {}
        
        for symbol in symbols:
            try:
                report = self.generate_structure_report(symbol)
                analysis_results[symbol] = report
            except Exception as e:
                analysis_results[symbol] = {'error': str(e)}
        
        # Add summary statistics
        successful_analyses = [r for r in analysis_results.values() if 'error' not in r]
        
        summary = {
            'total_symbols': len(symbols),
            'successful_analyses': len(successful_analyses),
            'failed_analyses': len(symbols) - len(successful_analyses),
            'trending_markets': len([r for r in successful_analyses if r.get('market_phase', {}).get('phase') == 'trending']),
            'ranging_markets': len([r for r in successful_analyses if r.get('market_phase', {}).get('phase') == 'ranging']),
            'breakout_markets': len([r for r in successful_analyses if r.get('market_phase', {}).get('phase') == 'breakout'])
        }
        
        export_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'timeframe': '1h',
                'analysis_type': 'market_structure'
            },
            'summary': summary,
            'symbol_analyses': analysis_results
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filename


# Example usage and testing
if __name__ == "__main__":
    # Initialize market structure analyzer
    analyzer = MarketStructureAnalyzer()
    
    print("=" * 70)
    print("📊 MARKET STRUCTURE ANALYZER DEMONSTRATION")
    print("=" * 70)
    
    # Test symbols
    test_symbols = ['BTCUSDT', 'EURUSD', 'GBPUSD']
    
    for symbol in test_symbols:
        print(f"\n🔍 ANALYZING {symbol}")
        print("-" * 50)
        
        # Generate structure report
        report = analyzer.generate_structure_report(symbol)
        
        if 'error' in report:
            print(f"❌ Analysis failed: {report['error']}")
            continue
        
        # Display key information
        print(f"Current Price: {report['current_price']}")
        print(f"Price Change: {report['price_change_pct']:+.2f}%")
        print(f"Market Phase: {report['market_phase']['phase']} ({report['market_phase']['confidence']}% confidence)")
        
        if report['market_phase']['trend_direction'] != 'neutral':
            print(f"Trend: {report['market_phase']['trend_direction']}")
        
        # Support/Resistance levels
        structure = report['market_structure']
        if structure['nearest_support']:
            support_price = structure['nearest_support']['price']
            support_distance = ((report['current_price'] - support_price) / report['current_price']) * 100
            print(f"Nearest Support: {support_price:.5f} ({support_distance:.2f}% below)")
        
        if structure['nearest_resistance']:
            resistance_price = structure['nearest_resistance']['price']
            resistance_distance = ((resistance_price - report['current_price']) / report['current_price']) * 100
            print(f"Nearest Resistance: {resistance_price:.5f} ({resistance_distance:.2f}% above)")
        
        # Session info
        session_info = report['session_info']
        if session_info['active_sessions']:
            print(f"Active Sessions: {', '.join(session_info['active_sessions'])}")
            print(f"Volatility Expectation: {session_info['volatility_expectation']}")
        
        # Recommendations
        if report['recommendations']:
            print("Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
    
    # Export comprehensive analysis
    print(f"\n📁 EXPORTING COMPREHENSIVE ANALYSIS")
    print("-" * 50)
    
    filename = analyzer.export_structure_analysis(test_symbols)
    print(f"📊 Analysis exported to: {filename}")
    
    print("\n✅ Market structure analyzer demonstration complete!")
