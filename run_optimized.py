#!/usr/bin/env python3
"""
High-Performance Trading System Launcher
Optimized for maximum speed and efficiency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config

def run_health_check():
    """Run system health check"""
    print("Running system health check...")
    try:
        from health_check import main as health_main
        return health_main()
    except ImportError:
        print("Health check not available")
        return False

def main():
    """Main performance launcher"""
    print("HIGH-PERFORMANCE TRADING SYSTEM")
    print("="*50)
    print("All optimizations enabled for maximum speed!")
    print()

    # Run health check first
    if not run_health_check():
        print("Health check failed. Please run health_check.py manually.")
        return False

    try:
        # Test optimized components
        print("Testing optimized components...")

        # Test data fetching
        from data_fetcher import BinanceDataFetcher
        fetcher = BinanceDataFetcher(performance_mode=True)
        print("Data fetcher initialized with performance mode")

        # Test signal generation
        from elite_signal_generator import EliteAPlusSignalGenerator
        generator = EliteAPlusSignalGenerator(performance_mode=True)
        print("Signal generator initialized with performance mode")

        # Test AI predictions
        from ai_neural_predictor import NeuralPredictor
        predictor = NeuralPredictor(performance_mode=True)
        print("AI predictor initialized with performance mode")

        print("
All optimized components tested successfully!")
        print("Ready for high-performance trading operations!")

    except Exception as e:
        print(f"Error during optimization test: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
