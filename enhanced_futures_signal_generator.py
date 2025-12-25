"""
ENHANCED FUTURES Signal Generator with Improved 20-Criteria System
Professional ES (E-mini S&P 500) and NQ (E-mini NASDAQ-100) analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from enhanced_criteria_system import Enhanced20CriteriaSystem

class EnhancedFuturesSignalGenerator:
    """
    Enhanced Futures signal generator for ES and NQ using improved 20-criteria system
    """
    
    def __init__(self, futures_symbol='ES'):
        self.futures_symbol = futures_symbol.upper()
        
        # Symbol mappings for Yahoo Finance
        symbol_map = {
            'ES': 'ES=F',  # E-mini S&P 500
            'NQ': 'NQ=F',  # E-mini NASDAQ-100
            'YM': 'YM=F',  # E-mini Dow Jones
            'RTY': 'RTY=F' # E-mini Russell 2000
        }
        
        self.symbol = symbol_map.get(self.futures_symbol, 'ES=F')
        
        self.timeframes = {
            'M15': '15m',
            'H1': '1h', 
            'H4': '4h',
            'D1': '1d'
        }
        
        self.enhanced_criteria = Enhanced20CriteriaSystem()
        
        # Futures-specific settings
        self.futures_configs = {
            'ES': {
                'name': 'E-mini S&P 500',
                'point_value': 50,    # $50 per point
                'tick_size': 0.25,    # 0.25 points
                'typical_atr': 25,    # Typical ATR in points
                'session_hours': (13, 21)  # US market hours UTC
            },
            'NQ': {
                'name': 'E-mini NASDAQ-100',
                'point_value': 20,    # $20 per point
                'tick_size': 0.25,    # 0.25 points
                'typical_atr': 60,    # Typical ATR in points
                'session_hours': (13, 21)  # US market hours UTC
            },
            'YM': {
                'name': 'E-mini Dow Jones',
                'point_value': 5,     # $5 per point
                'tick_size': 1.0,     # 1 point
                'typical_atr': 150,   # Typical ATR in points
                'session_hours': (13, 21)
            },
            'RTY': {
                'name': 'E-mini Russell 2000',
                'point_value': 50,    # $50 per point
                'tick_size': 0.10,    # 0.10 points
                'typical_atr': 15,    # Typical ATR in points
                'session_hours': (13, 21)
            }
        }
        
        self.config = self.futures_configs.get(self.futures_symbol, self.futures_configs['ES'])
        
    def fetch_live_data(self):
        """Fetch live futures data from Yahoo Finance"""
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
                    period = "2y"   # Last 2 years of daily data
                    
                df = ticker.history(period=period, interval=tf_period)
                
                if df.empty:
                    print(f"Warning: No {self.futures_symbol} data for {tf_name}")
                    continue
                    
                # Convert column names to lowercase
                df.columns = [col.lower() for col in df.columns]
                data[tf_name] = df
                
            # If no data fetched, use fallback
            if not data:
                return self.generate_fallback_data()
                
            return data
            
        except Exception as e:
            print(f"Error fetching {self.futures_symbol} data: {e}")
            return self.generate_fallback_data()
    
    def generate_fallback_data(self):
        """Generate simulated futures data for testing"""
        np.random.seed(hash(self.futures_symbol) % 2**32)
        
        # Base prices for different futures
        base_prices = {
            'ES': 4500.0,   # S&P 500 E-mini
            'NQ': 15500.0,  # NASDAQ-100 E-mini
            'YM': 35000.0,  # Dow Jones E-mini
            'RTY': 2000.0   # Russell 2000 E-mini
        }
        
        base_price = base_prices.get(self.futures_symbol, 4500.0)
        
        data = {}
        for tf in ['M15', 'H1', 'H4', 'D1']:
            if tf == 'M15':
                periods = 480  # 5 days of 15min candles
                freq = '15T'
            elif tf == 'H1':
                periods = 720  # 30 days of hourly candles  
                freq = '1H'
            elif tf == 'H4':
                periods = 360  # 60 days of 4h candles
                freq = '4H'
            else:  # D1
                periods = 730  # 2 years of daily candles
                freq = '1D'
                
            dates = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
            
            # Generate realistic futures price movements
            daily_vol = 0.015 if self.futures_symbol == 'NQ' else 0.012  # NQ more volatile
            returns = np.random.normal(0, daily_vol / (24 if tf == 'D1' else 1), periods)
            prices = [base_price]
            for r in returns[1:]:
                new_price = prices[-1] * (1 + r)
                prices.append(new_price)
            
            df = pd.DataFrame({
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
                'close': prices,
                'volume': np.random.randint(50000, 200000, periods)  # Futures have good volume data
            }, index=dates)
            
            # Ensure high >= low relationships
            for i in range(len(df)):
                df.iloc[i]['high'] = max(df.iloc[i]['open'], df.iloc[i]['close'], df.iloc[i]['high'])
                df.iloc[i]['low'] = min(df.iloc[i]['open'], df.iloc[i]['close'], df.iloc[i]['low'])
            
            data[tf] = df
            
        print(f"Using simulated {self.futures_symbol} data for analysis...")
        return data
    
    def is_market_session(self):
        """Check if US futures market is active"""
        current_hour = datetime.now().hour
        session_start, session_end = self.config['session_hours']
        
        if session_start <= current_hour <= session_end:
            return True, "US Regular Session"
        elif 18 <= current_hour <= 23 or 0 <= current_hour <= 7:
            return True, "Overnight Session"  # Futures trade nearly 24/7
        else:
            return False, "Market Closed"
    
    def generate_signal(self):
        """Generate futures signal using enhanced 20-criteria system"""
        try:
            print(f"📊 Fetching live {self.futures_symbol} ({self.config['name']}) data...")
            data = self.fetch_live_data()
            
            if not data:
                print(f"❌ Failed to fetch {self.futures_symbol} data")
                return None
            
            print(f"🧮 Applying enhanced 20-criteria {self.futures_symbol} analysis...")
            is_elite, analysis = self.enhanced_criteria.apply_enhanced_criteria(data, self.futures_symbol)
            
            # Get market session info
            market_active, session_type = self.is_market_session()
            
            if is_elite:
                # Generate detailed futures signal
                current_price = data['M15']['close'].iloc[-1]
                h1_data = data['H1'].iloc[-1]
                
                # Determine direction from trend analysis  
                h1_trend = 'bullish' if h1_data['close'] > data['H1']['close'].iloc[-10] else 'bearish'
                
                # Calculate proper entry levels using ATR (futures-specific)
                try:
                    # Try to get actual ATR from analysis
                    h1_processed = self.enhanced_criteria.calculate_all_indicators(data['H1'])
                    atr = h1_processed['atr'].iloc[-1]
                except:
                    # Fallback: use typical ATR for the futures contract
                    atr = self.config['typical_atr']
                
                if h1_trend == 'bullish':
                    signal = {
                        'symbol': self.futures_symbol,
                        'name': self.config['name'],
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
                        'atr_points': float(atr),
                        'point_value': self.config['point_value'],
                        'tick_size': self.config['tick_size'],
                        'market_session': session_type,
                        'analysis': analysis
                    }
                else:
                    signal = {
                        'symbol': self.futures_symbol,
                        'name': self.config['name'],
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
                        'atr_points': float(atr),
                        'point_value': self.config['point_value'],
                        'tick_size': self.config['tick_size'],
                        'market_session': session_type,
                        'analysis': analysis
                    }
                
                # Calculate risk/reward ratios
                if signal['direction'] == 'BUY':
                    risk_points = signal['entry'] - signal['stop_loss']
                    reward_points_1 = signal['take_profit_1'] - signal['entry']
                    reward_points_2 = signal['take_profit_2'] - signal['entry']
                else:
                    risk_points = signal['stop_loss'] - signal['entry']
                    reward_points_1 = signal['entry'] - signal['take_profit_1']
                    reward_points_2 = signal['entry'] - signal['take_profit_2']
                
                signal['risk_reward_1'] = round(reward_points_1 / risk_points, 2) if risk_points > 0 else 0
                signal['risk_reward_2'] = round(reward_points_2 / risk_points, 2) if risk_points > 0 else 0
                signal['risk_points'] = abs(round(risk_points, 2))
                signal['reward_points_1'] = abs(round(reward_points_1, 2))
                signal['reward_points_2'] = abs(round(reward_points_2, 2))
                signal['risk_dollars'] = abs(round(risk_points * self.config['point_value'], 2))
                signal['reward_dollars_1'] = abs(round(reward_points_1 * self.config['point_value'], 2))
                signal['reward_dollars_2'] = abs(round(reward_points_2 * self.config['point_value'], 2))
                
                print(f"✅ ELITE {analysis['grade']} {self.futures_symbol} SIGNAL GENERATED!")
                print(f"   Score: {analysis['total_score']}/20 ({analysis['percentage']:.1f}%)")
                print(f"   Direction: {signal['direction']} at {current_price:,.2f}")
                print(f"   Confidence: {analysis['confidence_level']}")
                print(f"   Session: {session_type}")
                print(f"   Risk: {signal['risk_points']:.1f} points (${signal['risk_dollars']:,.0f})")
                
                return signal
            else:
                print(f"⏳ No elite {self.futures_symbol} signal - Score: {analysis['total_score']}/20 ({analysis['percentage']:.1f}%)")
                print(f"   Failed criteria: {len(analysis['failed_criteria'])}")
                print(f"   Session: {session_type}")
                for i, failure in enumerate(analysis['failed_criteria'][:3]):
                    print(f"   {i+1}. {failure}")
                
                # Return analysis for partial signals
                return {
                    'symbol': self.futures_symbol,
                    'name': self.config['name'],
                    'direction': 'HOLD',
                    'current_price': float(data['M15']['close'].iloc[-1]),
                    'confidence': analysis['percentage'],
                    'criteria_met': analysis['total_score'],
                    'grade': analysis['grade'],
                    'market_session': session_type,
                    'analysis': analysis,
                    'failed_criteria': analysis['failed_criteria'][:5],
                    'timestamp': datetime.now()
                }
                
        except Exception as e:
            print(f"Error generating {self.futures_symbol} signal: {e}")
            import traceback
            traceback.print_exc()
            return None

# Multi-futures testing function
def test_multiple_futures():
    """Test multiple futures contracts"""
    futures_list = ['ES', 'NQ']
    
    print("="*100)
    print("ENHANCED FUTURES SIGNAL GENERATOR - MULTI-CONTRACT TESTING")
    print("="*100)
    
    results = {}
    
    for futures in futures_list:
        print(f"\n{'='*20} {futures} {'='*20}")
        generator = EnhancedFuturesSignalGenerator(futures)
        signal = generator.generate_signal()
        
        results[futures] = signal
        
        if signal and signal.get('direction') != 'HOLD':
            print(f"✅ {futures}: {signal['direction']} signal ({signal['grade']})")
        elif signal:
            print(f"⏳ {futures}: No elite signal ({signal['criteria_met']}/20)")
        else:
            print(f"❌ {futures}: Error generating signal")
    
    # Summary
    print(f"\n{'='*100}")
    print("SUMMARY:")
    print(f"{'='*100}")
    
    for futures, signal in results.items():
        if signal and signal.get('direction') != 'HOLD':
            print(f"🟢 {futures}: {signal['direction']} @ {signal['entry']:,.2f} ({signal['score']})")
        elif signal:
            print(f"🟡 {futures}: HOLD @ {signal['current_price']:,.2f} ({signal['criteria_met']}/20)")
        else:
            print(f"🔴 {futures}: ERROR")
    
    print(f"\n{'='*100}")

# Testing
if __name__ == "__main__":
    # Test ES contract
    print("="*80)
    print("ENHANCED FUTURES SIGNAL GENERATOR - ES TESTING")
    print("="*80)
    
    generator = EnhancedFuturesSignalGenerator('ES')
    signal = generator.generate_signal()
    
    if signal and signal.get('direction') != 'HOLD':
        print("\n" + "="*60)
        print("📊 ES SIGNAL DETAILS:")
        print("="*60)
        print(f"Direction: {signal['direction']}")
        print(f"Entry: {signal['entry']:,.2f}")
        print(f"Stop Loss: {signal['stop_loss']:,.2f}")
        print(f"Take Profit 1: {signal['take_profit_1']:,.2f}")
        print(f"Take Profit 2: {signal['take_profit_2']:,.2f}")
        print(f"Risk/Reward 1: {signal['risk_reward_1']:.2f}:1")
        print(f"Risk/Reward 2: {signal['risk_reward_2']:.2f}:1")
        print(f"Risk: {signal['risk_points']:.1f} pts (${signal['risk_dollars']:,.0f})")
        print(f"Reward 1: {signal['reward_points_1']:.1f} pts (${signal['reward_dollars_1']:,.0f})")
        print(f"Grade: {signal['grade']}")
        print(f"Score: {signal['score']}")
        print(f"Session: {signal['market_session']}")
    elif signal and signal.get('direction') == 'HOLD':
        print("\n" + "="*60)
        print("⏳ ES - NO ELITE SIGNAL")
        print("="*60)
        print(f"Current Price: {signal['current_price']:,.2f}")
        print(f"Score: {signal['criteria_met']}/20 ({signal['confidence']:.1f}%)")
        print(f"Grade: {signal['grade']}")
        print(f"Session: {signal['market_session']}")
        print("\nTop Failures:")
        for i, failure in enumerate(signal['failed_criteria'][:5]):
            print(f"  {i+1}. {failure}")
    else:
        print("\n❌ No ES signal generated - system error")
    
    # Test both ES and NQ
    print("\n\n")
    test_multiple_futures()
    
    print("\n" + "="*80)
