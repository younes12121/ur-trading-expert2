"""
Australian Dollar (AUD) Signal Generator
Provides professional trading signals for AUD/USD currency pair
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

class AUDUSDGenerator:
    """Generate trading signals for AUD/USD (Australian Dollar vs US Dollar)"""

    def __init__(self, data_fetcher=None):
        self.symbol = "AUDUSD"
        self.name = "AUD/USD"
        self.description = "Australian Dollar vs US Dollar"
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)

        # Risk parameters specific to AUD
        self.risk_params = {
            'stop_loss_pips': 55,  # AUD has medium volatility, commodity influenced
            'take_profit_1_pips': 110,
            'take_profit_2_pips': 220,
            'max_spread': 9,  # AUD spreads are reasonable
            'min_volume': 100000,
            'max_volume': 10000000
        }

        # Timeframes to analyze
        self.timeframes = ['M15', 'H1', 'H4', 'D1']

    def generate_signal(self) -> Dict:
        """Generate comprehensive trading signal for AUD/USD"""
        try:
            # Fetch market data for all timeframes
            market_data = self._fetch_market_data()

            if not market_data:
                return self._empty_signal("Unable to fetch market data")

            # Perform technical analysis
            technical_analysis = self._perform_technical_analysis(market_data)

            # Calculate signal strength and confidence
            signal_data = self._calculate_signal_strength(technical_analysis)

            # Generate final signal
            signal = self._generate_final_signal(signal_data, technical_analysis)

            return signal

        except Exception as e:
            self.logger.error(f"Error generating AUD signal: {str(e)}")
            return self._empty_signal(f"Signal generation error: {str(e)}")

    def _fetch_market_data(self) -> Dict:
        """Fetch market data for AUD/USD across all timeframes"""
        market_data = {}

        for timeframe in self.timeframes:
            try:
                # Use data fetcher or fallback to sample data for demo
                if self.data_fetcher:
                    data = self.data_fetcher.fetch_forex_data("AUDUSD", timeframe, limit=200)
                else:
                    data = self._get_sample_data(timeframe)

                if data is not None and len(data) > 0:
                    market_data[timeframe] = data

            except Exception as e:
                self.logger.warning(f"Failed to fetch {timeframe} data: {str(e)}")

        return market_data

    def _get_sample_data(self, timeframe: str) -> pd.DataFrame:
        """Generate sample data for demonstration (replace with real data)"""
        # Generate realistic AUD/USD price data
        base_price = 0.6620  # Current approximate AUD/USD rate
        periods = 200

        # Generate price series with realistic volatility (medium for AUD)
        np.random.seed(46)  # For reproducible results
        returns = np.random.normal(0, 0.0009, periods)  # Medium volatility for AUD
        prices = base_price * np.exp(np.cumsum(returns))

        # Create OHLC data
        highs = prices * (1 + np.random.uniform(0, 0.003, periods))
        lows = prices * (1 - np.random.uniform(0, 0.003, periods))
        opens = np.roll(prices, 1)
        opens[0] = base_price

        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=periods, freq='15min' if timeframe == 'M15' else '1H'),
            'open': opens,
            'high': highs,
            'low': lows,
            'close': prices,
            'volume': np.random.randint(100000, 1000000, periods)
        })

        return data

    def _perform_technical_analysis(self, market_data: Dict) -> Dict:
        """Perform comprehensive technical analysis"""
        analysis = {}

        for timeframe, data in market_data.items():
            try:
                analysis[timeframe] = self._analyze_timeframe(data, timeframe)
            except Exception as e:
                self.logger.warning(f"Analysis failed for {timeframe}: {str(e)}")

        return analysis

    def _analyze_timeframe(self, data: pd.DataFrame, timeframe: str) -> Dict:
        """Analyze a specific timeframe"""
        close_prices = data['close'].values
        high_prices = data['high'].values
        low_prices = data['low'].values

        # Moving averages
        sma_20 = self._calculate_sma(close_prices, 20)
        sma_50 = self._calculate_sma(close_prices, 50)
        ema_21 = self._calculate_ema(close_prices, 21)

        # RSI
        rsi = self._calculate_rsi(close_prices, 14)

        # MACD
        macd_line, signal_line, histogram = self._calculate_macd(close_prices)

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close_prices)

        # Support and Resistance
        support, resistance = self._find_support_resistance(high_prices, low_prices)

        # Trend analysis
        trend = self._determine_trend(sma_20, sma_50, ema_21)

        return {
            'sma_20': sma_20[-1] if len(sma_20) > 0 else None,
            'sma_50': sma_50[-1] if len(sma_50) > 0 else None,
            'ema_21': ema_21[-1] if len(ema_21) > 0 else None,
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
            'current_price': close_prices[-1],
            'previous_price': close_prices[-2] if len(close_prices) > 1 else close_prices[-1]
        }

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

    def _calculate_macd(self, prices: np.ndarray, fast=12, slow=26, signal=9) -> Tuple:
        """Calculate MACD indicator"""
        if len(prices) < slow:
            return np.array([]), np.array([]), np.array([])

        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)

        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2.0):
        """Calculate Bollinger Bands"""
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

    def _determine_trend(self, sma_20: float, sma_50: float, ema_21: float) -> str:
        """Determine market trend"""
        if sma_20 and sma_50 and ema_21:
            if sma_20 > sma_50 and ema_21 > sma_50:
                return "bullish"
            elif sma_20 < sma_50 and ema_21 < sma_50:
                return "bearish"
            else:
                return "sideways"
        return "unknown"

    def _calculate_signal_strength(self, technical_analysis: Dict) -> Dict:
        """Calculate overall signal strength and direction"""
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0

        # Weight different timeframes
        timeframe_weights = {'M15': 1, 'H1': 2, 'H4': 3, 'D1': 4}

        for timeframe, analysis in technical_analysis.items():
            weight = timeframe_weights.get(timeframe, 1)

            # RSI signals
            if analysis.get('rsi'):
                if analysis['rsi'] < 30:
                    bullish_signals += weight
                elif analysis['rsi'] > 70:
                    bearish_signals += weight
                total_signals += weight

            # MACD signals
            macd = analysis.get('macd', {})
            if macd.get('histogram'):
                if macd['histogram'] > 0:
                    bullish_signals += weight
                else:
                    bearish_signals += weight
                total_signals += weight

            # Bollinger Band signals
            bb = analysis.get('bollinger', {})
            current_price = analysis.get('current_price')
            if current_price and bb.get('lower') and bb.get('upper'):
                if current_price < bb['lower']:
                    bullish_signals += weight
                elif current_price > bb['upper']:
                    bearish_signals += weight
                total_signals += weight

            # Trend signals
            trend = analysis.get('trend')
            if trend == 'bullish':
                bullish_signals += weight * 2  # Trend is important
            elif trend == 'bearish':
                bearish_signals += weight * 2
            total_signals += weight * 2

        # Calculate confidence
        if total_signals > 0:
            bullish_percentage = bullish_signals / total_signals
            bearish_percentage = bearish_signals / total_signals

            if bullish_percentage > 0.6:
                direction = "BUY"
                confidence = min(bullish_percentage * 100, 95)
            elif bearish_percentage > 0.6:
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
            'total_signals': total_signals
        }

    def _generate_final_signal(self, signal_data: Dict, technical_analysis: Dict) -> Dict:
        """Generate the final comprehensive signal"""
        direction = signal_data['direction']
        confidence = signal_data['confidence']

        # Get current market data
        current_analysis = technical_analysis.get('M15', {})

        # Entry and exit levels
        current_price = current_analysis.get('current_price', 0.6620)
        support = current_analysis.get('support', current_price * 0.995)
        resistance = current_analysis.get('resistance', current_price * 1.005)

        if direction == "BUY":
            entry_price = current_price
            stop_loss = entry_price - (self.risk_params['stop_loss_pips'] / 10000)  # AUD pip value
            take_profit_1 = entry_price + (self.risk_params['take_profit_1_pips'] / 10000)
            take_profit_2 = entry_price + (self.risk_params['take_profit_2_pips'] / 10000)
        elif direction == "SELL":
            entry_price = current_price
            stop_loss = entry_price + (self.risk_params['stop_loss_pips'] / 10000)
            take_profit_1 = entry_price - (self.risk_params['take_profit_1_pips'] / 10000)
            take_profit_2 = entry_price - (self.risk_params['take_profit_2_pips'] / 10000)
        else:
            entry_price = current_price
            stop_loss = current_price * 0.98
            take_profit_1 = current_price * 1.02
            take_profit_2 = current_price * 1.04

        # Calculate risk-reward ratio
        risk = abs(entry_price - stop_loss)
        reward_1 = abs(take_profit_1 - entry_price)
        reward_2 = abs(take_profit_2 - entry_price)
        rr_ratio = reward_1 / risk if risk > 0 else 0

        # Generate signal
        signal = {
            'symbol': self.symbol,
            'name': self.name,
            'description': self.description,
            'timestamp': datetime.now().isoformat(),
            'direction': direction,
            'confidence': round(confidence, 1),
            'entry_price': round(entry_price, 5),
            'stop_loss': round(stop_loss, 5),
            'take_profit_1': round(take_profit_1, 5),
            'take_profit_2': round(take_profit_2, 5),
            'risk_reward_ratio': round(rr_ratio, 2),
            'technical_indicators': {
                'rsi': current_analysis.get('rsi'),
                'trend': current_analysis.get('trend'),
                'support': round(support, 5),
                'resistance': round(resistance, 5)
            },
            'market_data': {
                'current_price': round(current_price, 5),
                'daily_range': round(resistance - support, 5),
                'volatility': 'Medium'  # AUD has medium volatility
            },
            'trading_hours': '24/5 (Asian/Pacific session dominant)',
            'spread_typical': f"{self.risk_params['max_spread']/10:.1f} pips",
            'recommended_volume': f"{self.risk_params['min_volume']:,} - {self.risk_params['max_volume']:,}",
            'signal_quality': self._assess_signal_quality(confidence, rr_ratio),
            'analysis_summary': self._generate_analysis_summary(signal_data, current_analysis)
        }

        return signal

    def _assess_signal_quality(self, confidence: float, rr_ratio: float) -> str:
        """Assess overall signal quality"""
        if confidence >= 80 and rr_ratio >= 2.0:
            return "A+ (Excellent)"
        elif confidence >= 70 and rr_ratio >= 1.5:
            return "A (Very Good)"
        elif confidence >= 60 and rr_ratio >= 1.2:
            return "B+ (Good)"
        elif confidence >= 50:
            return "B (Moderate)"
        else:
            return "C (Weak)"

    def _generate_analysis_summary(self, signal_data: Dict, analysis: Dict) -> str:
        """Generate human-readable analysis summary"""
        direction = signal_data['direction']
        confidence = signal_data['confidence']
        trend = analysis.get('trend', 'unknown')
        rsi = analysis.get('rsi')

        summary = f"AUD/USD analysis shows {direction.lower()} signal with {confidence:.1f}% confidence. "

        if trend != 'unknown':
            summary += f"Market trend is {trend}. "

        if rsi:
            if rsi < 30:
                summary += "RSI indicates oversold conditions. "
            elif rsi > 70:
                summary += "RSI indicates overbought conditions. "
            else:
                summary += "RSI is neutral. "

        summary += "AUD is heavily influenced by commodity prices, RBA policy, and Chinese economic data."

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
            'signal_quality': 'N/A'
        }

# Example usage
if __name__ == "__main__":
    generator = AUDUSDGenerator()
    signal = generator.generate_signal()

    print("AUD/USD Signal:")
    print(f"Direction: {signal['direction']}")
    print(f"Confidence: {signal['confidence']}%")
    print(f"Entry: {signal['entry_price']}")
    print(f"Stop Loss: {signal['stop_loss']}")
    print(f"Take Profit 1: {signal['take_profit_1']}")
    print(f"Take Profit 2: {signal['take_profit_2']}")
    print(f"Risk-Reward: {signal['risk_reward_ratio']}")
    print(f"Quality: {signal['signal_quality']}")
    print(f"Summary: {signal['analysis_summary']}")
