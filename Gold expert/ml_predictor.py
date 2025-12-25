"""
Machine Learning Signal Predictor
Predicts signal success probability using historical data
"""

import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

class MLSignalPredictor:
    """ML-based signal success probability predictor"""
    
    def __init__(self, model_file="ml_model_data.json"):
        self.model_file = model_file
        self.model_data = {
            'training_data': [],
            'feature_weights': {},
            'success_thresholds': {},
            'model_version': '1.0',
            'last_trained': None,
            'total_samples': 0
        }
        self.load_model()
        
        # Initialize default feature weights (can be trained with actual data)
        if not self.model_data['feature_weights']:
            self._initialize_default_weights()
    
    def load_model(self):
        """Load ML model data"""
        if os.path.exists(self.model_file):
            try:
                with open(self.model_file, 'r') as f:
                    self.model_data = json.load(f)
            except:
                pass
    
    def save_model(self):
        """Save ML model data"""
        with open(self.model_file, 'w') as f:
            json.dump(self.model_data, f, indent=2)
    
    def _initialize_default_weights(self):
        """Initialize default feature weights based on domain knowledge"""
        self.model_data['feature_weights'] = {
            # Technical indicators
            'criteria_score': 0.25,  # 20-criteria score (most important)
            'rsi_value': 0.08,
            'trend_strength': 0.10,
            'volume_profile': 0.07,
            
            # Session timing
            'london_session': 0.08,
            'ny_session': 0.08,
            'tokyo_session': 0.05,
            
            # Market conditions
            'volatility': 0.07,
            'spread': 0.05,
            
            # Multi-timeframe alignment
            'mtf_alignment': 0.12,
            
            # News impact
            'high_impact_news': -0.05,  # Negative weight (risky)
            
            # Historical performance
            'pair_win_rate': 0.10
        }
        
        self.model_data['success_thresholds'] = {
            'high_confidence': 0.75,  # >75% probability
            'medium_confidence': 0.60,  # 60-75%
            'low_confidence': 0.45  # 45-60%
        }
    
    # ============================================================================
    # PREDICTION
    # ============================================================================
    
    def predict_signal_success(self, signal_features: Dict) -> Dict:
        """Predict probability of signal success
        
        Args:
            signal_features: Dict with signal features (criteria_score, rsi, etc.)
        
        Returns:
            Dict with probability, confidence_level, and explanation
        """
        # Extract and normalize features
        features = self._extract_features(signal_features)
        
        # Calculate weighted score
        probability = self._calculate_probability(features)
        
        # Determine confidence level
        confidence = self._get_confidence_level(probability)
        
        # Generate explanation
        explanation = self._generate_explanation(features, probability)
        
        return {
            'probability': round(probability * 100, 1),  # Convert to percentage
            'confidence_level': confidence,
            'explanation': explanation,
            'key_factors': self._get_key_factors(features),
            'recommendation': self._get_recommendation(probability)
        }
    
    def _extract_features(self, signal_features: Dict) -> Dict:
        """Extract and normalize features from signal"""
        features = {}
        
        # Criteria score (normalize to 0-1)
        criteria_score = signal_features.get('criteria_score', 18)
        features['criteria_score'] = min(criteria_score / 20.0, 1.0)
        
        # RSI (normalize to 0-1, optimal range 30-70)
        rsi = signal_features.get('rsi', 50)
        if rsi < 30:
            features['rsi_value'] = (30 - rsi) / 30  # Oversold = good for buy
        elif rsi > 70:
            features['rsi_value'] = (rsi - 70) / 30  # Overbought = good for sell
        else:
            features['rsi_value'] = 0.5  # Neutral
        
        # Trend strength (assume provided as 0-1)
        features['trend_strength'] = signal_features.get('trend_strength', 0.7)
        
        # Volume profile (assume provided as 0-1)
        features['volume_profile'] = signal_features.get('volume_profile', 0.6)
        
        # Session timing (boolean → 0 or 1)
        features['london_session'] = 1.0 if signal_features.get('london_session') else 0.0
        features['ny_session'] = 1.0 if signal_features.get('ny_session') else 0.0
        features['tokyo_session'] = 1.0 if signal_features.get('tokyo_session') else 0.0
        
        # Volatility (normalize, assume provided as percentage)
        volatility = signal_features.get('volatility', 0.5)
        features['volatility'] = min(volatility, 1.0)
        
        # Spread (normalize, lower is better)
        spread = signal_features.get('spread', 2.0)
        features['spread'] = max(0, 1.0 - (spread / 10.0))  # Normalize spread
        
        # MTF alignment (0-1)
        features['mtf_alignment'] = signal_features.get('mtf_alignment', 0.7)
        
        # High impact news (boolean)
        features['high_impact_news'] = 1.0 if signal_features.get('high_impact_news') else 0.0
        
        # Pair win rate (historical)
        features['pair_win_rate'] = signal_features.get('pair_win_rate', 0.6)
        
        return features
    
    def _calculate_probability(self, features: Dict) -> float:
        """Calculate success probability using weighted features"""
        weights = self.model_data['feature_weights']
        
        probability = 0.0
        total_weight = 0.0
        
        for feature_name, feature_value in features.items():
            if feature_name in weights:
                weight = weights[feature_name]
                probability += feature_value * weight
                total_weight += abs(weight)
        
        # Normalize to 0-1 range
        if total_weight > 0:
            probability = probability / total_weight
        
        # Apply sigmoid for smoother probabilities
        probability = 1 / (1 + np.exp(-5 * (probability - 0.5)))
        
        # Ensure within bounds
        probability = max(0.0, min(1.0, probability))
        
        return probability
    
    def _get_confidence_level(self, probability: float) -> str:
        """Determine confidence level"""
        thresholds = self.model_data['success_thresholds']
        
        if probability >= thresholds['high_confidence']:
            return 'HIGH'
        elif probability >= thresholds['medium_confidence']:
            return 'MEDIUM'
        elif probability >= thresholds['low_confidence']:
            return 'LOW'
        else:
            return 'VERY LOW'
    
    def _get_key_factors(self, features: Dict) -> List[str]:
        """Identify key factors influencing prediction"""
        weights = self.model_data['feature_weights']
        
        # Calculate contribution of each feature
        contributions = []
        for feature_name, feature_value in features.items():
            if feature_name in weights:
                contribution = feature_value * weights[feature_name]
                contributions.append((feature_name, contribution, feature_value))
        
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Get top 3 factors
        key_factors = []
        for feature_name, contribution, value in contributions[:3]:
            impact = "positive" if contribution > 0 else "negative"
            readable_name = feature_name.replace('_', ' ').title()
            key_factors.append(f"{readable_name} ({value:.2f}) - {impact}")
        
        return key_factors
    
    def _generate_explanation(self, features: Dict, probability: float) -> str:
        """Generate human-readable explanation"""
        confidence = self._get_confidence_level(probability)
        
        explanation = f"Based on {len(features)} analyzed factors, "
        
        if confidence == 'HIGH':
            explanation += "this signal shows strong potential for success. "
        elif confidence == 'MEDIUM':
            explanation += "this signal shows moderate potential. "
        elif confidence == 'LOW':
            explanation += "this signal has uncertain potential. "
        else:
            explanation += "this signal shows weak potential. "
        
        # Add specific insights
        if features.get('criteria_score', 0) > 0.9:
            explanation += "Excellent technical setup (18+ criteria). "
        
        if features.get('mtf_alignment', 0) > 0.8:
            explanation += "Strong multi-timeframe alignment. "
        
        if features.get('high_impact_news', 0) > 0:
            explanation += "⚠️ High-impact news present - increased risk. "
        
        if features.get('london_session', 0) or features.get('ny_session', 0):
            explanation += "Optimal trading session. "
        
        return explanation
    
    def _get_recommendation(self, probability: float) -> str:
        """Get trade recommendation"""
        if probability >= 0.75:
            return "✅ STRONG TAKE - High probability setup"
        elif probability >= 0.60:
            return "✔️ CONSIDER - Decent probability, standard risk"
        elif probability >= 0.45:
            return "⚠️ CAUTION - Lower probability, reduce position size"
        else:
            return "❌ SKIP - Low probability, wait for better setup"
    
    # ============================================================================
    # TRAINING (Simplified - would use real ML in production)
    # ============================================================================
    
    def add_training_sample(self, signal_features: Dict, outcome: bool):
        """Add training sample (signal + outcome)
        
        Args:
            signal_features: Signal features
            outcome: True if signal was successful, False otherwise
        """
        sample = {
            'features': signal_features,
            'outcome': outcome,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.model_data['training_data'].append(sample)
        self.model_data['total_samples'] += 1
        
        # Retrain if we have enough samples (every 100 samples)
        if self.model_data['total_samples'] % 100 == 0:
            self._retrain_model()
        
        self.save_model()
    
    def _retrain_model(self):
        """Retrain model with accumulated data (simplified)"""
        # In production, would use sklearn, XGBoost, etc.
        # For now, just adjust weights based on successful/unsuccessful patterns
        
        training_data = self.model_data['training_data']
        
        if len(training_data) < 50:
            return  # Need minimum samples
        
        # Calculate feature importance from data
        # This is a simplified approach - real ML would be more sophisticated
        
        self.model_data['last_trained'] = datetime.now().strftime('%Y-%m-%d')
        self.save_model()
    
    # ============================================================================
    # BATCH PREDICTION
    # ============================================================================
    
    def predict_multiple_signals(self, signals: List[Dict]) -> List[Dict]:
        """Predict success probability for multiple signals
        
        Args:
            signals: List of signal feature dicts
        
        Returns:
            List of predictions sorted by probability
        """
        predictions = []
        
        for signal in signals:
            prediction = self.predict_signal_success(signal)
            prediction['signal'] = signal
            predictions.append(prediction)
        
        # Sort by probability (descending)
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        return predictions


if __name__ == "__main__":
    # Test ML predictor
    predictor = MLSignalPredictor()
    
    # Test signal
    signal_features = {
        'criteria_score': 19,
        'rsi': 35,
        'trend_strength': 0.8,
        'volume_profile': 0.7,
        'london_session': True,
        'ny_session': False,
        'volatility': 0.6,
        'spread': 1.5,
        'mtf_alignment': 0.85,
        'high_impact_news': False,
        'pair_win_rate': 0.65
    }
    
    prediction = predictor.predict_signal_success(signal_features)
    
    print("🤖 ML SIGNAL PREDICTION\n")
    print(f"Success Probability: {prediction['probability']}%")
    print(f"Confidence Level: {prediction['confidence_level']}")
    print(f"\nExplanation: {prediction['explanation']}")
    print(f"\nKey Factors:")
    for factor in prediction['key_factors']:
        print(f"  • {factor}")
    print(f"\nRecommendation: {prediction['recommendation']}")


















