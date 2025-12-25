"""
Ethereum (ETH) Futures Signal Generator
Provides professional trading signals for ETH/USD futures contracts
Crypto futures with high volatility and 24/7 trading
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

class ETHSignalGenerator:
    """Generate trading signals for ETH/USD futures"""

    def __init__(self, data_fetcher=None):
        self.symbol = "ETHUSD"
        self.name = "ETH/USD Futures"
        self.description = "Ethereum Futures Contract"
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)

        # Risk parameters for crypto futures (very high volatility)
        self.risk_params = {
            'stop_loss_percentage': 3.0,  # Percentage-based stops for crypto
            'take_profit_1_percentage': 6.0,
            'take_profit_2_percentage': 12.0,
            'max_leverage': 5,  # Typical crypto futures leverage
            'min_volume': 0.1,  # ETH contracts
            'max_volume': 100.0,
            'volatility_multiplier': 3.0  # Very high volatility
        }

        # Timeframes to analyze (crypto trades 24/7)
        self.timeframes = ['M15', 'H1', 'H4', 'D1']

        # Crypto-specific factors
        self.crypto_factors = {
            'market_cap_rank': 2,  # After Bitcoin
            'network_upgrades': 'active',  # Ethereum has frequent upgrades
            'defi_ecosystem': 'large',  # Major DeFi ecosystem
            'institutional_adoption': 'growing',
            'correlation_to_btc': 0.7  # Typically correlated to BTC
        }

    def generate_signal(self) -> Dict:
        """Generate comprehensive trading signal for ETH futures"""
        try:
            # Fetch market data for all timeframes
            market_data = self._fetch_market_data()

            if not market_data:
                return self._empty_signal("Unable to fetch market data")

            # Perform technical analysis
            technical_analysis = self._perform_technical_analysis(market_data)

            # Calculate signal strength and confidence
            signal_data = self._calculate_signal_strength(technical_analysis)

            # Apply crypto-specific adjustments
            adjusted_signal = self._apply_crypto_adjustments(signal_data, technical_analysis)

            # Generate final signal
            signal = self._generate_final_signal(adjusted_signal, technical_analysis)

            return signal

        except Exception as e:
            self.logger.error(f"Error generating ETH signal: {str(e)}")
            return self._empty_signal(f"Signal generation error: {str(e)}")

    def _fetch_market_data(self) -> Dict:
        """Fetch market data for ETH/USD futures across all timeframes"""
        market_data = {}

        for timeframe in self.timeframes:
            try:
                # Use data fetcher or fallback to sample data for demo
                if self.data_fetcher:
                    data = self.data_fetcher.fetch_crypto_data("ETHUSD", timeframe, limit=200)
                else:
                    data = self._get_sample_data(timeframe)

                if data is not None and len(data) > 0:
                    market_data[timeframe] = data

            except Exception as e:
                self.logger.warning(f"Failed to fetch {timeframe} data: {str(e)}")

        return market_data

    def _get_sample_data(self, timeframe: str) -> pd.DataFrame:
        """Generate sample data for demonstration (replace with real data)"""
        # Generate realistic ETH price data (Ethereum is around $2,500-4,000)
        base_price = 3200.0  # Current approximate ETH price
        periods = 200

        # Generate price series with very high volatility (crypto)
        np.random.seed(42)  # For reproducible results
        returns = np.random.normal(0, 0.005, periods)  # High volatility for crypto
        prices = base_price * np.exp(np.cumsum(returns))

        # Create OHLC data with very wide ranges (crypto volatility)
        highs = prices * (1 + np.random.uniform(0, 0.02, periods))  # Very wide ranges
        lows = prices * (1 - np.random.uniform(0, 0.02, periods))
        opens = np.roll(prices, 1)
        opens[0] = base_price

        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=periods, freq='15min' if timeframe == 'M15' else '1H'),
            'open': opens,
            'high': highs,
            'low': lows,
            'close': prices,
            'volume': np.random.randint(100000, 10000000, periods),  # High volume crypto
            'oi': np.random.randint(1000000, 10000000, periods)  # Open interest
        })

        return data

    def _perform_technical_analysis(self, market_data: Dict) -> Dict:
        """Perform comprehensive technical analysis for crypto"""
        analysis = {}

        for timeframe, data in market_data.items():
            try:
                analysis[timeframe] = self._analyze_timeframe(data, timeframe)
            except Exception as e:
                self.logger.warning(f"Analysis failed for {timeframe}: {str(e)}")

        return analysis

    def _analyze_timeframe(self, data: pd.DataFrame, timeframe: str) -> Dict:
        """Analyze a specific timeframe with crypto-specific considerations"""
        close_prices = data['close'].values
        high_prices = data['high'].values
        low_prices = data['low'].values
        volume = data['volume'].values if 'volume' in data.columns else np.ones(len(close_prices))

        # Moving averages (crypto often uses shorter periods)
        sma_10 = self._calculate_sma(close_prices, 10)  # Shorter for crypto
        sma_30 = self._calculate_sma(close_prices, 30)
        ema_12 = self._calculate_ema(close_prices, 12)

        # RSI (crypto can be more extreme)
        rsi = self._calculate_rsi(close_prices, 14)

        # MACD (crypto favorite indicator)
        macd_line, signal_line, histogram = self._calculate_macd(close_prices, fast=8, slow=21, signal=5)  # Shorter for crypto

        # Bollinger Bands (wider for crypto volatility)
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close_prices, period=20, std_dev=3.0)

        # Support and Resistance
        support, resistance = self._find_support_resistance(high_prices, low_prices)

        # Trend analysis
        trend = self._determine_trend(sma_10, sma_30, ema_12)

        # Volatility analysis (crucial for crypto)
        volatility = self._calculate_volatility(close_prices)

        # Volume analysis (important for crypto)
        volume_analysis = self._analyze_volume(volume)

        # Momentum indicators (crypto specific)
        momentum = self._calculate_momentum(close_prices)

        return {
            'sma_10': sma_10[-1] if len(sma_10) > 0 else None,
            'sma_30': sma_30[-1] if len(sma_30) > 0 else None,
            'ema_12': ema_12[-1] if len(ema_12) > 0 else None,
            'rsi': rsi[-1] if len(rsi) > 0 else None,
            'macd': {
                'line': macd_line[-1] if len(macd_line) > 0 else None,
                'signal': signal_line[-1] if len(signal_line) > 0 else None,
                'histogram': histogram[-1] if len(histogram) > 0 else None
            },
            'bollinger': {
                'upper': bb_upper[-1] if len(bb_upper) > 0 else None,
                'middle': bb_middle[-1] if len(bb_middle) > 0 else None,
                'lower': bb_lower[-1] if len(bb_lower) > 0 else None
            },
            'support': support,
            'resistance': resistance,
            'trend': trend,
            'volatility': volatility,
            'volume_analysis': volume_analysis,
            'momentum': momentum,
            'current_price': close_prices[-1],
            'previous_price': close_prices[-2] if len(close_prices) > 1 else close_prices[-1]
        }

    def _calculate_momentum(self, prices: np.ndarray, period: int = 10) -> float:
        """Calculate momentum indicator (popular in crypto)"""
        if len(prices) < period + 1:
            return 0.0

        current = prices[-1]
        past = prices[-period-1]
        momentum = (current - past) / past * 100
        return momentum

    def _calculate_volatility(self, prices: np.ndarray, period: int = 20) -> float:
        """Calculate price volatility (very important for crypto risk management)"""
        if len(prices) < period:
            return 0.0

        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns[-period:]) * np.sqrt(365 * 24)  # Very high frequency
        return volatility

    def _analyze_volume(self, volumes: np.ndarray) -> Dict:
        """Analyze trading volume patterns (crucial for crypto)"""
        if len(volumes) < 20:
            return {'trend': 'unknown', 'average': 0, 'intensity': 'unknown'}

        avg_volume = np.mean(volumes[-20:])
        recent_volume = np.mean(volumes[-5:])

        volume_trend = 'increasing' if recent_volume > avg_volume * 1.2 else 'decreasing' if recent_volume < avg_volume * 0.8 else 'stable'

        # Assess volume intensity (crypto can have extreme volume spikes)
        intensity = 'extreme' if recent_volume > avg_volume * 2 else 'high' if recent_volume > avg_volume * 1.5 else 'normal' if recent_volume > avg_volume * 0.8 else 'low'

        return {
            'trend': volume_trend,
            'average': avg_volume,
            'intensity': intensity
        }

    # [Technical indicator methods remain the same as previous generators]
    def _calculate_sma(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return np.array([])
        return pd.Series(prices).rolling(window=period).mean().values

    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.array([])
        return pd.Series(prices).ewm(span=period).mean().values

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return np.array([])

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gains = pd.Series(gains).rolling(window=period).mean().values
        avg_losses = pd.Series(losses).rolling(window=period).mean().values

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_macd(self, prices: np.ndarray, fast=8, slow=21, signal=5) -> Tuple:
        """Calculate MACD indicator (crypto-tuned parameters)"""
        if len(prices) < slow:
            return np.array([]), np.array([]), np.array([])

        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)

        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 3.0):
        """Calculate Bollinger Bands (wider for crypto volatility)"""
        if len(prices) < period:
            return np.array([]), np.array([]), np.array([])

        sma = self._calculate_sma(prices, period)
        std = pd.Series(prices).rolling(window=period).std().values

        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        return upper, sma, lower

    def _find_support_resistance(self, highs: np.ndarray, lows: np.ndarray, lookback: int = 20) -> Tuple:
        """Find support and resistance levels"""
        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]

        support = np.min(recent_lows)
        resistance = np.max(recent_highs)

        return support, resistance

    def _determine_trend(self, sma_10: float, sma_30: float, ema_12: float) -> str:
        """Determine market trend"""
        if sma_10 and sma_30 and ema_12:
            if sma_10 > sma_30 and ema_12 > sma_30:
                return "bullish"
            elif sma_10 < sma_30 and ema_12 < sma_30:
                return "bearish"
            else:
                return "sideways"
        return "unknown"

    def _apply_crypto_adjustments(self, signal_data: Dict, technical_analysis: Dict) -> Dict:
        """Apply crypto-specific adjustments to signals"""
        adjusted_data = signal_data.copy()

        # Get current analysis
        current_analysis = technical_analysis.get('H1', technical_analysis.get('M15', {}))

        # Adjust confidence based on crypto factors
        base_confidence = signal_data['confidence']

        # Volume intensity adjustment (crypto can have extreme volume)
        volume_analysis = current_analysis.get('volume_analysis', {})
        if volume_analysis.get('intensity') in ['extreme', 'high']:
            base_confidence *= 1.1  # Increase confidence for high volume
            adjusted_data['high_volume_confirmation'] = True
        elif volume_analysis.get('intensity') == 'low':
            base_confidence *= 0.9  # Decrease confidence for low volume

        # Volatility adjustment (crypto is very volatile)
        volatility = current_analysis.get('volatility', 0)
        if volatility > 0.1:  # Very high volatility
            base_confidence *= 0.95  # Slight reduction but still tradeable

        # Momentum adjustment (crypto often trends strongly)
        momentum = current_analysis.get('momentum', 0)
        if abs(momentum) > 5:  # Strong momentum
            base_confidence *= 1.05  # Increase confidence

        adjusted_data['confidence'] = min(base_confidence, 95)  # Cap at 95%

        return adjusted_data

    def _calculate_signal_strength(self, technical_analysis: Dict) -> Dict:
        """Calculate overall signal strength and direction for crypto"""
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0

        # Weight different timeframes (crypto favors shorter timeframes)
        timeframe_weights = {'M15': 2, 'H1': 3, 'H4': 2, 'D1': 1}

        for timeframe, analysis in technical_analysis.items():
            weight = timeframe_weights.get(timeframe, 1)

            # RSI signals (crypto can be more extreme)
            if analysis.get('rsi'):
                if analysis['rsi'] < 25:  # More extreme for crypto
                    bullish_signals += weight * 1.5  # Extra weight
                elif analysis['rsi'] > 75:
                    bearish_signals += weight * 1.5
                total_signals += weight

            # MACD signals (very popular in crypto)
            macd = analysis.get('macd', {})
            if macd.get('histogram'):
                histogram_strength = abs(macd['histogram'])
                if macd['histogram'] > 0:
                    bullish_signals += weight * (1 + histogram_strength * 10)  # Stronger signals
                else:
                    bearish_signals += weight * (1 + histogram_strength * 10)
                total_signals += weight

            # Bollinger Band signals
            bb = analysis.get('bollinger', {})
            current_price = analysis.get('current_price')
            if current_price and bb.get('lower') and bb.get('upper'):
                if current_price < bb['lower']:
                    bullish_signals += weight * 1.2  # Bollinger signals are strong in crypto
                elif current_price > bb['upper']:
                    bearish_signals += weight * 1.2
                total_signals += weight

            # Trend signals
            trend = analysis.get('trend')
            if trend == 'bullish':
                bullish_signals += weight * 2  # Trend is very important in crypto
            elif trend == 'bearish':
                bearish_signals += weight * 2
            total_signals += weight * 2

            # Momentum signals (crypto specific)
            momentum = analysis.get('momentum', 0)
            if momentum > 3:
                bullish_signals += weight
            elif momentum < -3:
                bearish_signals += weight
            total_signals += weight

        # Calculate confidence
        if total_signals > 0:
            bullish_percentage = bullish_signals / total_signals
            bearish_percentage = bearish_signals / total_signals

            if bullish_percentage > 0.55:
                direction = "BUY"
                confidence = min(bullish_percentage * 100, 95)
            elif bearish_percentage > 0.55:
                direction = "SELL"
                confidence = min(bearish_percentage * 100, 95)
            else:
                direction = "HOLD"
                confidence = 50
        else:
            direction = "HOLD"
            confidence = 0

        return {
            'direction': direction,
            'confidence': confidence,
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'total_signals': total_signals,
            'crypto_adjusted': True
        }

    def _generate_final_signal(self, signal_data: Dict, technical_analysis: Dict) -> Dict:
        """Generate the final comprehensive signal for crypto futures"""
        direction = signal_data['direction']
        confidence = signal_data['confidence']

        # Get current market data
        current_analysis = technical_analysis.get('M15', {})

        # Entry and exit levels (percentage-based for crypto)
        current_price = current_analysis.get('current_price', 3200.0)
        support = current_analysis.get('support', current_price * 0.9)
        resistance = current_analysis.get('resistance', current_price * 1.1)

        if direction == "BUY":
            entry_price = current_price
            stop_loss = entry_price * (1 - self.risk_params['stop_loss_percentage'] / 100)
            take_profit_1 = entry_price * (1 + self.risk_params['take_profit_1_percentage'] / 100)
            take_profit_2 = entry_price * (1 + self.risk_params['take_profit_2_percentage'] / 100)
        elif direction == "SELL":
            entry_price = current_price
            stop_loss = entry_price * (1 + self.risk_params['stop_loss_percentage'] / 100)
            take_profit_1 = entry_price * (1 - self.risk_params['take_profit_1_percentage'] / 100)
            take_profit_2 = entry_price * (1 - self.risk_params['take_profit_2_percentage'] / 100)
        else:
            entry_price = current_price
            stop_loss = current_price * 0.85
            take_profit_1 = current_price * 1.15
            take_profit_2 = current_price * 1.3

        # Calculate risk-reward ratio
        risk = abs(entry_price - stop_loss) / entry_price * 100  # Percentage
        reward_1 = abs(take_profit_1 - entry_price) / entry_price * 100
        reward_2 = abs(take_profit_2 - entry_price) / entry_price * 100
        rr_ratio = reward_1 / risk if risk > 0 else 0

        # Get crypto-specific data
        volume_analysis = current_analysis.get('volume_analysis', {})
        volatility = current_analysis.get('volatility', 0)
        momentum = current_analysis.get('momentum', 0)

        # Generate signal
        signal = {
            'symbol': self.symbol,
            'name': self.name,
            'description': self.description,
            'timestamp': datetime.now().isoformat(),
            'direction': direction,
            'confidence': round(confidence, 1),
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'risk_reward_ratio': round(rr_ratio, 2),
            'technical_indicators': {
                'rsi': current_analysis.get('rsi'),
                'trend': current_analysis.get('trend'),
                'support': round(support, 2),
                'resistance': round(resistance, 2),
                'volatility': round(volatility, 4),
                'momentum': round(momentum, 2),
                'volume_intensity': volume_analysis.get('intensity', 'unknown')
            },
            'market_data': {
                'current_price': round(current_price, 2),
                'daily_range': round(resistance - support, 2),
                'volatility': 'Extreme' if volatility > 0.05 else 'High',
                'market_type': 'Crypto Futures',
                'leverage_available': f"Up to {self.risk_params['max_leverage']}x"
            },
            'trading_hours': '24/7 (Crypto markets never sleep)',
            'spread_typical': 'Variable (typically 0.1-0.5%)',
            'recommended_volume': f"{self.risk_params['min_volume']:.1f} - {self.risk_params['max_volume']:.1f} ETH",
            'signal_quality': self._assess_signal_quality(confidence, rr_ratio),
            'crypto_factors': self.crypto_factors,
            'crypto_warnings': self._get_crypto_warnings(signal_data),
            'analysis_summary': self._generate_analysis_summary(signal_data, current_analysis)
        }

        return signal

    def _get_crypto_warnings(self, signal_data: Dict) -> List[str]:
        """Get crypto-specific warnings"""
        warnings = []

        if signal_data.get('high_volume_confirmation'):
            warnings.append("High volume confirms signal strength")

        warnings.extend([
            "Extreme volatility - use tight risk management",
            "24/7 market - monitor positions continuously",
            "High leverage available - use responsibly",
            "Crypto markets can gap significantly"
        ])

        if self.crypto_factors['correlation_to_btc'] > 0.5:
            warnings.append("Strong correlation to BTC - monitor Bitcoin price")

        return warnings

    def _assess_signal_quality(self, confidence: float, rr_ratio: float) -> str:
        """Assess overall signal quality for crypto futures"""
        if confidence >= 80 and rr_ratio >= 1.5:
            return "A+ (Excellent for Crypto)"
        elif confidence >= 70 and rr_ratio >= 1.2:
            return "A (Very Good for Crypto)"
        elif confidence >= 60 and rr_ratio >= 1.0:
            return "B+ (Good for Crypto)"
        elif confidence >= 50:
            return "B (Moderate for Crypto)"
        else:
            return "C (Weak - High Risk)"

    def _generate_analysis_summary(self, signal_data: Dict, analysis: Dict) -> str:
        """Generate human-readable analysis summary for crypto"""
        direction = signal_data['direction']
        confidence = signal_data['confidence']
        trend = analysis.get('trend', 'unknown')
        rsi = analysis.get('rsi')
        momentum = analysis.get('momentum', 0)
        volatility = analysis.get('volatility', 0)

        summary = f"ETH futures analysis shows {direction.lower()} signal with {confidence:.1f}% confidence. "

        if trend != 'unknown':
            summary += f"Market trend is {trend}. "

        if rsi:
            if rsi < 25:
                summary += "RSI indicates extreme oversold conditions. "
            elif rsi > 75:
                summary += "RSI indicates extreme overbought conditions. "
            else:
                summary += "RSI is in normal range. "

        if abs(momentum) > 5:
            direction_word = "upward" if momentum > 0 else "downward"
            summary += f"Strong {direction_word} momentum detected. "

        if volatility > 0.05:
            summary += "Extreme volatility environment. "

        summary += "ETH is the second-largest cryptocurrency with strong DeFi ecosystem exposure."

        return summary

    def _empty_signal(self, reason: str = "No data available") -> Dict:
        """Return empty signal structure"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'description': self.description,
            'timestamp': datetime.now().isoformat(),
            'direction': 'HOLD',
            'confidence': 0,
            'message': reason,
            'signal_quality': 'N/A',
            'market_type': 'Crypto Futures'
        }

# Example usage
if __name__ == "__main__":
    generator = ETHSignalGenerator()
    signal = generator.generate_signal()

    print("ETH/USD Futures Signal:")
    print(f"Direction: {signal['direction']}")
    print(f"Confidence: {signal['confidence']}%")
    print(f"Entry: ${signal['entry_price']}")
    print(f"Stop Loss: ${signal['stop_loss']}")
    print(f"Take Profit 1: ${signal['take_profit_1']}")
    print(f"Take Profit 2: ${signal['take_profit_2']}")
    print(f"Risk-Reward: {signal['risk_reward_ratio']}")
    print(f"Quality: {signal['signal_quality']}")
    print(f"Warnings: {signal.get('crypto_warnings', [])}")
    print(f"Summary: {signal['analysis_summary']}")
