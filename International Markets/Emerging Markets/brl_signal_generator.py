"""
Brazilian Real (BRL) Signal Generator
Provides professional trading signals for USD/BRL currency pair
Emerging market currency with higher volatility and carry trade opportunities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

class BRLSignalGenerator:
    """Generate trading signals for USD/BRL (US Dollar vs Brazilian Real)"""

    def __init__(self, data_fetcher=None):
        self.symbol = "USDBRL"
        self.name = "USD/BRL"
        self.description = "US Dollar vs Brazilian Real (Emerging Market)"
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)

        # Risk parameters for emerging market currency (higher volatility)
        self.risk_params = {
            'stop_loss_pips': 250,  # Higher volatility than major pairs
            'take_profit_1_pips': 500,
            'take_profit_2_pips': 1000,
            'max_spread': 50,  # Emerging market spreads can be wider
            'min_volume': 50000,
            'max_volume': 5000000,
            'volatility_multiplier': 1.5  # Account for higher volatility
        }

        # Timeframes to analyze
        self.timeframes = ['M15', 'H1', 'H4', 'D1']

        # Economic indicators specific to Brazil
        self.economic_factors = {
            'interest_rate_differential': 0.08,  # Brazil often has higher rates
            'inflation_expectations': 'moderate',
            'commodity_exposure': 'high',  # Brazil is commodity exporter
            'political_risk': 'medium'
        }

    def generate_signal(self) -> Dict:
        """Generate comprehensive trading signal for USD/BRL"""
        try:
            # Fetch market data for all timeframes
            market_data = self._fetch_market_data()

            if not market_data:
                return self._empty_signal("Unable to fetch market data")

            # Perform technical analysis
            technical_analysis = self._perform_technical_analysis(market_data)

            # Calculate signal strength and confidence
            signal_data = self._calculate_signal_strength(technical_analysis)

            # Apply emerging market adjustments
            adjusted_signal = self._apply_emerging_market_adjustments(signal_data, technical_analysis)

            # Generate final signal
            signal = self._generate_final_signal(adjusted_signal, technical_analysis)

            return signal

        except Exception as e:
            self.logger.error(f"Error generating BRL signal: {str(e)}")
            return self._empty_signal(f"Signal generation error: {str(e)}")

    def _fetch_market_data(self) -> Dict:
        """Fetch market data for USD/BRL across all timeframes"""
        market_data = {}

        for timeframe in self.timeframes:
            try:
                # Use data fetcher or fallback to sample data for demo
                if self.data_fetcher:
                    data = self.data_fetcher.fetch_forex_data("USDBRL", timeframe, limit=200)
                else:
                    data = self._get_sample_data(timeframe)

                if data is not None and len(data) > 0:
                    market_data[timeframe] = data

            except Exception as e:
                self.logger.warning(f"Failed to fetch {timeframe} data: {str(e)}")

        return market_data

    def _get_sample_data(self, timeframe: str) -> pd.DataFrame:
        """Generate sample data for demonstration (replace with real data)"""
        # Generate realistic USD/BRL price data (Brazilian Real is around 5.0-5.5 USD/BRL)
        base_price = 5.25  # Current approximate USD/BRL rate
        periods = 200

        # Generate price series with higher volatility (emerging market)
        np.random.seed(42)  # For reproducible results
        returns = np.random.normal(0, 0.001, periods)  # Higher volatility than CNY
        prices = base_price * np.exp(np.cumsum(returns))

        # Create OHLC data with wider ranges
        highs = prices * (1 + np.random.uniform(0, 0.005, periods))  # Wider ranges
        lows = prices * (1 - np.random.uniform(0, 0.005, periods))
        opens = np.roll(prices, 1)
        opens[0] = base_price

        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=periods, freq='15min' if timeframe == 'M15' else '1H'),
            'open': opens,
            'high': highs,
            'low': lows,
            'close': prices,
            'volume': np.random.randint(5000, 50000, periods)  # Lower volume than major pairs
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
        """Analyze a specific timeframe with emerging market considerations"""
        close_prices = data['close'].values
        high_prices = data['high'].values
        low_prices = data['low'].values

        # Moving averages (adjusted for volatility)
        sma_20 = self._calculate_sma(close_prices, 20)
        sma_50 = self._calculate_sma(close_prices, 50)
        ema_21 = self._calculate_ema(close_prices, 21)

        # RSI with volatility adjustment
        rsi = self._calculate_rsi(close_prices, 14)

        # MACD
        macd_line, signal_line, histogram = self._calculate_macd(close_prices)

        # Bollinger Bands (wider for emerging markets)
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close_prices, std_dev=2.5)

        # Support and Resistance
        support, resistance = self._find_support_resistance(high_prices, low_prices)

        # Trend analysis
        trend = self._determine_trend(sma_20, sma_50, ema_21)

        # Volatility analysis (important for emerging markets)
        volatility = self._calculate_volatility(close_prices)

        # Volume analysis (emerging markets may have lower liquidity)
        volume_analysis = self._analyze_volume(data['volume'].values)

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
            'volatility': volatility,
            'volume_analysis': volume_analysis,
            'current_price': close_prices[-1],
            'previous_price': close_prices[-2] if len(close_prices) > 1 else close_prices[-1]
        }

    def _calculate_volatility(self, prices: np.ndarray, period: int = 20) -> float:
        """Calculate price volatility (important for risk management)"""
        if len(prices) < period:
            return 0.0

        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns[-period:]) * np.sqrt(252)  # Annualized volatility
        return volatility

    def _analyze_volume(self, volumes: np.ndarray) -> Dict:
        """Analyze trading volume patterns"""
        if len(volumes) < 20:
            return {'trend': 'unknown', 'average': 0, 'liquidity': 'unknown'}

        avg_volume = np.mean(volumes[-20:])
        recent_volume = np.mean(volumes[-5:])

        volume_trend = 'increasing' if recent_volume > avg_volume * 1.1 else 'decreasing' if recent_volume < avg_volume * 0.9 else 'stable'

        # Assess liquidity (emerging markets often have lower liquidity)
        liquidity = 'high' if avg_volume > 50000 else 'medium' if avg_volume > 10000 else 'low'

        return {
            'trend': volume_trend,
            'average': avg_volume,
            'liquidity': liquidity
        }

    # [Previous technical indicator methods remain the same]
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

    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2.5):
        """Calculate Bollinger Bands (wider for emerging markets)"""
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

    def _apply_emerging_market_adjustments(self, signal_data: Dict, technical_analysis: Dict) -> Dict:
        """Apply emerging market specific adjustments to signals"""
        adjusted_data = signal_data.copy()

        # Get current analysis
        current_analysis = technical_analysis.get('H1', technical_analysis.get('M15', {}))

        # Adjust confidence based on emerging market factors
        base_confidence = signal_data['confidence']

        # Volume/liquidity adjustment
        volume_analysis = current_analysis.get('volume_analysis', {})
        if volume_analysis.get('liquidity') == 'low':
            base_confidence *= 0.8  # Reduce confidence for low liquidity
            adjusted_data['liquidity_warning'] = True

        # Volatility adjustment
        volatility = current_analysis.get('volatility', 0)
        if volatility > 0.3:  # High volatility
            base_confidence *= 0.9  # Slight reduction for very high volatility
            adjusted_data['high_volatility'] = True

        # Economic factors adjustment
        if self.economic_factors['political_risk'] == 'medium':
            base_confidence *= 0.95  # Small adjustment for political risk

        adjusted_data['confidence'] = min(base_confidence, 95)  # Cap at 95%

        return adjusted_data

    def _calculate_signal_strength(self, technical_analysis: Dict) -> Dict:
        """Calculate overall signal strength and direction with emerging market considerations"""
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0

        # Weight different timeframes (emphasize H1 for emerging markets)
        timeframe_weights = {'M15': 1, 'H1': 3, 'H4': 2, 'D1': 2}

        for timeframe, analysis in technical_analysis.items():
            weight = timeframe_weights.get(timeframe, 1)

            # RSI signals
            if analysis.get('rsi'):
                if analysis['rsi'] < 35:  # Wider range for emerging markets
                    bullish_signals += weight
                elif analysis['rsi'] > 65:
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

            # Bollinger Band signals (wider bands for emerging markets)
            bb = analysis.get('bollinger', {})
            current_price = analysis.get('current_price')
            if current_price and bb.get('lower') and bb.get('upper'):
                bb_range = bb['upper'] - bb['lower']
                if current_price < bb['lower'] + (bb_range * 0.1):  # Near lower band
                    bullish_signals += weight
                elif current_price > bb['upper'] - (bb_range * 0.1):  # Near upper band
                    bearish_signals += weight
                total_signals += weight

            # Trend signals
            trend = analysis.get('trend')
            if trend == 'bullish':
                bullish_signals += weight * 2
            elif trend == 'bearish':
                bearish_signals += weight * 2
            total_signals += weight * 2

        # Calculate confidence with emerging market adjustments
        if total_signals > 0:
            bullish_percentage = bullish_signals / total_signals
            bearish_percentage = bearish_signals / total_signals

            if bullish_percentage > 0.55:  # Lower threshold for emerging markets
                direction = "BUY"
                confidence = min(bullish_percentage * 100, 90)  # Cap lower for EM
            elif bearish_percentage > 0.55:
                direction = "SELL"
                confidence = min(bearish_percentage * 100, 90)
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
            'emerging_market_adjusted': True
        }

    def _generate_final_signal(self, signal_data: Dict, technical_analysis: Dict) -> Dict:
        """Generate the final comprehensive signal for emerging market"""
        direction = signal_data['direction']
        confidence = signal_data['confidence']

        # Get current market data
        current_analysis = technical_analysis.get('M15', {})

        # Entry and exit levels (adjusted for higher volatility)
        current_price = current_analysis.get('current_price', 5.25)
        support = current_analysis.get('support', current_price * 0.95)
        resistance = current_analysis.get('resistance', current_price * 1.05)

        # Wider stops and targets for emerging markets
        pip_value = 0.0001  # BRL pip value

        if direction == "BUY":
            entry_price = current_price
            stop_loss = entry_price - (self.risk_params['stop_loss_pips'] * pip_value)
            take_profit_1 = entry_price + (self.risk_params['take_profit_1_pips'] * pip_value)
            take_profit_2 = entry_price + (self.risk_params['take_profit_2_pips'] * pip_value)
        elif direction == "SELL":
            entry_price = current_price
            stop_loss = entry_price + (self.risk_params['stop_loss_pips'] * pip_value)
            take_profit_1 = entry_price - (self.risk_params['take_profit_1_pips'] * pip_value)
            take_profit_2 = entry_price - (self.risk_params['take_profit_2_pips'] * pip_value)
        else:
            entry_price = current_price
            stop_loss = current_price * 0.92  # Wider stops for EM
            take_profit_1 = current_price * 1.08
            take_profit_2 = current_price * 1.15

        # Calculate risk-reward ratio
        risk = abs(entry_price - stop_loss)
        reward_1 = abs(take_profit_1 - entry_price)
        reward_2 = abs(take_profit_2 - entry_price)
        rr_ratio = reward_1 / risk if risk > 0 else 0

        # Get additional emerging market data
        volume_analysis = current_analysis.get('volume_analysis', {})
        volatility = current_analysis.get('volatility', 0)

        # Generate signal
        signal = {
            'symbol': self.symbol,
            'name': self.name,
            'description': self.description,
            'timestamp': datetime.now().isoformat(),
            'direction': direction,
            'confidence': round(confidence, 1),
            'entry_price': round(entry_price, 4),
            'stop_loss': round(stop_loss, 4),
            'take_profit_1': round(take_profit_1, 4),
            'take_profit_2': round(take_profit_2, 4),
            'risk_reward_ratio': round(rr_ratio, 2),
            'technical_indicators': {
                'rsi': current_analysis.get('rsi'),
                'trend': current_analysis.get('trend'),
                'support': round(support, 4),
                'resistance': round(resistance, 4),
                'volatility': round(volatility, 4),
                'liquidity': volume_analysis.get('liquidity', 'unknown')
            },
            'market_data': {
                'current_price': round(current_price, 4),
                'daily_range': round(resistance - support, 4),
                'volatility': 'High' if volatility > 0.2 else 'Moderate',
                'market_type': 'Emerging Market'
            },
            'trading_hours': '24/5 (Americas session focus)',
            'spread_typical': f"{self.risk_params['max_spread']/10:.1f} pips",
            'recommended_volume': f"{self.risk_params['min_volume']:,} - {self.risk_params['max_volume']:,}",
            'signal_quality': self._assess_signal_quality(confidence, rr_ratio),
            'economic_factors': self.economic_factors,
            'emerging_market_warnings': self._get_em_warnings(signal_data),
            'analysis_summary': self._generate_analysis_summary(signal_data, current_analysis)
        }

        return signal

    def _get_em_warnings(self, signal_data: Dict) -> List[str]:
        """Get emerging market specific warnings"""
        warnings = []

        if signal_data.get('liquidity_warning'):
            warnings.append("Low liquidity may increase slippage")

        if signal_data.get('high_volatility'):
            warnings.append("High volatility - use wider stops")

        if self.economic_factors['political_risk'] == 'medium':
            warnings.append("Monitor political developments in Brazil")

        if self.economic_factors['inflation_expectations'] == 'moderate':
            warnings.append("Inflation data may impact currency direction")

        return warnings

    def _assess_signal_quality(self, confidence: float, rr_ratio: float) -> str:
        """Assess overall signal quality for emerging markets"""
        # Slightly lower thresholds for emerging markets due to higher volatility
        if confidence >= 75 and rr_ratio >= 1.8:
            return "A+ (Excellent for EM)"
        elif confidence >= 65 and rr_ratio >= 1.3:
            return "A (Very Good for EM)"
        elif confidence >= 55 and rr_ratio >= 1.1:
            return "B+ (Good for EM)"
        elif confidence >= 45:
            return "B (Moderate for EM)"
        else:
            return "C (Weak - Consider avoiding)"

    def _generate_analysis_summary(self, signal_data: Dict, analysis: Dict) -> str:
        """Generate human-readable analysis summary for emerging market"""
        direction = signal_data['direction']
        confidence = signal_data['confidence']
        trend = analysis.get('trend', 'unknown')
        rsi = analysis.get('rsi')
        volatility = analysis.get('volatility', 0)

        summary = f"USD/BRL emerging market analysis shows {direction.lower()} signal with {confidence:.1f}% confidence. "

        if trend != 'unknown':
            summary += f"Market trend is {trend}. "

        if rsi:
            if rsi < 35:  # Wider ranges for EM
                summary += "RSI indicates oversold conditions. "
            elif rsi > 65:
                summary += "RSI indicates overbought conditions. "

        if volatility > 0.2:
            summary += "High volatility detected - use appropriate risk management. "

        summary += "BRL is an emerging market currency with commodity exposure and interest rate differentials."

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
            'market_type': 'Emerging Market'
        }

# Example usage
if __name__ == "__main__":
    generator = BRLSignalGenerator()
    signal = generator.generate_signal()

    print("USD/BRL Emerging Market Signal:")
    print(f"Direction: {signal['direction']}")
    print(f"Confidence: {signal['confidence']}%")
    print(f"Entry: {signal['entry_price']}")
    print(f"Stop Loss: {signal['stop_loss']}")
    print(f"Take Profit 1: {signal['take_profit_1']}")
    print(f"Take Profit 2: {signal['take_profit_2']}")
    print(f"Risk-Reward: {signal['risk_reward_ratio']}")
    print(f"Quality: {signal['signal_quality']}")
    print(f"Warnings: {signal.get('emerging_market_warnings', [])}")
    print(f"Summary: {signal['analysis_summary']}")
