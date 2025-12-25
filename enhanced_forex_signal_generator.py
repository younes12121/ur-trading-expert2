"""
ENHANCED FOREX Signal Generator with Improved 20-Criteria System
Professional forex analysis for all major pairs with proper validation
Supports: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, EURJPY, NZDUSD, EURGBP, GBPJPY, AUDJPY, USDCHF
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from enhanced_criteria_system import Enhanced20CriteriaSystem
import requests
import json
import warnings

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class EnhancedForexSignalGenerator:
    """
    Enhanced Forex signal generator using the improved 20-criteria system
    Works with any major forex pair
    """
    
    def __init__(self, pair='EURUSD'):
        self.pair = pair.upper()
        self.symbol = f"{pair}=X"  # Yahoo Finance forex format
        self.timeframes = {
            'M15': '15m',
            'H1': '1h', 
            'H4': '4h',
            'D1': '1d'
        }
        self.enhanced_criteria = Enhanced20CriteriaSystem()
        
        # Pair-specific settings
        self.pair_configs = {
            'EURUSD': {'pip_value': 0.0001, 'spread_typical': 0.00015, 'volatility_normal': 0.008},
            'GBPUSD': {'pip_value': 0.0001, 'spread_typical': 0.0002, 'volatility_normal': 0.012},
            'USDJPY': {'pip_value': 0.01, 'spread_typical': 0.015, 'volatility_normal': 0.009},
            'AUDUSD': {'pip_value': 0.0001, 'spread_typical': 0.00018, 'volatility_normal': 0.010},
            'USDCAD': {'pip_value': 0.0001, 'spread_typical': 0.0002, 'volatility_normal': 0.009},
            'EURJPY': {'pip_value': 0.01, 'spread_typical': 0.02, 'volatility_normal': 0.011},
            'NZDUSD': {'pip_value': 0.0001, 'spread_typical': 0.0003, 'volatility_normal': 0.012},
            'EURGBP': {'pip_value': 0.0001, 'spread_typical': 0.0002, 'volatility_normal': 0.007},
            'GBPJPY': {'pip_value': 0.01, 'spread_typical': 0.025, 'volatility_normal': 0.015},
            'AUDJPY': {'pip_value': 0.01, 'spread_typical': 0.02, 'volatility_normal': 0.013},
            'USDCHF': {'pip_value': 0.0001, 'spread_typical': 0.00018, 'volatility_normal': 0.008}
        }
        
        self.config = self.pair_configs.get(self.pair, self.pair_configs['EURUSD'])
        
    def fetch_live_data(self):
        """Fetch live forex data from Yahoo Finance"""
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
                    period = "60d"  # Last 60 days of 4h data  
                else:  # D1
                    period = "1y"   # Last year of daily data
                    
                df = ticker.history(period=period, interval=tf_period)
                
                if df.empty:
                    print(f"Warning: No {self.pair} data for {tf_name}")
                    continue
                    
                # Convert column names to lowercase
                df.columns = [col.lower() for col in df.columns]
                data[tf_name] = df
                
            # If no data fetched, use fallback
            if not data:
                return self.generate_fallback_data()
                
            return data
            
        except Exception as e:
            print(f"Error fetching {self.pair} data: {e}")
            return self.generate_fallback_data()
    
    def generate_fallback_data(self):
        """Generate simulated forex data for testing"""
        np.random.seed(hash(self.pair) % 2**32)  # Different seed per pair
        
        # Base prices for different pairs
        base_prices = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 148.50, 'AUDUSD': 0.6550,
            'USDCAD': 1.3720, 'EURJPY': 161.20, 'NZDUSD': 0.6150, 'EURGBP': 0.8580,
            'GBPJPY': 187.80, 'AUDJPY': 97.30, 'USDCHF': 0.8890
        }
        
        base_price = base_prices.get(self.pair, 1.1000)
        volatility = self.config['volatility_normal']
        
        data = {}
        for tf in ['M15', 'H1', 'H4', 'D1']:
            if tf == 'M15':
                periods = 480  # 5 days of 15min candles
                freq = '15T'
            elif tf == 'H1':
                periods = 720  # 30 days of hourly candles  
                freq = '1h'  # Changed from '1H' to '1h' (deprecated)
            elif tf == 'H4':
                periods = 360  # 60 days of 4h candles
                freq = '4H'
            else:  # D1
                periods = 365  # 1 year of daily candles
                freq = '1D'
                
            dates = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
            
            # Generate realistic forex price movements
            returns = np.random.normal(0, volatility / (24 if tf == 'D1' else 1), periods)
            prices = [base_price]
            for r in returns[1:]:
                new_price = prices[-1] * (1 + r)
                prices.append(new_price)
            
            df = pd.DataFrame({
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, volatility/3))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, volatility/3))) for p in prices],
                'close': prices,
                'volume': np.random.randint(1000, 5000, periods)  # Forex volume is often unavailable
            }, index=dates)
            
            # Ensure high >= low relationships (using vectorized operations to avoid SettingWithCopyWarning)
            df['high'] = df[['open', 'close', 'high']].max(axis=1)
            df['low'] = df[['open', 'close', 'low']].min(axis=1)
            
            data[tf] = df
            
        print(f"Using simulated {self.pair} data for analysis...")
        return data
    
    def get_current_session_info(self):
        """Get current forex trading session information"""
        current_hour = datetime.now().hour
        
        # UTC times for major sessions
        sessions = {
            'Sydney': (22, 7),
            'Tokyo': (0, 9),
            'London': (8, 17),
            'New York': (13, 22)
        }
        
        active_sessions = []
        for session, (start, end) in sessions.items():
            if start <= current_hour <= end or (start > end and (current_hour >= start or current_hour <= end)):
                active_sessions.append(session)
        
        # Determine liquidity level
        if 'London' in active_sessions and 'New York' in active_sessions:
            liquidity = 'MAXIMUM'
            session_description = 'London-NY Overlap'
        elif 'London' in active_sessions or 'New York' in active_sessions:
            liquidity = 'HIGH'
            session_description = active_sessions[0]
        elif 'Tokyo' in active_sessions:
            liquidity = 'MEDIUM'
            session_description = 'Asian Session'
        else:
            liquidity = 'LOW'
            session_description = 'Between Sessions'
        
        return {
            'active_sessions': active_sessions,
            'liquidity': liquidity,
            'description': session_description,
            'optimal': liquidity in ['MAXIMUM', 'HIGH']
        }
    
    def generate_signal(self):
        """Generate forex signal using enhanced 20-criteria system"""
        try:
            print(f"💱 Fetching live {self.pair} data...")
            data = self.fetch_live_data()
            
            if not data:
                print(f"❌ Failed to fetch {self.pair} data")
                return None
            
            print(f"🧮 Applying enhanced 20-criteria {self.pair} analysis...")
            is_elite, analysis = self.enhanced_criteria.apply_enhanced_criteria(data, self.pair)
            
            # Get session info
            session_info = self.get_current_session_info()
            
            if is_elite:
                # Generate detailed forex signal
                current_price = data['M15']['close'].iloc[-1]
                h1_data = data['H1'].iloc[-1]
                
                # Determine direction from trend analysis  
                h1_trend = 'bullish' if h1_data['close'] > data['H1']['close'].iloc[-10] else 'bearish'
                
                # Calculate proper entry levels using ATR (forex-specific)
                try:
                    # Try to get actual ATR from analysis
                    h1_processed = self.enhanced_criteria.calculate_all_indicators(data['H1'])
                    atr = h1_processed['atr'].iloc[-1]
                except:
                    # Fallback: estimate ATR based on pair volatility
                    atr = current_price * self.config['volatility_normal']
                
                if h1_trend == 'bullish':
                    signal = {
                        'symbol': self.pair,
                        'name': f"{self.pair[:3]}/{self.pair[3:]}",
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
                        'pip_value': self.config['pip_value'],
                        'session_info': session_info,
                        'analysis': analysis
                    }
                else:
                    signal = {
                        'symbol': self.pair,
                        'name': f"{self.pair[:3]}/{self.pair[3:]}",
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
                        'pip_value': self.config['pip_value'],
                        'session_info': session_info,
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
                signal['risk_pips'] = abs(round(risk / self.config['pip_value'], 1))
                signal['reward_pips_1'] = abs(round(reward_1 / self.config['pip_value'], 1))
                signal['reward_pips_2'] = abs(round(reward_2 / self.config['pip_value'], 1))
                
                print(f"✅ ELITE {analysis['grade']} {self.pair} SIGNAL GENERATED!")
                print(f"   Score: {analysis['total_score']}/20 ({analysis['percentage']:.1f}%)")
                print(f"   Direction: {signal['direction']} at {current_price:.5f}")
                print(f"   Confidence: {analysis['confidence_level']}")
                print(f"   Session: {session_info['description']} ({session_info['liquidity']} liquidity)")
                print(f"   Risk: {signal['risk_pips']} pips")
                
                return signal
            else:
                print(f"⏳ No elite {self.pair} signal - Score: {analysis['total_score']}/20 ({analysis['percentage']:.1f}%)")
                print(f"   Failed criteria: {len(analysis['failed_criteria'])}")
                print(f"   Session: {session_info['description']} ({session_info['liquidity']} liquidity)")
                for i, failure in enumerate(analysis['failed_criteria'][:3]):
                    print(f"   {i+1}. {failure}")
                
                # Return analysis for partial signals
                return {
                    'symbol': self.pair,
                    'name': f"{self.pair[:3]}/{self.pair[3:]}",
                    'direction': 'HOLD',
                    'current_price': float(data['M15']['close'].iloc[-1]),
                    'confidence': analysis['percentage'],
                    'criteria_met': analysis['total_score'],
                    'grade': analysis['grade'],
                    'session_info': session_info,
                    'analysis': analysis,
                    'failed_criteria': analysis['failed_criteria'][:5],
                    'timestamp': datetime.now()
                }
                
        except Exception as e:
            print(f"Error generating {self.pair} signal: {e}")
            import traceback
            traceback.print_exc()
            return None

# Multi-pair testing function
def test_multiple_pairs():
    """Test multiple forex pairs"""
    major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
    
    print("="*100)
    print("ENHANCED FOREX SIGNAL GENERATOR - MULTI-PAIR TESTING")
    print("="*100)
    
    results = {}
    
    for pair in major_pairs:
        print(f"\n{'='*20} {pair} {'='*20}")
        generator = EnhancedForexSignalGenerator(pair)
        signal = generator.generate_signal()
        
        results[pair] = signal
        
        if signal and signal.get('direction') != 'HOLD':
            print(f"✅ {pair}: {signal['direction']} signal ({signal['grade']})")
        elif signal:
            print(f"⏳ {pair}: No elite signal ({signal['criteria_met']}/20)")
        else:
            print(f"❌ {pair}: Error generating signal")
    
    # Summary
    print(f"\n{'='*100}")
    print("SUMMARY:")
    print(f"{'='*100}")
    
    for pair, signal in results.items():
        if signal and signal.get('direction') != 'HOLD':
            print(f"🟢 {pair}: {signal['direction']} @ {signal['entry']:.5f} ({signal['score']})")
        elif signal:
            print(f"🟡 {pair}: HOLD @ {signal['current_price']:.5f} ({signal['criteria_met']}/20)")
        else:
            print(f"🔴 {pair}: ERROR")
    
    print(f"\n{'='*100}")

# Testing
if __name__ == "__main__":
    # Test single pair
    print("="*80)
    print("ENHANCED FOREX SIGNAL GENERATOR - EURUSD TESTING")
    print("="*80)
    
    generator = EnhancedForexSignalGenerator('EURUSD')
    signal = generator.generate_signal()
    
    if signal and signal.get('direction') != 'HOLD':
        print("\n" + "="*60)
        print("💱 EURUSD SIGNAL DETAILS:")
        print("="*60)
        print(f"Direction: {signal['direction']}")
        print(f"Entry: {signal['entry']:.5f}")
        print(f"Stop Loss: {signal['stop_loss']:.5f}")
        print(f"Take Profit 1: {signal['take_profit_1']:.5f}")
        print(f"Take Profit 2: {signal['take_profit_2']:.5f}")
        print(f"Risk/Reward 1: {signal['risk_reward_1']:.2f}:1")
        print(f"Risk/Reward 2: {signal['risk_reward_2']:.2f}:1")
        print(f"Risk: {signal['risk_pips']} pips")
        print(f"Reward 1: {signal['reward_pips_1']} pips")
        print(f"Grade: {signal['grade']}")
        print(f"Score: {signal['score']}")
        print(f"Session: {signal['session_info']['description']}")
    elif signal and signal.get('direction') == 'HOLD':
        print("\n" + "="*60)
        print("⏳ EURUSD - NO ELITE SIGNAL")
        print("="*60)
        print(f"Current Price: {signal['current_price']:.5f}")
        print(f"Score: {signal['criteria_met']}/20 ({signal['confidence']:.1f}%)")
        print(f"Grade: {signal['grade']}")
        print(f"Session: {signal['session_info']['description']}")
        print("\nTop Failures:")
        for i, failure in enumerate(signal['failed_criteria'][:5]):
            print(f"  {i+1}. {failure}")
    else:
        print("\n❌ No EURUSD signal generated - system error")
    
    # Uncomment to test multiple pairs
    # print("\n\n")
    # test_multiple_pairs()
    
    print("\n" + "="*80)
