"""
Run Signal Optimization
Optimize trading strategy parameters
"""

from historical_data import HistoricalDataManager
from signal_optimizer import SignalOptimizer, SignalStrengthScorer
from multi_timeframe import MultiTimeframeAnalyzer, AdaptiveParameterManager
import config

def run_optimization():
    """Run complete signal optimization"""
    print("=" * 70)
    print("🎯 SIGNAL OPTIMIZATION")
    print("=" * 70)
    print()
    
    # Step 1: Download historical data
    print("📥 Step 1: Loading Historical Data...")
    data_manager = HistoricalDataManager()
    data = data_manager.get_data(interval="5m", days=30, use_cache=True)
    
    if data is None:
        print("❌ Failed to load data")
        return
    
    print(f"✅ Loaded {len(data)} candles")
    print()
    
    # Step 2: Optimize signal thresholds
    print("🔍 Step 2: Optimizing Signal Thresholds...")
    optimizer = SignalOptimizer(data, initial_capital=500)
    
    best_params = optimizer.optimize_signal_thresholds()
    
    print(f"\n🏆 Best Parameters Found:")
    for key, value in best_params.items():
        print(f"   {key}: {value}")
    
    # Save results
    if len(optimizer.optimization_results) > 0:
        optimizer.optimization_results.to_csv('data_cache/optimization_results.csv', index=False)
        print("\n💾 Results saved to data_cache/optimization_results.csv")
    
    print("\n" + "=" * 70)
    print("✅ OPTIMIZATION COMPLETE!")
    print("=" * 70)
    
    return best_params


def test_multi_timeframe():
    """Test multi-timeframe analysis"""
    print("\n" + "=" * 70)
    print("📊 TESTING MULTI-TIMEFRAME ANALYSIS")
    print("=" * 70)
    print()
    
    mtf = MultiTimeframeAnalyzer()
    mtf.print_mtf_analysis()
    
    # Test signal confirmation
    print("\n🎯 Testing Signal Confirmation:")
    buy_confirmed = mtf.get_higher_timeframe_confirmation('BUY')
    sell_confirmed = mtf.get_higher_timeframe_confirmation('SELL')
    
    print(f"   BUY signal confirmed: {buy_confirmed}")
    print(f"   SELL signal confirmed: {sell_confirmed}")


def test_adaptive_parameters():
    """Test adaptive parameter management"""
    print("\n" + "=" * 70)
    print("🔄 TESTING ADAPTIVE PARAMETERS")
    print("=" * 70)
    print()
    
    from data_fetcher import BinanceDataFetcher
    
    fetcher = BinanceDataFetcher()
    market_data = fetcher.get_market_data()
    
    if market_data:
        adaptive = AdaptiveParameterManager()
        params = adaptive.get_adaptive_parameters(market_data)
        
        print(f"Current Market Regime: {params['regime']}")
        print(f"Adaptive Parameters:")
        print(f"   Risk per Trade: {params['risk_per_trade'] * 100}%")
        print(f"   TP Multiplier: {params['tp_multiplier']}x")
        print(f"   Confidence Threshold: {params['confidence_threshold']}%")
        print(f"   Should Trade: {adaptive.should_trade_in_regime()}")


def test_signal_strength():
    """Test signal strength scoring"""
    print("\n" + "=" * 70)
    print("💪 TESTING SIGNAL STRENGTH SCORING")
    print("=" * 70)
    print()
    
    from data_fetcher import BinanceDataFetcher
    
    fetcher = BinanceDataFetcher()
    market_data = fetcher.get_market_data()
    
    if market_data:
        scorer = SignalStrengthScorer()
        
        # Test with a sample signal
        signal = {
            'direction': 'BUY',
            'confidence': 70
        }
        
        score = scorer.calculate_score(market_data, signal)
        
        print(f"Signal Strength Score: {score}/100")
        
        if score >= 80:
            print("   Rating: ⭐⭐⭐⭐⭐ Excellent")
        elif score >= 70:
            print("   Rating: ⭐⭐⭐⭐ Good")
        elif score >= 60:
            print("   Rating: ⭐⭐⭐ Fair")
        else:
            print("   Rating: ⭐⭐ Weak")


if __name__ == "__main__":
    print("\n" + "*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  SIGNAL OPTIMIZATION SUITE".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    print("Select test to run:")
    print("1. Run full optimization (30 days data)")
    print("2. Test multi-timeframe analysis")
    print("3. Test adaptive parameters")
    print("4. Test signal strength scoring")
    print("5. Run all tests")
    print()
    
    try:
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "1":
            run_optimization()
        elif choice == "2":
            test_multi_timeframe()
        elif choice == "3":
            test_adaptive_parameters()
        elif choice == "4":
            test_signal_strength()
        elif choice == "5":
            run_optimization()
            test_multi_timeframe()
            test_adaptive_parameters()
            test_signal_strength()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
