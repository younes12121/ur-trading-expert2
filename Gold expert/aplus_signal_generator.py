"""
Gold A+ Signal Generator - Only Shows Highest Quality Setups
Protects you from mediocre trades and forces patience
"""

from gold_analyzer import GoldScalpingAnalyzer
from aplus_filter import APlusFilter
from datetime import datetime
import config

class GoldAPlusSignalGenerator:
    """
    Generates Gold trading signals but ONLY shows A+ setups
    All other signals are filtered out
    """
    
    def __init__(self, capital=500, risk_per_trade=0.01):
        self.analyzer = GoldScalpingAnalyzer(capital=capital, risk_per_trade=risk_per_trade)
        self.filter = APlusFilter()
        
    def get_signal(self, verbose=True):
        """
        Get trading signal - returns None if not A+ setup
        """
        # Generate signal from analyzer
        signal = self.analyzer.generate_trading_signal()
        market_data = self.analyzer.get_market_data()
        
        # Filter through A+ criteria
        is_aplus, reasons = self.filter.filter_signal(signal, market_data)
        
        # Add filter results to signal
        signal['is_aplus'] = is_aplus
        signal['filter_reasons'] = reasons
        
        if verbose:
            self.print_signal(signal, is_aplus, reasons)
        
        return signal if is_aplus else None
    
    def print_signal(self, signal, is_aplus, reasons):
        """
        Print signal with A+ filter results
        """
        print("\n" + "="*80)
        print("GOLD A+ SIGNAL GENERATOR - STRICT FILTERING ENABLED")
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
        
        print("A+ FILTER ANALYSIS:")
        print("-" * 80)
        
        for criterion, result in reasons.items():
            if criterion not in ['overall', 'news_items']:
                print(f"   {result}")
        
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
            print("[SUCCESS] THIS IS A GOLD A+ SETUP - READY TO TRADE!")
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
            print("[WAIT] NOT A GOLD A+ SETUP - WAIT FOR BETTER OPPORTUNITY")
            print("!" * 80)
            print()
            print("WHAT TO DO:")
            print("   - Be patient - A+ setups are rare")
            print("   - Wait for all criteria to align")
            print("   - Protect your capital")
            print("   - Check back in 1-2 hours")
        
        print("="*80)


def run_gold_aplus_signal():
    """
    Main function to run Gold A+ signal generator
    """
    print("\n>> Starting Gold A+ Signal Generator...")
    print("WARNING: STRICT MODE - Only showing highest probability setups\n")
    
    generator = GoldAPlusSignalGenerator(
        capital=config.CAPITAL,
        risk_per_trade=config.RISK_PER_TRADE
    )
    
    signal = generator.get_signal(verbose=True)
    
    if signal:
        print("\n[SUCCESS] Gold A+ Setup found! Review the details above.")
        return signal
    else:
        print("\n[WAIT] No Gold A+ setup available right now.")
        print("Stay patient - the best trades come to those who wait!")
        return None


if __name__ == "__main__":
    run_gold_aplus_signal()
