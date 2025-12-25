"""
Enhanced BTC Scalping Analyzer with Real-Time Data
Upgraded version with live Binance data integration
"""

import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our new data fetcher
from data_fetcher import BinanceDataFetcher
from correlation_analyzer import CorrelationAdjustedSignal
from risk_manager import EnhancedRiskManager
import config

class BTCScalpingAnalyzerV2:
    def __init__(self, capital=500, risk_per_trade=0.01, max_leverage=100):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.max_leverage = max_leverage

        # Initialize data fetcher
        self.data_fetcher = BinanceDataFetcher(symbol=config.SYMBOL)

        # Market correlation matrix (historical averages)
        self.correlation_matrix = np.array([
            [1.0, -0.65, 0.45, 0.35],  # BTC
            [-0.65, 1.0, -0.3, 0.8],   # USD Index
            [0.45, -0.3, 1.0, 0.2],    # Gold
            [0.35, 0.8, 0.2, 1.0]      # Oil
        ])

        # Adaptive regime detection parameters
        self.regime_history = []
        self.regime_window = 50  # Look back period for regime analysis
        self.adaptive_params = {
            'trend_strength_threshold': 0.001,
            'volatility_threshold': 0.03,
            'volume_multiplier': 1.2,
            'signal_weight_bull': [0.3, 0.4, 0.3],
            'signal_weight_bear': [0.4, 0.3, 0.3],
            'signal_weight_neutral': [0.2, 0.5, 0.3]
        }
        
    def get_market_data(self):
        """Fetch REAL-TIME market data from Binance"""
        market_data = self.data_fetcher.get_market_data()
        
        if market_data is None:
            print("⚠️  Failed to fetch real-time data, using fallback values")
            # Fallback to safe defaults
            return {
                'btc_price': 85000.0,
                'btc_volatility': 0.04,
                'market_sentiment': 0.5,
                'volume_ratio': 1.0,
                'usd_index': 103.2,  # Still using static value (no free API)
                'gold_price': 2045.0,  # Still using static value
                'oil_price': 73.5  # Still using static value
            }
        
        # Add static values for assets without free APIs
        market_data['usd_index'] = 103.2  # Would need paid API
        market_data['gold_price'] = 2045.0  # Would need paid API
        market_data['oil_price'] = 73.5  # Would need paid API
        
        return market_data

    def detect_market_regime(self, market_data):
        """Detect current market regime and return adaptive parameters"""
        try:
            # Get historical data for regime analysis
            historical_data = self.data_fetcher.get_historical_data(limit=self.regime_window + 20)
            if historical_data is None or len(historical_data) < self.regime_window:
                return self._get_default_regime_params()

            prices = np.array([float(k) for k in historical_data['close']])
            volumes = np.array([float(v) for v in historical_data['volume']])

            # Calculate trend strength
            returns = np.diff(prices) / prices[:-1]
            trend_strength = abs(np.mean(returns[-20:]))  # Last 20 periods

            # Calculate volatility
            volatility = np.std(returns[-20:])

            # Calculate volume trend
            volume_ma_short = np.mean(volumes[-10:])
            volume_ma_long = np.mean(volumes[-30:])
            volume_trend = volume_ma_short / volume_ma_long if volume_ma_long > 0 else 1.0

            # Determine regime
            if trend_strength > self.adaptive_params['trend_strength_threshold'] * 1.5:
                if np.mean(returns[-10:]) > 0:
                    regime = 'STRONG_BULL'
                    params = {
                        'signal_weights': [0.2, 0.3, 0.5],  # Favor MC simulation in strong trends
                        'confidence_multiplier': 1.2,
                        'stop_distance_multiplier': 1.5,  # Wider stops in trends
                        'entry_buffer': 10  # Tighter entries
                    }
                else:
                    regime = 'STRONG_BEAR'
                    params = {
                        'signal_weights': [0.2, 0.3, 0.5],
                        'confidence_multiplier': 1.2,
                        'stop_distance_multiplier': 1.5,
                        'entry_buffer': 10
                    }
            elif volatility > self.adaptive_params['volatility_threshold'] * 1.3:
                regime = 'HIGH_VOLATILITY'
                params = {
                    'signal_weights': [0.4, 0.4, 0.2],  # Favor probabilistic in high vol
                    'confidence_multiplier': 0.8,  # More cautious
                    'stop_distance_multiplier': 2.0,  # Much wider stops
                    'entry_buffer': 25  # Looser entries
                }
            elif volume_trend > 1.5:
                regime = 'HIGH_VOLUME'
                params = {
                    'signal_weights': [0.3, 0.4, 0.3],
                    'confidence_multiplier': 1.1,
                    'stop_distance_multiplier': 1.2,
                    'entry_buffer': 15
                }
            elif trend_strength < self.adaptive_params['trend_strength_threshold'] * 0.5:
                regime = 'RANGING'
                params = {
                    'signal_weights': [0.5, 0.3, 0.2],  # Favor algebraic in ranges
                    'confidence_multiplier': 0.9,  # More conservative
                    'stop_distance_multiplier': 0.8,  # Tighter stops
                    'entry_buffer': 20
                }
            else:
                regime = 'NORMAL_TREND'
                params = self._get_default_regime_params()

            # Store regime for tracking
            regime_info = {
                'regime': regime,
                'trend_strength': trend_strength,
                'volatility': volatility,
                'volume_trend': volume_trend,
                'timestamp': datetime.now()
            }
            self.regime_history.append(regime_info)

            # Keep only recent history
            if len(self.regime_history) > 10:
                self.regime_history = self.regime_history[-10:]

            return params

        except Exception as e:
            print(f"Regime detection error: {e}")
            return self._get_default_regime_params()

    def _get_default_regime_params(self):
        """Get default regime parameters"""
        return {
            'signal_weights': [0.3, 0.4, 0.3],  # Default: algebraic, probabilistic, MC
            'confidence_multiplier': 1.0,
            'stop_distance_multiplier': 1.0,
            'entry_buffer': 5
        }

    def algebraic_price_model(self, market_data):
        """Linear and nonlinear price relationships"""
        btc_price = market_data['btc_price']
        usd_index = market_data.get('usd_index', 103.2)
        sentiment = market_data['market_sentiment']
        volatility = market_data['btc_volatility']
        
        # Dynamic alpha based on current price level
        # Adjust coefficients based on price range
        if btc_price > 90000:
            alpha = 100000
        elif btc_price > 80000:
            alpha = 95000
        elif btc_price > 70000:
            alpha = 85000
        else:
            alpha = 75000
        
        beta = 210     # USD inverse relationship
        gamma = 15000  # Sentiment multiplier
        
        predicted_price = alpha - beta * usd_index + gamma * sentiment
        
        # Nonlinear volatility adjustment
        vol_factor = 1 + np.tanh(volatility - 0.03) * 0.1
        adjusted_price = predicted_price * vol_factor
        
        price_deviation = (adjusted_price - btc_price) / btc_price
        
        return {
            'predicted_price': adjusted_price,
            'current_price': btc_price,
            'deviation': price_deviation,
            'signal_strength': abs(price_deviation)
        }
    
    def probabilistic_analysis(self, market_data):
        """Probability-based trading signals"""
        btc_price = market_data['btc_price']
        volatility = market_data['btc_volatility']
        sentiment = market_data['market_sentiment']
        
        # Normal distribution for price movements
        mu = 0.001 * sentiment - 0.0005  # Drift based on sentiment
        sigma = volatility / np.sqrt(24)  # Hourly volatility
        
        # Probability calculations
        prob_up = 1 - stats.norm.cdf(0, mu, sigma)
        prob_down = stats.norm.cdf(0, mu, sigma)
        
        # Conditional probabilities
        usd_change = (market_data.get('usd_index', 103.2) - 103.0) / 103.0
        prob_btc_up_given_usd_down = 0.72 if usd_change < 0 else 0.45
        
        # Markov chain states
        if sentiment > 0.7:
            current_state = "Bullish"
            transition_probs = {'Bull': 0.7, 'Neutral': 0.25, 'Bear': 0.05}
        elif sentiment < 0.3:
            current_state = "Bearish"
            transition_probs = {'Bull': 0.1, 'Neutral': 0.3, 'Bear': 0.6}
        else:
            current_state = "Neutral"
            transition_probs = {'Bull': 0.4, 'Neutral': 0.4, 'Bear': 0.2}
        
        return {
            'prob_up': prob_up,
            'prob_down': prob_down,
            'conditional_prob': prob_btc_up_given_usd_down,
            'current_state': current_state,
            'transition_probs': transition_probs,
            'expected_return': mu,
            'volatility': sigma
        }
    
    def monte_carlo_simulation(self, market_data, n_simulations=1000, hours=4):
        """Monte Carlo price path simulation"""
        current_price = market_data['btc_price']
        volatility = market_data['btc_volatility']
        sentiment = market_data['market_sentiment']
        
        dt = 1/24  # Hourly steps
        mu = 0.001 * sentiment - 0.0005  # Drift
        sigma = volatility
        
        # Generate price paths
        price_paths = []
        for _ in range(n_simulations):
            prices = [current_price]
            for _ in range(hours):
                random_shock = np.random.normal(0, 1)
                price_change = mu * dt + sigma * np.sqrt(dt) * random_shock
                new_price = prices[-1] * (1 + price_change)
                prices.append(new_price)
            price_paths.append(prices)
        
        price_paths = np.array(price_paths)
        final_prices = price_paths[:, -1]
        
        # Statistical analysis
        percentiles = np.percentile(final_prices, [5, 25, 50, 75, 95])
        
        return {
            'final_prices': final_prices,
            'percentiles': {
                'p5': percentiles[0],
                'p25': percentiles[1],
                'median': percentiles[2],
                'p75': percentiles[3],
                'p95': percentiles[4]
            },
            'expected_price': np.mean(final_prices),
            'price_std': np.std(final_prices)
        }
    
    def risk_management(self, market_data, signal_strength):
        """Calculate position size, SL, and TP"""
        current_price = market_data['btc_price']
        volatility = market_data['btc_volatility']
        
        # Position sizing based on Kelly Criterion
        win_rate = 0.55 + signal_strength * 0.15
        avg_win_loss_ratio = 1.2
        
        kelly_fraction = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Risk amount per trade
        risk_amount = self.capital * self.risk_per_trade
        
        # Volatility-based stop loss (ATR approach)
        atr_multiplier = 1.5
        stop_distance = current_price * volatility * atr_multiplier / np.sqrt(365)
        
        # Calculate lot size based on risk
        lot_size = risk_amount / stop_distance
        
        # Position value and leverage
        position_value = lot_size * current_price
        effective_leverage = min(position_value / self.capital, self.max_leverage)
        
        return {
            'lot_size': round(lot_size, 3),
            'effective_leverage': effective_leverage,
            'stop_distance': stop_distance,
            'risk_amount': risk_amount,
            'kelly_fraction': kelly_fraction
        }

    def enhanced_risk_management(self, market_data, signal_strength, regime_params, risk_manager):
        """Enhanced risk management with adaptive sizing"""
        try:
            current_price = market_data['btc_price']

            # Use enhanced risk manager for position sizing
            # Estimate confidence for risk calculation
            confidence = 70 + signal_strength * 20  # Rough confidence estimate

            # Get market regime for risk adjustment
            regime = regime_params.get('detected_regime', 'NORMAL_TREND') if isinstance(regime_params, dict) else 'NORMAL_TREND'

            # Calculate adaptive position size
            risk_calculation = risk_manager.calculate_adaptive_position_size(
                balance=self.capital,
                entry_price=current_price,
                stop_loss=current_price * 0.98,  # Estimate SL for calculation
                market_data=market_data,
                signal_confidence=confidence,
                market_regime=regime
            )

            if 'error' in risk_calculation:
                # Fallback to original calculation
                return self.risk_management(market_data, signal_strength)

            # Calculate dynamic stop loss
            direction = 'BUY'  # Assume for calculation
            dynamic_sl = risk_manager.calculate_dynamic_stop_loss(
                entry_price=current_price,
                direction=direction,
                market_data=market_data,
                signal_strength=signal_strength
            )

            return {
                'lot_size': risk_calculation.get('lots', 0.001),
                'effective_leverage': min(risk_calculation.get('lots', 0.001) * current_price / self.capital, self.max_leverage),
                'stop_distance': dynamic_sl.get('stop_distance', current_price * 0.02),
                'risk_amount': risk_calculation.get('risk_amount', self.capital * 0.01),
                'kelly_fraction': risk_calculation.get('risk_pct', 1.0) / 100.0,
                'risk_calculation': risk_calculation,  # Store full calculation for reference
                'dynamic_stop_loss': dynamic_sl
            }

        except Exception as e:
            print(f"Enhanced risk management error: {e}")
            # Fallback to original calculation
            return self.risk_management(market_data, signal_strength)
    
    def generate_trading_signal(self):
        """Main function to generate complete trading analysis"""
        # Fetch REAL-TIME market data
        market_data = self.get_market_data()

        # 0. Detect Market Regime and get adaptive parameters
        regime_params = self.detect_market_regime(market_data)

        # 1. Algebraic Analysis
        price_model = self.algebraic_price_model(market_data)

        # 2. Probabilistic Analysis
        prob_analysis = self.probabilistic_analysis(market_data)

        # 3. Monte Carlo Simulation
        mc_results = self.monte_carlo_simulation(market_data)

        # 4. Enhanced Risk Management with market regime
        risk_manager = EnhancedRiskManager()
        risk_mgmt = self.enhanced_risk_management(
            market_data, price_model['signal_strength'], regime_params, risk_manager
        )

        # 5. Generate initial signal
        signal = self._create_base_signal(
            market_data, price_model, prob_analysis, mc_results,
            risk_mgmt, regime_params
        )

        # 6. Apply correlation-based adjustments
        correlation_adjuster = CorrelationAdjustedSignal()
        adjusted_signal = correlation_adjuster.adjust_signal(signal)
        
        # 7. Return adjusted signal
        return adjusted_signal

    def _create_base_signal(self, market_data, price_model, prob_analysis, mc_results, risk_mgmt, regime_params):
        """Create the base signal before correlation adjustments"""
        # Generate Trading Decision with Adaptive Weights
        current_price = market_data['btc_price']

        # Signal generation logic
        algebraic_signal = 1 if price_model['deviation'] > 0 else -1
        probabilistic_signal = 1 if prob_analysis['prob_up'] > 0.55 else -1
        mc_signal = 1 if mc_results['expected_price'] > current_price else -1

        # Adaptive weighted signal combination based on market regime
        weights = regime_params['signal_weights']
        signal_weight = (algebraic_signal * weights[0] +
                        probabilistic_signal * weights[1] +
                        mc_signal * weights[2])

        # Adaptive Entry decision based on regime
        entry_buffer = regime_params['entry_buffer']

        if signal_weight > 0.3:
            direction = "BUY"
            entry_price = current_price + entry_buffer
            stop_distance = risk_mgmt['stop_distance'] * regime_params['stop_distance_multiplier']
            stop_loss = entry_price - stop_distance
            take_profit_1 = entry_price + stop_distance * 1.2
            take_profit_2 = entry_price + stop_distance * 2.5
        elif signal_weight < -0.3:
            direction = "SELL"
            entry_price = current_price - entry_buffer
            stop_distance = risk_mgmt['stop_distance'] * regime_params['stop_distance_multiplier']
            stop_loss = entry_price + stop_distance
            take_profit_1 = entry_price - stop_distance * 1.2
            take_profit_2 = entry_price - stop_distance * 2.5
        else:
            direction = "HOLD"
            entry_price = current_price
            stop_loss = None
            take_profit_1 = None
            take_profit_2 = None

        # Adaptive confidence calculation
        base_confidence = 50 + abs(signal_weight) * 30 + price_model['signal_strength'] * 20
        confidence = min(95, base_confidence * regime_params['confidence_multiplier'])

        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'direction': direction,
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2) if stop_loss else None,
            'take_profit_1': round(take_profit_1, 2) if take_profit_1 else None,
            'take_profit_2': round(take_profit_2, 2) if take_profit_2 else None,
            'confidence': round(confidence, 1),
            'lot_size': risk_mgmt['lot_size'],
            'effective_leverage': round(risk_mgmt['effective_leverage'], 2),
            'risk_amount': round(risk_mgmt['risk_amount'], 2),
            'market_analysis': {
                'current_price': current_price,
                'volatility': round(market_data['btc_volatility'] * 100, 2),
                'market_state': prob_analysis['current_state'],
                'signal_strength': round(price_model['signal_strength'] * 100, 2),
                'volume_ratio': round(market_data.get('volume_ratio', 1.0), 2)
            },
            'monte_carlo': {
                'expected_price_4h': round(mc_results['expected_price'], 2),
                'price_range_95': f"{round(mc_results['percentiles']['p5'], 2)} - {round(mc_results['percentiles']['p95'], 2)}"
            },
            'market_regime': {
                'detected_regime': self.regime_history[-1]['regime'] if self.regime_history else 'NORMAL_TREND',
                'adaptive_weights': regime_params['signal_weights'],
                'confidence_multiplier': regime_params['confidence_multiplier'],
                'regime_history': [r['regime'] for r in self.regime_history[-3:]]  # Last 3 regimes
            }
        }

# Run the analyzer with REAL-TIME data
if __name__ == "__main__":
    print("🚀 Starting BTC Scalping Analyzer V2 with REAL-TIME DATA")
    print("=" * 70)
    
    analyzer = BTCScalpingAnalyzerV2(
        capital=config.CAPITAL,
        risk_per_trade=config.RISK_PER_TRADE
    )
    
    trading_signal = analyzer.generate_trading_signal()
    
    # Display results
    print("=" * 70)
    print("BTCUSD CFD SCALPING ANALYSIS (LIVE DATA)")
    print("=" * 70)
    print(f"Timestamp: {trading_signal['timestamp']}")
    print(f"Direction: {trading_signal['direction']}")
    print(f"Entry Price: ${trading_signal['entry_price']:,.2f}")
    
    if trading_signal['stop_loss']:
        print(f"Stop Loss: ${trading_signal['stop_loss']:,.2f}")
        print(f"Take Profit 1 (50%): ${trading_signal['take_profit_1']:,.2f}")
        print(f"Take Profit 2 (50%): ${trading_signal['take_profit_2']:,.2f}")
    else:
        print("Stop Loss: N/A")
        print("Take Profit: N/A")
    
    print(f"Confidence Level: {trading_signal['confidence']}%")
    print()
    print("POSITION DETAILS:")
    print(f"Lot Size: {trading_signal['lot_size']}")
    print(f"Capital: ${analyzer.capital}")
    print(f"Effective Leverage: {trading_signal['effective_leverage']}:1")
    print(f"Risk Amount: ${trading_signal['risk_amount']}")
    print()
    print("MARKET ANALYSIS (REAL-TIME):")
    print(f"Current BTC Price: ${trading_signal['market_analysis']['current_price']:,.2f}")
    print(f"Volatility: {trading_signal['market_analysis']['volatility']}%")
    print(f"Market State: {trading_signal['market_analysis']['market_state']}")
    print(f"Signal Strength: {trading_signal['market_analysis']['signal_strength']}%")
    print(f"Volume Ratio: {trading_signal['market_analysis']['volume_ratio']}")
    print()
    print("MONTE CARLO FORECAST (4 hours):")
    print(f"Expected Price: ${trading_signal['monte_carlo']['expected_price_4h']:,.2f}")
    print(f"95% Price Range: ${trading_signal['monte_carlo']['price_range_95']}")
    
    if trading_signal['direction'] != 'HOLD':
        entry = trading_signal['entry_price']
        sl = trading_signal['stop_loss']
        tp1 = trading_signal['take_profit_1']
        tp2 = trading_signal['take_profit_2']
        
        risk = abs(entry - sl)
        reward1 = abs(tp1 - entry)
        reward2 = abs(tp2 - entry)
        
        print()
        print("RISK-REWARD ANALYSIS:")
        print(f"Risk per unit: ${risk:.2f}")
        print(f"Reward TP1: ${reward1:.2f} (RR 1:{reward1/risk:.2f})")
        print(f"Reward TP2: ${reward2:.2f} (RR 1:{reward2/risk:.2f})")
        
        lot_size = trading_signal['lot_size']
        potential_loss = lot_size * risk
        potential_profit_tp1 = lot_size * reward1
        potential_profit_tp2 = lot_size * reward2
        
        print(f"Potential Loss: ${potential_loss:.2f}")
        print(f"Profit at TP1 (50%): ${potential_profit_tp1/2:.2f}")
        print(f"Profit at TP2 (50%): ${potential_profit_tp2/2:.2f}")
        print(f"Total Potential: ${(potential_profit_tp1/2 + potential_profit_tp2/2):.2f}")
    
    print("\n" + "=" * 70)
    print("✅ Analysis complete with LIVE market data!")
    print("=" * 70)
