#!/usr/bin/env python3
"""Test AI module imports"""

import sys
import os

# Add staging directory to path
sys.path.insert(0, 'staging')

print("Testing AI module imports...")

try:
    from ai_advanced_neural_predictor import QuantumEliteNeuralPredictor
    print("[OK] Neural predictor: OK")
except ImportError as e:
    print(f"[FAIL] Neural predictor: FAILED - {e}")

try:
    from ai_advanced_reinforcement_learning import QuantumEliteStrategyManager
    print("[OK] RL: OK")
except ImportError as e:
    print(f"[FAIL] RL: FAILED - {e}")

try:
    from ai_federated_learning import QuantumEliteFederatedLearning
    print("[OK] FL: OK")
except ImportError as e:
    print(f"[FAIL] FL: FAILED - {e}")

try:
    from ai_nlp_market_intelligence import MarketSentimentAnalyzer
    print("[OK] NLP: OK")
except ImportError as e:
    print(f"[FAIL] NLP: FAILED - {e}")

try:
    from ai_realtime_predictive_analytics import StreamingDataProcessor
    print("[OK] Predictive Analytics: OK")
except ImportError as e:
    print(f"[FAIL] Predictive Analytics: FAILED - {e}")

print("Import test complete.")
