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
import config

class GoldScalpingAnalyzer:
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
        
    def get_market_data(self):
        """Fetch REAL-TIME market data from Binance"""
        market_data = self.data_fetcher.get_market_data()
        
        if market_data is None:
            print("WARNING: Failed to fetch real-time data, using fallback values")
            # Fallback to safe defaults
            return {
                'gold_price': 2650.0,
                'gold_volatility': 0.01,
                'market_sentiment': 0.5,
                'volume_ratio': 1.0,
                'usd_index': 103.2,
                'oil_price': 73.5
            }
        
        # Add static values for assets without free APIs
        market_data['usd_index'] = 103.2  # Would need paid API
        # market_data['gold_price'] = 2045.0  # REMOVED: Using real fetched data now
        market_data['oil_price'] = 73.5  # Would need paid API
        
        return market_data
    
    def algebraic_price_model(self, market_data):
        """Linear and nonlinear price relationships"""
        gold_price = market_data['gold_price']
        usd_index = market_data.get('usd_index', 103.2)
        sentiment = market_data['market_sentiment']
        volatility = market_data['gold_volatility']
        
        # Dynamic alpha based on current price level
        # Adjust coefficients based on price range
        if gold_price > 2800:
            alpha = 3000
        elif gold_price > 2700:
            alpha = 2900
        elif gold_price > 2600:
            alpha = 2800
        else:
            alpha = 2700
        
        beta = 15      # USD inverse relationship (adjusted for Gold scale)
        gamma = 400    # Sentiment multiplier (adjusted for Gold scale)
        
        predicted_price = alpha - beta * usd_index + gamma * sentiment
        
        # Nonlinear volatility adjustment
        vol_factor = 1 + np.tanh(volatility - 0.01) * 0.1
        adjusted_price = predicted_price * vol_factor
        
        price_deviation = (adjusted_price - gold_price) / gold_price
        
        return {
            'predicted_price': adjusted_price,
            'current_price': gold_price,
            'deviation': price_deviation,
            'signal_strength': abs(price_deviation)
        }
    
    def probabilistic_analysis(self, market_data):
        """Probability-based trading signals"""
        gold_price = market_data['gold_price']
        volatility = market_data['gold_volatility']
        sentiment = market_data['market_sentiment']
        
        # Normal distribution for price movements
        mu = 0.001 * sentiment - 0.0005  # Drift based on sentiment
        sigma = volatility / np.sqrt(24)  # Hourly volatility
        
        # Probability calculations
        prob_up = 1 - stats.norm.cdf(0, mu, sigma)
        prob_down = stats.norm.cdf(0, mu, sigma)
        
        # Conditional probabilities
        usd_change = (market_data.get('usd_index', 103.2) - 103.0) / 103.0
        prob_gold_up_given_usd_down = 0.72 if usd_change < 0 else 0.45
        
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
            'conditional_prob': prob_gold_up_given_usd_down,
            'current_state': current_state,
            'transition_probs': transition_probs,
            'expected_return': mu,
            'volatility': sigma
        }
    
    def monte_carlo_simulation(self, market_data, n_simulations=1000, hours=4):
        """Monte Carlo price path simulation"""
        current_price = market_data['gold_price']
        volatility = market_data['gold_volatility']
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
        current_price = market_data['gold_price']
        volatility = market_data['gold_volatility']
        
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
    
    def generate_trading_signal(self):
        """Main function to generate complete trading analysis"""
        # Fetch REAL-TIME market data
        market_data = self.get_market_data()
        
        # 1. Algebraic Analysis
        price_model = self.algebraic_price_model(market_data)
        
        # 2. Probabilistic Analysis
        prob_analysis = self.probabilistic_analysis(market_data)
        
        # 3. Monte Carlo Simulation
        mc_results = self.monte_carlo_simulation(market_data)
        
        # 4. Risk Management
        risk_mgmt = self.risk_management(market_data, price_model['signal_strength'])
        
        # 5. Generate Trading Decision
        current_price = market_data['gold_price']
        
        # Signal generation logic
        algebraic_signal = 1 if price_model['deviation'] > 0 else -1
        probabilistic_signal = 1 if prob_analysis['prob_up'] > 0.55 else -1
        mc_signal = 1 if mc_results['expected_price'] > current_price else -1
        
        # Weighted signal combination
        signal_weight = (algebraic_signal * 0.3 + 
                        probabilistic_signal * 0.4 + 
                        mc_signal * 0.3)
        
        # Entry decision
        if signal_weight > 0.3:
            direction = "BUY"
            entry_price = current_price + 0.5
            stop_loss = entry_price - risk_mgmt['stop_distance']
            take_profit_1 = entry_price + risk_mgmt['stop_distance'] * 1.2
            take_profit_2 = entry_price + risk_mgmt['stop_distance'] * 2.5
        elif signal_weight < -0.3:
            direction = "SELL"
            entry_price = current_price - 0.5
            stop_loss = entry_price + risk_mgmt['stop_distance']
            take_profit_1 = entry_price - risk_mgmt['stop_distance'] * 1.2
            take_profit_2 = entry_price - risk_mgmt['stop_distance'] * 2.5
        else:
            direction = "HOLD"
            entry_price = current_price
            stop_loss = None
            take_profit_1 = None
            take_profit_2 = None
        
        # Confidence calculation
        confidence = min(95, 50 + abs(signal_weight) * 30 + price_model['signal_strength'] * 20)
        
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
                'volatility': round(market_data['gold_volatility'] * 100, 2),
                'market_state': prob_analysis['current_state'],
                'signal_strength': round(price_model['signal_strength'] * 100, 2),
                'volume_ratio': round(market_data.get('volume_ratio', 1.0), 2)
            },
            'monte_carlo': {
                'expected_price_4h': round(mc_results['expected_price'], 2),
                'price_range_95': f"{round(mc_results['percentiles']['p5'], 2)} - {round(mc_results['percentiles']['p95'], 2)}"
            }
        }

# Run the analyzer with REAL-TIME data
if __name__ == "__main__":
    print("🚀 Starting Gold Scalping Analyzer with REAL-TIME DATA")
    print("=" * 70)
    
    analyzer = GoldScalpingAnalyzer(
        capital=config.CAPITAL,
        risk_per_trade=config.RISK_PER_TRADE
    )
    
    trading_signal = analyzer.generate_trading_signal()
    
    # Display results
    print("=" * 70)
    print("XAUUSD (GOLD) SCALPING ANALYSIS (LIVE DATA)")
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
    print(f"Current Gold Price: ${trading_signal['market_analysis']['current_price']:,.2f}")
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
