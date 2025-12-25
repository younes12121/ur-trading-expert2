"""
ENHANCED GOLD Signal Generator with Improved 20-Criteria System
Professional XAUUSD analysis with proper validation for all criteria
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import time
import logging
from enhanced_criteria_system import Enhanced20CriteriaSystem
from global_error_learning import global_error_manager, record_error

logger = logging.getLogger(__name__)

class EnhancedGoldSignalGenerator:
    """
    Enhanced Gold (XAUUSD) signal generator using the improved 20-criteria system
    """
    
    def __init__(self):
        self.symbol = "GC=F"  # Gold Futures
        self.symbol_alt = "GOLD"  # Alternative symbol
        self.timeframes = {
            'M15': '15m',
            'H1': '1h', 
            'H4': '4h',
            'D1': '1d'
        }
        self.enhanced_criteria = Enhanced20CriteriaSystem()
        
    def fetch_live_data(self):
        """Fetch live Gold data from Yahoo Finance"""
        try:
            data = {}
            ticker = yf.Ticker(self.symbol)
            
            for tf_name, tf_period in self.timeframes.items():
                # Get appropriate period for each timeframe
                if tf_name == 'M15':
                    period = "5d"  # Last 5 days of 15min data
                elif tf_name == 'H1':
                    period = "30d"  # Last 30 days of hourly data
                elif tf_name == 'H4':
                    period = "90d"  # Last 90 days of 4h data  
                else:  # D1
                    period = "1y"   # Last year of daily data
                    
                df = ticker.history(period=period, interval=tf_period)
                
                if df.empty:
                    print(f"Warning: No Gold data for {tf_name}, trying alternative...")
                    # Try alternative symbols or generate fallback
                    continue
                    
                # Convert column names to lowercase
                df.columns = [col.lower() for col in df.columns]
                data[tf_name] = df
                
            # If no data fetched, use fallback
            if not data:
                return self.generate_fallback_data()
                
            return data
            
        except Exception as e:
            print(f"Error fetching Gold data: {e}")
            return self.generate_fallback_data()
    
    def generate_fallback_data(self):
        """Generate simulated Gold data for testing"""
        np.random.seed(42)
        base_price = 1950.0  # Gold base price
        
        data = {}
        for tf in ['M15', 'H1', 'H4', 'D1']:
            if tf == 'M15':
                periods = 480  # 5 days of 15min candles
                freq = '15T'
            elif tf == 'H1':
                periods = 720  # 30 days of hourly candles  
                freq = '1H'
            elif tf == 'H4':
                periods = 540  # 90 days of 4h candles
                freq = '4H'
            else:  # D1
                periods = 365  # 1 year of daily candles
                freq = '1D'
                
            dates = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
            
            # Generate realistic Gold price movements
            returns = np.random.normal(0, 0.015, periods)  # Gold volatility ~1.5%
            prices = [base_price]
            for r in returns[1:]:
                new_price = prices[-1] * (1 + r)
                # Keep Gold in realistic range (1800-2200)
                new_price = max(1800, min(2200, new_price))
                prices.append(new_price)
            
            df = pd.DataFrame({
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.008))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.008))) for p in prices],
                'close': prices,
                'volume': np.random.randint(10000, 50000, periods)
            }, index=dates)
            
            # Ensure high >= low >= close relationships
            for i in range(len(df)):
                df.iloc[i]['high'] = max(df.iloc[i]['open'], df.iloc[i]['close'], df.iloc[i]['high'])
                df.iloc[i]['low'] = min(df.iloc[i]['open'], df.iloc[i]['close'], df.iloc[i]['low'])
            
            data[tf] = df
            
        print("Using simulated Gold data for analysis...")
        return data
    
    def generate_signal(self):
        """Generate Gold signal using enhanced 20-criteria system with error learning"""
        start_time = time.time()

        operation_context = {
            'generator_type': 'enhanced_gold',
            'asset_symbol': 'XAU',
            'timeframe': 'multi_timeframe',
            'market_condition': 'live_data',
            'data_quality': 0.9,
            'computation_load': 0.7,
            'cache_status': 0,  # Live data, no cache
            'system_load': 0.5,
            'memory_usage': 0.5
        }

        # Predict error likelihood
        error_prediction = global_error_manager.predict_error_likelihood('signal_generator', operation_context)

        if not error_prediction['should_attempt']:
            logger.warning(f"[GOLD_SIGNAL_GENERATOR] Avoiding signal generation due to high error risk: {error_prediction['error_probability']:.1%}")
            print(f"⚠️ Gold signal generation cancelled due to high error risk prediction")
            print(f"   Alternative suggestions: {error_prediction['alternative_suggestions']}")

            record_error('signal_generator', operation_context, had_error=False,
                        error_details="Proactively avoided due to error prediction",
                        success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']},
                        execution_time=time.time() - start_time)

            return None

        success = False
        error_details = None

        try:
            print("🥇 Fetching live Gold (XAUUSD) data...")
            data = self.fetch_live_data()
            
            if not data:
                print("❌ Failed to fetch Gold data")
                return None
            
            print("🧮 Applying enhanced 20-criteria Gold analysis...")
            is_elite, analysis = self.enhanced_criteria.apply_enhanced_criteria(data, "GOLD")
            
            if is_elite:
                # Generate detailed Gold signal
                current_price = data['M15']['close'].iloc[-1]
                h1_data = data['H1'].iloc[-1]
                
                # Determine direction from trend analysis  
                h1_trend = 'bullish' if h1_data['close'] > data['H1']['close'].iloc[-10] else 'bearish'
                
                # Calculate proper entry levels using ATR (Gold-specific)
                try:
                    # Try to get actual ATR from analysis
                    h1_processed = self.enhanced_criteria.calculate_all_indicators(data['H1'])
                    atr = h1_processed['atr'].iloc[-1]
                except:
                    # Fallback: estimate ATR as 0.8% of current price for Gold
                    atr = current_price * 0.008
                
                if h1_trend == 'bullish':
                    signal = {
                        'symbol': 'GOLD',
                        'name': 'Gold (XAUUSD)',
                        'direction': 'BUY',
                        'entry': float(current_price),
                        'stop_loss': float(current_price - atr * 1.5),
                        'take_profit_1': float(current_price + atr * 2.0),
                        'take_profit_2': float(current_price + atr * 3.5),
                        'confidence': analysis['percentage'],
                        'score': f"{analysis['total_score']}/20",
                        'criteria_met': analysis['total_score'],
                        'grade': analysis['grade'],
                        'timestamp': datetime.now(),
                        'timeframe': 'H1',
                        'atr': float(atr),
                        'analysis': analysis
                    }
                else:
                    signal = {
                        'symbol': 'GOLD',
                        'name': 'Gold (XAUUSD)', 
                        'direction': 'SELL',
                        'entry': float(current_price),
                        'stop_loss': float(current_price + atr * 1.5),
                        'take_profit_1': float(current_price - atr * 2.0),
                        'take_profit_2': float(current_price - atr * 3.5),
                        'confidence': analysis['percentage'],
                        'score': f"{analysis['total_score']}/20",
                        'criteria_met': analysis['total_score'],
                        'grade': analysis['grade'],
                        'timestamp': datetime.now(),
                        'timeframe': 'H1',
                        'atr': float(atr),
                        'analysis': analysis
                    }
                
                # Calculate risk/reward ratios
                if signal['direction'] == 'BUY':
                    risk = signal['entry'] - signal['stop_loss']
                    reward_1 = signal['take_profit_1'] - signal['entry']
                    reward_2 = signal['take_profit_2'] - signal['entry']
                else:
                    risk = signal['stop_loss'] - signal['entry']
                    reward_1 = signal['entry'] - signal['take_profit_1']
                    reward_2 = signal['entry'] - signal['take_profit_2']
                
                signal['risk_reward_1'] = round(reward_1 / risk, 2) if risk > 0 else 0
                signal['risk_reward_2'] = round(reward_2 / risk, 2) if risk > 0 else 0
                signal['risk_dollars'] = abs(round(risk, 2))
                signal['reward_dollars_1'] = abs(round(reward_1, 2))
                signal['reward_dollars_2'] = abs(round(reward_2, 2))
                
                print(f"✅ ELITE {analysis['grade']} GOLD SIGNAL GENERATED!")
                print(f"   Score: {analysis['total_score']}/20 ({analysis['percentage']:.1f}%)")
                print(f"   Direction: {signal['direction']} at ${current_price:,.2f}")
                print(f"   Confidence: {analysis['confidence_level']}")
                print(f"   ATR: ${atr:.2f}")
                
                success = True
                record_error('signal_generator', operation_context, had_error=False,
                            success_metrics={
                                'signal_generated': True,
                                'signal_score': analysis['total_score'],
                                'signal_confidence': analysis['percentage'],
                                'signal_grade': analysis['grade']
                            },
                            execution_time=time.time() - start_time)

                return signal
            else:
                print(f"⏳ No elite Gold signal - Score: {analysis['total_score']}/20 ({analysis['percentage']:.1f}%)")
                print(f"   Failed criteria: {len(analysis['failed_criteria'])}")
                for i, failure in enumerate(analysis['failed_criteria'][:3]):
                    print(f"   {i+1}. {failure}")

                # Return analysis for partial signals
                success = True  # Successfully determined no elite signal needed
                record_error('signal_generator', operation_context, had_error=False,
                            success_metrics={
                                'signal_generated': False,
                                'criteria_failed': len(analysis['failed_criteria']),
                                'signal_score': analysis['total_score'],
                                'partial_signal_returned': True
                            },
                            execution_time=time.time() - start_time)

                return {
                    'symbol': 'GOLD',
                    'name': 'Gold (XAUUSD)',
                    'direction': 'HOLD',
                    'current_price': float(data['M15']['close'].iloc[-1]),
                    'confidence': analysis['percentage'],
                    'criteria_met': analysis['total_score'],
                    'grade': analysis['grade'],
                    'analysis': analysis,
                    'failed_criteria': analysis['failed_criteria'][:5],
                    'timestamp': datetime.now()
                }

        except Exception as e:
            error_details = str(e)
            record_error('signal_generator', operation_context, had_error=True,
                        error_details=error_details,
                        execution_time=time.time() - start_time)
            print(f"Error generating Gold signal: {e}")
            import traceback
            traceback.print_exc()
            return None

# Testing
if __name__ == "__main__":
    print("="*80)
    print("ENHANCED GOLD SIGNAL GENERATOR - TESTING")
    print("="*80)
    
    generator = EnhancedGoldSignalGenerator()
    signal = generator.generate_signal()
    
    if signal and signal.get('direction') != 'HOLD':
        print("\n" + "="*60)
        print("🥇 GOLD SIGNAL DETAILS:")
        print("="*60)
        print(f"Direction: {signal['direction']}")
        print(f"Entry: ${signal['entry']:,.2f}")
        print(f"Stop Loss: ${signal['stop_loss']:,.2f}")
        print(f"Take Profit 1: ${signal['take_profit_1']:,.2f}")
        print(f"Take Profit 2: ${signal['take_profit_2']:,.2f}")
        print(f"Risk/Reward 1: {signal['risk_reward_1']:.2f}:1")
        print(f"Risk/Reward 2: {signal['risk_reward_2']:.2f}:1")
        print(f"Grade: {signal['grade']}")
        print(f"Score: {signal['score']}")
        print(f"ATR: ${signal['atr']:.2f}")
    elif signal and signal.get('direction') == 'HOLD':
        print("\n" + "="*60)
        print("⏳ GOLD - NO ELITE SIGNAL")
        print("="*60)
        print(f"Current Price: ${signal['current_price']:,.2f}")
        print(f"Score: {signal['criteria_met']}/20 ({signal['confidence']:.1f}%)")
        print(f"Grade: {signal['grade']}")
        print("\nTop Failures:")
        for i, failure in enumerate(signal['failed_criteria'][:5]):
            print(f"  {i+1}. {failure}")
    else:
        print("\n❌ No Gold signal generated - system error")
    
    print("\n" + "="*80)
