"""
International Market Analytics
Provides correlation analysis, cross-market signals, and global market insights
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from functools import lru_cache
import json

class InternationalAnalytics:
    """Advanced analytics for international markets"""

    def __init__(self, data_fetcher=None, cache_manager=None):
        self.data_fetcher = data_fetcher
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)

        # Market groupings for analysis
        self.market_groups = {
            'asian_currencies': ['CNY', 'JPY'],
            'european_currencies': ['EUR', 'GBP'],
            'pacific_currencies': ['AUD'],
            'emerging_markets': ['BRL'],
            'crypto_futures': ['ETH'],
            'commodity_currencies': ['AUD'],  # AUD is heavily influenced by commodities
            'safe_haven': ['JPY', 'CHF'] if 'CHF' in ['JPY', 'EUR', 'GBP', 'AUD'] else ['JPY']
        }

        # Market sessions and their active hours (UTC)
        self.market_sessions = {
            'asian': {'start': 23, 'end': 8, 'name': 'Asian Session'},
            'european': {'start': 7, 'end': 15, 'name': 'European Session'},
            'american': {'start': 13, 'end': 21, 'name': 'American Session'},
            'pacific': {'start': 0, 'end': 8, 'name': 'Pacific Session'}
        }

    def get_market_correlations(self, symbols: List[str] = None, period_days: int = 30) -> Dict:
        """Calculate correlation matrix for international markets"""
        try:
            if symbols is None:
                symbols = ['CNY', 'JPY', 'EUR', 'GBP', 'AUD', 'BRL', 'ETH']

            # Fetch price data for all symbols
            price_data = {}
            for symbol in symbols:
                try:
                    data = self._get_price_data(symbol, period_days)
                    if data is not None and len(data) > 0:
                        price_data[symbol] = data
                except Exception as e:
                    self.logger.warning(f"Failed to fetch data for {symbol}: {e}")

            if len(price_data) < 2:
                return self._error_result("Insufficient data for correlation analysis")

            # Calculate correlation matrix
            correlation_matrix = self._calculate_correlation_matrix(price_data)

            # Generate insights
            insights = self._generate_correlation_insights(correlation_matrix)

            return {
                'correlation_matrix': correlation_matrix,
                'insights': insights,
                'symbols_analyzed': list(price_data.keys()),
                'period_days': period_days,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error calculating market correlations: {e}")
            return self._error_result(str(e))

    def get_cross_market_signals(self, base_symbol: str = 'EUR') -> Dict:
        """Generate cross-market signals based on inter-market relationships"""
        try:
            # Get signals for all international markets
            from international_signal_api import get_international_signal, get_international_symbols

            symbols = get_international_symbols()
            market_signals = {}

            for symbol in symbols:
                try:
                    signal = get_international_signal(symbol)
                    if signal and signal.get('direction') != 'ERROR':
                        market_signals[symbol] = signal
                except Exception as e:
                    self.logger.warning(f"Failed to get signal for {symbol}: {e}")

            if not market_signals:
                return self._error_result("No market signals available")

            # Analyze cross-market relationships
            cross_signals = self._analyze_cross_market_relationships(market_signals, base_symbol)

            # Generate combined signal
            combined_signal = self._generate_combined_signal(market_signals, cross_signals)

            return {
                'base_symbol': base_symbol,
                'market_signals': market_signals,
                'cross_market_signals': cross_signals,
                'combined_signal': combined_signal,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error generating cross-market signals: {e}")
            return self._error_result(str(e))

    def get_market_session_analysis(self) -> Dict:
        """Analyze current market session activity"""
        try:
            current_hour = datetime.now().hour

            # Determine active sessions
            active_sessions = []
            for session_name, session_info in self.market_sessions.items():
                if self._is_session_active(current_hour, session_info):
                    active_sessions.append({
                        'name': session_info['name'],
                        'start_hour': session_info['start'],
                        'end_hour': session_info['end'],
                        'markets': self._get_session_markets(session_name)
                    })

            # Get session-specific insights
            session_insights = self._generate_session_insights(active_sessions)

            return {
                'current_hour_utc': current_hour,
                'active_sessions': active_sessions,
                'session_insights': session_insights,
                'next_session': self._get_next_session(current_hour),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error analyzing market sessions: {e}")
            return self._error_result(str(e))

    def get_currency_strength_analysis(self) -> Dict:
        """Analyze currency strength across international markets"""
        try:
            # Get signals for currency pairs
            currency_symbols = ['EUR', 'GBP', 'AUD', 'JPY']
            strength_data = {}

            from international_signal_api import get_international_signal

            for symbol in currency_symbols:
                try:
                    signal = get_international_signal(symbol)
                    if signal and signal.get('direction') != 'ERROR':
                        # Calculate strength score based on signal confidence and direction
                        base_strength = signal['confidence'] / 100.0
                        direction_multiplier = 1.0 if signal['direction'] == 'BUY' else -1.0
                        strength_data[symbol] = base_strength * direction_multiplier
                except Exception as e:
                    self.logger.warning(f"Failed to get strength for {symbol}: {e}")

            # Calculate relative strength
            strength_ranking = self._calculate_relative_strength(strength_data)

            return {
                'currency_strength': strength_data,
                'strength_ranking': strength_ranking,
                'strongest_currency': max(strength_data.items(), key=lambda x: x[1]) if strength_data else None,
                'weakest_currency': min(strength_data.items(), key=lambda x: x[1]) if strength_data else None,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error analyzing currency strength: {e}")
            return self._error_result(str(e))

    def get_market_regime_analysis(self) -> Dict:
        """Analyze current market regime (trending, ranging, volatile)"""
        try:
            # Get volatility and trend data from multiple markets
            from international_signal_api import get_international_signal, get_international_symbols

            symbols = get_international_symbols()
            regime_indicators = {}

            for symbol in symbols:
                try:
                    signal = get_international_signal(symbol)
                    if signal and signal.get('direction') != 'ERROR':
                        regime_indicators[symbol] = {
                            'trend': signal['technical_indicators'].get('trend', 'unknown'),
                            'volatility': signal['market_data'].get('volatility', 'unknown'),
                            'rsi': signal['technical_indicators'].get('rsi')
                        }
                except Exception as e:
                    self.logger.warning(f"Failed to get regime data for {symbol}: {e}")

            # Determine overall market regime
            overall_regime = self._determine_market_regime(regime_indicators)

            return {
                'market_regime_indicators': regime_indicators,
                'overall_regime': overall_regime,
                'regime_confidence': self._calculate_regime_confidence(regime_indicators),
                'trading_implications': self._get_regime_trading_implications(overall_regime),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error analyzing market regime: {e}")
            return self._error_result(str(e))

    def _get_price_data(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """Get historical price data for correlation analysis"""
        try:
            # Try to get cached data first
            cache_key = f"price_data_{symbol}_{days}d"
            if self.cache_manager:
                cached_data = self.cache_manager.get(cache_key)
                if cached_data:
                    return pd.DataFrame(cached_data)

            # Fetch fresh data
            if self.data_fetcher:
                # Use data fetcher if available
                data = self.data_fetcher.fetch_forex_data(f"USD{symbol}", days * 24 * 60)  # minutes
            else:
                # Generate sample data for demo
                data = self._generate_sample_price_data(symbol, days)

            # Cache the data
            if self.cache_manager and data is not None:
                self.cache_manager.set(cache_key, data.to_dict('records'), ttl=3600)  # Cache for 1 hour

            return data

        except Exception as e:
            self.logger.warning(f"Failed to get price data for {symbol}: {e}")
            return None

    def _generate_sample_price_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Generate sample price data for demonstration"""
        # Different base prices and volatilities for each symbol
        symbol_params = {
            'CNY': {'base': 7.15, 'volatility': 0.0005},
            'JPY': {'base': 147.50, 'volatility': 0.0003},
            'EUR': {'base': 1.0850, 'volatility': 0.0008},
            'GBP': {'base': 1.2750, 'volatility': 0.0012},
            'AUD': {'base': 0.6620, 'volatility': 0.0009},
            'BRL': {'base': 5.4321, 'volatility': 0.0015},
            'ETH': {'base': 3456.78, 'volatility': 0.02}
        }

        params = symbol_params.get(symbol, {'base': 1.0, 'volatility': 0.001})
        base_price = params['base']
        volatility = params['volatility']

        periods = days * 24 * 12  # 5-minute intervals
        np.random.seed(hash(symbol) % 2**32)  # Reproducible seed per symbol

        # Generate price series
        returns = np.random.normal(0, volatility, periods)
        prices = base_price * np.exp(np.cumsum(returns))

        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=periods, freq='5min'),
            'close': prices,
            'symbol': symbol
        })

        return data

    def _calculate_correlation_matrix(self, price_data: Dict) -> Dict:
        """Calculate correlation matrix from price data"""
        try:
            # Extract close prices and align dates
            aligned_prices = {}

            # Get common date range
            all_dates = set()
            for symbol, data in price_data.items():
                all_dates.update(data['timestamp'].values)

            common_dates = sorted(list(all_dates))[-min(1000, len(all_dates)):]  # Last 1000 periods

            # Align prices to common dates
            for symbol, data in price_data.items():
                data_dict = dict(zip(data['timestamp'], data['close']))
                aligned_prices[symbol] = [data_dict.get(date) for date in common_dates if data_dict.get(date) is not None]

            # Remove None values and ensure equal length
            min_length = min(len(prices) for prices in aligned_prices.values())
            for symbol in aligned_prices:
                aligned_prices[symbol] = aligned_prices[symbol][:min_length]

            # Calculate correlations
            correlation_matrix = {}
            symbols = list(aligned_prices.keys())

            for i, symbol1 in enumerate(symbols):
                correlation_matrix[symbol1] = {}
                for symbol2 in symbols:
                    if symbol1 == symbol2:
                        correlation_matrix[symbol1][symbol2] = 1.0
                    else:
                        prices1 = aligned_prices[symbol1]
                        prices2 = aligned_prices[symbol2]

                        if len(prices1) == len(prices2) and len(prices1) > 10:
                            try:
                                corr = np.corrcoef(prices1, prices2)[0, 1]
                                correlation_matrix[symbol1][symbol2] = round(corr, 3)
                            except:
                                correlation_matrix[symbol1][symbol2] = 0.0
                        else:
                            correlation_matrix[symbol1][symbol2] = 0.0

            return correlation_matrix

        except Exception as e:
            self.logger.error(f"Error calculating correlation matrix: {e}")
            return {}

    def _generate_correlation_insights(self, correlation_matrix: Dict) -> List[str]:
        """Generate insights from correlation matrix"""
        insights = []

        try:
            symbols = list(correlation_matrix.keys())

            # Find highly correlated pairs
            high_corr_pairs = []
            for i, symbol1 in enumerate(symbols):
                for symbol2 in symbols[i+1:]:
                    corr = correlation_matrix[symbol1].get(symbol2, 0)
                    if abs(corr) > 0.7:
                        high_corr_pairs.append((symbol1, symbol2, corr))

            if high_corr_pairs:
                insights.append(f"🔗 High correlation detected between: {', '.join([f'{pair[0]}-{pair[1]} ({pair[2]:.2f})' for pair in high_corr_pairs[:3]])}")

            # Find uncorrelated pairs (diversification opportunities)
            low_corr_pairs = []
            for i, symbol1 in enumerate(symbols):
                for symbol2 in symbols[i+1:]:
                    corr = correlation_matrix[symbol1].get(symbol2, 0)
                    if abs(corr) < 0.3:
                        low_corr_pairs.append((symbol1, symbol2, corr))

            if low_corr_pairs:
                insights.append(f"🔀 Low correlation (diversification): {', '.join([f'{pair[0]}-{pair[1]}' for pair in low_corr_pairs[:3]])}")

            # Market group analysis
            for group_name, group_symbols in self.market_groups.items():
                group_corrs = []
                available_symbols = [s for s in group_symbols if s in symbols]

                if len(available_symbols) >= 2:
                    for i, sym1 in enumerate(available_symbols):
                        for sym2 in available_symbols[i+1:]:
                            corr = correlation_matrix[sym1].get(sym2, 0)
                            group_corrs.append(corr)

                    if group_corrs:
                        avg_corr = sum(group_corrs) / len(group_corrs)
                        insights.append(f"📊 {group_name.replace('_', ' ').title()}: Average correlation {avg_corr:.2f}")

        except Exception as e:
            self.logger.error(f"Error generating correlation insights: {e}")

        return insights

    def _analyze_cross_market_relationships(self, market_signals: Dict, base_symbol: str) -> Dict:
        """Analyze relationships between different market signals"""
        cross_signals = {}

        try:
            # Analyze how other markets might influence the base symbol
            base_signal = market_signals.get(base_symbol)

            if not base_signal or base_signal.get('direction') == 'ERROR':
                return cross_signals

            for symbol, signal in market_signals.items():
                if symbol == base_symbol or signal.get('direction') == 'ERROR':
                    continue

                # Calculate influence score
                influence_score = self._calculate_market_influence(base_signal, signal)

                cross_signals[symbol] = {
                    'influence_score': influence_score,
                    'relationship_type': self._determine_relationship_type(symbol, base_symbol),
                    'signal_alignment': 'supporting' if influence_score > 0 else 'conflicting',
                    'strength': 'strong' if abs(influence_score) > 0.7 else 'moderate' if abs(influence_score) > 0.4 else 'weak'
                }

        except Exception as e:
            self.logger.error(f"Error analyzing cross-market relationships: {e}")

        return cross_signals

    def _calculate_market_influence(self, base_signal: Dict, other_signal: Dict) -> float:
        """Calculate how much one market influences another"""
        try:
            # Simple influence calculation based on correlation and signal strength
            base_confidence = base_signal.get('confidence', 0) / 100.0
            other_confidence = other_signal.get('confidence', 0) / 100.0

            # Direction alignment (1 if same direction, -1 if opposite)
            base_direction = 1 if base_signal.get('direction') == 'BUY' else -1
            other_direction = 1 if other_signal.get('direction') == 'BUY' else -1
            direction_alignment = 1 if base_direction == other_direction else -1

            # Influence based on confidence and direction alignment
            influence = (base_confidence + other_confidence) / 2 * direction_alignment

            return round(influence, 2)

        except Exception:
            return 0.0

    def _determine_relationship_type(self, symbol1: str, symbol2: str) -> str:
        """Determine the type of relationship between two markets"""
        # Define relationship types based on market knowledge
        relationships = {
            ('EUR', 'GBP'): 'European Cousins',
            ('EUR', 'JPY'): 'Risk Reversal',
            ('GBP', 'JPY'): 'Risk Reversal',
            ('AUD', 'CNY'): 'China Exposure',
            ('ETH', 'EUR'): 'Crypto vs Traditional',
            ('BRL', 'EUR'): 'Emerging vs Developed'
        }

        return relationships.get((symbol1, symbol2), relationships.get((symbol2, symbol1), 'General Correlation'))

    def _generate_combined_signal(self, market_signals: Dict, cross_signals: Dict) -> Dict:
        """Generate a combined signal from all market analysis"""
        try:
            # Calculate weighted average of all signals
            total_weight = 0
            weighted_directions = {'BUY': 0, 'SELL': 0, 'HOLD': 0}

            for symbol, signal in market_signals.items():
                if signal.get('direction') == 'ERROR':
                    continue

                weight = signal.get('confidence', 0) / 100.0

                # Apply cross-market influence
                if symbol in cross_signals:
                    influence = cross_signals[symbol]['influence_score']
                    weight *= (1 + influence)  # Boost or reduce weight based on influence

                direction = signal.get('direction', 'HOLD')
                weighted_directions[direction] += weight
                total_weight += weight

            # Determine combined direction
            if total_weight > 0:
                avg_buy = weighted_directions['BUY'] / total_weight
                avg_sell = weighted_directions['SELL'] / total_weight

                if avg_buy > 0.6:
                    combined_direction = 'BUY'
                    confidence = min(avg_buy * 100, 95)
                elif avg_sell > 0.6:
                    combined_direction = 'SELL'
                    confidence = min(avg_sell * 100, 95)
                else:
                    combined_direction = 'HOLD'
                    confidence = 50
            else:
                combined_direction = 'HOLD'
                confidence = 0

            return {
                'direction': combined_direction,
                'confidence': round(confidence, 1),
                'markets_analyzed': len(market_signals),
                'supporting_signals': sum(1 for cs in cross_signals.values() if cs.get('signal_alignment') == 'supporting'),
                'conflicting_signals': sum(1 for cs in cross_signals.values() if cs.get('signal_alignment') == 'conflicting'),
                'analysis_type': 'Cross-Market Combined Signal'
            }

        except Exception as e:
            self.logger.error(f"Error generating combined signal: {e}")
            return {'direction': 'HOLD', 'confidence': 0, 'error': str(e)}

    def _is_session_active(self, current_hour: int, session_info: Dict) -> bool:
        """Check if a market session is currently active"""
        start = session_info['start']
        end = session_info['end']

        if start < end:
            return start <= current_hour < end
        else:  # Session spans midnight
            return current_hour >= start or current_hour < end

    def _get_session_markets(self, session_name: str) -> List[str]:
        """Get markets active in a specific session"""
        session_markets = {
            'asian': ['CNY', 'JPY'],
            'european': ['EUR', 'GBP'],
            'american': ['BRL'],
            'pacific': ['AUD']
        }
        return session_markets.get(session_name, [])

    def _generate_session_insights(self, active_sessions: List[Dict]) -> List[str]:
        """Generate insights about current market sessions"""
        insights = []

        if not active_sessions:
            insights.append("🌙 No major market sessions currently active")
            return insights

        insights.append(f"🕐 Active Sessions: {', '.join([s['name'] for s in active_sessions])}")

        for session in active_sessions:
            markets = session['markets']
            if markets:
                insights.append(f"📊 {session['name']}: {', '.join(markets)} active")

        return insights

    def _get_next_session(self, current_hour: int) -> Dict:
        """Get information about the next market session"""
        try:
            # Find the next session start time
            next_sessions = []

            for session_name, session_info in self.market_sessions.items():
                start_hour = session_info['start']

                if start_hour > current_hour:
                    hours_until = start_hour - current_hour
                else:
                    hours_until = (24 - current_hour) + start_hour

                next_sessions.append({
                    'name': session_info['name'],
                    'hours_until': hours_until,
                    'markets': self._get_session_markets(session_name)
                })

            if next_sessions:
                next_session = min(next_sessions, key=lambda x: x['hours_until'])
                return next_session

        except Exception as e:
            self.logger.error(f"Error calculating next session: {e}")

        return {'name': 'Unknown', 'hours_until': 0, 'markets': []}

    def _calculate_relative_strength(self, strength_data: Dict) -> List[Tuple[str, float]]:
        """Calculate relative currency strength ranking"""
        try:
            # Sort by strength score
            ranking = sorted(strength_data.items(), key=lambda x: x[1], reverse=True)
            return ranking
        except Exception:
            return []

    def _determine_market_regime(self, regime_indicators: Dict) -> str:
        """Determine overall market regime"""
        try:
            if not regime_indicators:
                return 'unknown'

            # Count different regime indicators
            trending_count = 0
            ranging_count = 0
            volatile_count = 0

            for symbol, indicators in regime_indicators.items():
                trend = indicators.get('trend', 'unknown')
                volatility = indicators.get('volatility', 'unknown')
                rsi = indicators.get('rsi')

                # Trend analysis
                if trend in ['bullish', 'bearish']:
                    trending_count += 1
                elif trend == 'sideways':
                    ranging_count += 1

                # Volatility analysis
                if volatility in ['High', 'Extreme']:
                    volatile_count += 1

                # RSI extremes
                if rsi and (rsi < 30 or rsi > 70):
                    volatile_count += 0.5

            total_markets = len(regime_indicators)

            # Determine regime
            if trending_count > total_markets * 0.6:
                return 'trending'
            elif ranging_count > total_markets * 0.6:
                return 'ranging'
            elif volatile_count > total_markets * 0.4:
                return 'volatile'
            else:
                return 'mixed'

        except Exception:
            return 'unknown'

    def _calculate_regime_confidence(self, regime_indicators: Dict) -> float:
        """Calculate confidence in the regime determination"""
        try:
            if not regime_indicators:
                return 0.0

            # Calculate consistency of regime indicators
            trend_consistency = 0
            volatility_consistency = 0

            trends = [indicators.get('trend') for indicators in regime_indicators.values()]
            volatilities = [indicators.get('volatility') for indicators in regime_indicators.values()]

            # Trend consistency (how many agree)
            valid_trends = [t for t in trends if t and t != 'unknown']
            if valid_trends:
                most_common_trend = max(set(valid_trends), key=valid_trends.count)
                trend_consistency = valid_trends.count(most_common_trend) / len(valid_trends)

            # Volatility consistency
            valid_vols = [v for v in volatilities if v and v != 'unknown']
            if valid_vols:
                most_common_vol = max(set(valid_vols), key=valid_vols.count)
                volatility_consistency = valid_vols.count(most_common_vol) / len(valid_vols)

            return round((trend_consistency + volatility_consistency) / 2, 2)

        except Exception:
            return 0.0

    def _get_regime_trading_implications(self, regime: str) -> List[str]:
        """Get trading implications for the current market regime"""
        implications = {
            'trending': [
                '📈 Trend-following strategies preferred',
                '🎯 Higher probability of continuation signals',
                '⚡ Momentum indicators more reliable',
                '🚫 Avoid counter-trend trades'
            ],
            'ranging': [
                '🔄 Range-trading strategies preferred',
                '🎯 Support/resistance levels important',
                '⚡ Mean-reversion strategies effective',
                '🚫 Trend-following may produce false signals'
            ],
            'volatile': [
                '⚠️ Higher risk environment',
                '🎯 Wider stop losses required',
                '💰 Larger position sizing possible',
                '🚫 Tight risk management essential'
            ],
            'mixed': [
                '🔀 Mixed signals across markets',
                '🎯 Focus on strongest individual signals',
                '⚡ Cross-market confirmation important',
                '🚫 Avoid weak or conflicting signals'
            ],
            'unknown': [
                '❓ Unclear market regime',
                '🎯 Use conservative position sizing',
                '⚡ Wait for clearer signals',
                '🚫 Avoid aggressive trading'
            ]
        }

        return implications.get(regime, implications['unknown'])

    def _error_result(self, message: str) -> Dict:
        """Return standardized error result"""
        return {
            'status': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

# Global instance
international_analytics = InternationalAnalytics()

# Convenience functions
def get_market_correlations(symbols: List[str] = None, period_days: int = 30) -> Dict:
    """Convenience function for market correlations"""
    return international_analytics.get_market_correlations(symbols, period_days)

def get_cross_market_signals(base_symbol: str = 'EUR') -> Dict:
    """Convenience function for cross-market signals"""
    return international_analytics.get_cross_market_signals(base_symbol)

def get_market_session_analysis() -> Dict:
    """Convenience function for session analysis"""
    return international_analytics.get_market_session_analysis()

def get_currency_strength_analysis() -> Dict:
    """Convenience function for currency strength"""
    return international_analytics.get_currency_strength_analysis()

def get_market_regime_analysis() -> Dict:
    """Convenience function for market regime analysis"""
    return international_analytics.get_market_regime_analysis()

# Example usage
if __name__ == "__main__":
    print("International Analytics Test")
    print("=" * 50)

    # Test correlation analysis
    print("\n1. Market Correlations:")
    correlations = get_market_correlations()
    if correlations.get('status') == 'success':
        print(f"Symbols analyzed: {correlations['symbols_analyzed']}")
        for insight in correlations.get('insights', []):
            print(f"  {insight}")
    else:
        print(f"Error: {correlations.get('message')}")

    # Test cross-market signals
    print("\n2. Cross-Market Signals:")
    cross_signals = get_cross_market_signals('EUR')
    if cross_signals.get('status') == 'success':
        combined = cross_signals.get('combined_signal', {})
        print(f"Combined EUR signal: {combined.get('direction')} ({combined.get('confidence')}%)")
        print(f"Markets supporting: {combined.get('supporting_signals', 0)}")
    else:
        print(f"Error: {cross_signals.get('message')}")

    # Test session analysis
    print("\n3. Market Session Analysis:")
    sessions = get_market_session_analysis()
    if sessions.get('status') == 'success':
        active = sessions.get('active_sessions', [])
        if active:
            print(f"Active sessions: {', '.join([s['name'] for s in active])}")
        else:
            print("No active sessions")
    else:
        print(f"Error: {sessions.get('message')}")

    print("\nInternational Analytics test completed!")
