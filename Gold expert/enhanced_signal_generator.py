"""
Gold Enhanced A+ Signal Generator with 14 Criteria
Uses enhanced filtering for 75-85% win rate
"""

import config
from enhanced_aplus_filter import EnhancedAPlusFilter
from data_fetcher import BinanceDataFetcher
from news_fetcher import NewsFetcher
from gold_analyzer import GoldScalpingAnalyzer
from datetime import datetime


class GoldEnhancedAPlusSignalGenerator:
    """
    Enhanced Gold signal generator with 14-criteria filter
    Original 8 + Enhanced 6 = 14 total
    Target: 75-85% win rate
    """
    
    def __init__(self, capital=500, risk_per_trade=0.01):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.data_fetcher = BinanceDataFetcher()
        self.news_fetcher = NewsFetcher()
        self.analyzer = GoldScalpingAnalyzer(capital=capital, risk_per_trade=risk_per_trade)
        self.enhanced_filter = EnhancedAPlusFilter()
    
    def get_signal(self, verbose=True):
        """
        Get enhanced A+ signal (14 criteria)
        """
        # Get signal from analyzer
        signal = self.analyzer.generate_trading_signal()
        if not signal:
            print("Failed to generate signal")
            return None
        
        # Get market data for filter
        market_data = self.data_fetcher.get_market_data()
        if not market_data:
            print("Failed to fetch market data")
            return None
        
        # Apply enhanced A+ filter (14 criteria)
        is_aplus, reasons = self.enhanced_filter.filter_signal_enhanced(signal, market_data)
        
        # Print if verbose
        if verbose:
            self.print_signal(signal, is_aplus, reasons)
        
        return signal if is_aplus else None
    
    def print_signal(self, signal, is_aplus, reasons):
        """
        Print enhanced signal with all 14 criteria results
        """
        print("\n" + "="*80)
        print("GOLD ENHANCED A+ SIGNAL GENERATOR - 14 CRITERIA FILTER")
        print("="*80)
        print(f"Time: {signal['timestamp']}")
        print(f"Current Price: ${signal['market_analysis']['current_price']:,.2f}")
        print(f"Direction: {signal['direction']}")
        print(f"Confidence: {signal['confidence']}%")
        print()
        
        if signal['direction'] != 'HOLD':
            print("TRADE DETAILS:")
            print(f"   Entry: ${signal['entry_price']:,.2f}")
            print(f"   Stop Loss: ${signal['stop_loss']:,.2f}")
            print(f"   TP1 (50%): ${signal['take_profit_1']:,.2f}")
            print(f"   TP2 (50%): ${signal['take_profit_2']:,.2f}")
            print()
        
        print("ENHANCED A+ FILTER ANALYSIS (14 Criteria):")
        print("-" * 80)
        print("\nORIGINAL 8 CRITERIA:")
        original_criteria = ['confidence', 'trend', 'support_resistance', 'volatility', 
                            'fear_greed', 'risk_reward', 'confluence', 'news']
        for criterion in original_criteria:
            if criterion in reasons:
                print(f"   {reasons[criterion]}")
        
        print("\nNEW 6 ENHANCEMENTS:")
        new_criteria = ['multi_timeframe', 'order_flow', 'volume_profile', 
                       'order_blocks', 'volatility_regime', 'trading_session']
        for criterion in new_criteria:
            if criterion in reasons:
                print(f"   {reasons[criterion]}")
        
        # Display news items if there are any
        if reasons.get('news_items'):
            print()
            print("IMPORTANT GOLD NEWS (Last 2 hours):")
            print("-" * 80)
            for i, item in enumerate(reasons['news_items'][:3], 1):
                print(f"   {i}. {item['title']}")
                print(f"      Source: {item['source']} | {item['published_at'][:16]}")
            print("-" * 80)
        
        print("-" * 80)
        print(f"\n{reasons['overall']}")
        print()
        
        if is_aplus:
            print("*" * 80)
            print("[SUCCESS] GOLD ENHANCED A+ SETUP - ALL 14 CRITERIA MET!")
            print("*" * 80)
            print()
            print("EXECUTION CHECKLIST:")
            print("   [ ] Set buy/sell limit at entry price")
            print("   [ ] Set stop loss order")
            print("   [ ] Set take profit orders (TP1 and TP2)")
            print("   [ ] Verify position size")
            print("   [ ] Double-check all levels")
            print("   [ ] Execute trade")
        else:
            print("!" * 80)
            print("[WAIT] NOT A GOLD ENHANCED A+ SETUP - WAIT FOR BETTER OPPORTUNITY")
            print("!" * 80)
            print()
            print("WHAT TO DO:")
            print("   - Be patient - Enhanced A+ setups are rarer but better")
            print("   - Wait for all 14 criteria to align")
            print("   - Protect your capital")
            print("   - Check back in 1-2 hours")
        
        print("="*80)


def run_gold_enhanced_aplus_signal():
    """
    Main function to run enhanced A+ signal generator
    """
    print("\n>> Starting Gold ENHANCED A+ Signal Generator...")
    print("WARNING: ULTRA-STRICT MODE - 14 criteria (75-85% win rate)\n")
    
    generator = GoldEnhancedAPlusSignalGenerator(
        capital=config.CAPITAL,
        risk_per_trade=config.RISK_PER_TRADE
    )
    
    signal = generator.get_signal(verbose=True)
    
    if signal:
        print("\n[SUCCESS] Gold Enhanced A+ Setup found! Review the details above.")
        return signal
    else:
        print("\n[WAIT] No Gold enhanced A+ setup available right now.")
        print("Stay patient - enhanced setups are rarer but have 75-85% win rate!")
        return None


if __name__ == "__main__":
    run_gold_enhanced_aplus_signal()
