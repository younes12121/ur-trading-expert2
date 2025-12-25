"""
AI Market Regime Detection
Uses machine learning to automatically detect and classify market regimes
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketRegimeDetector:
    """AI-powered market regime detection system"""

    def __init__(self, models_dir: str = "regime_models"):
        self.models_dir = models_dir
        self.regime_model = None
        self.scaler = StandardScaler()
        self.regime_history = []
        self.regime_definitions = {
            'strong_bull': {
                'description': 'Strong upward trend with low volatility',
                'trend_threshold': 0.02,
                'volatility_threshold': 0.015,
                'confidence_required': 0.8
            },
            'bull': {
                'description': 'Moderate upward trend',
                'trend_threshold': 0.01,
                'volatility_threshold': 0.025,
                'confidence_required': 0.7
            },
            'strong_bear': {
                'description': 'Strong downward trend with low volatility',
                'trend_threshold': -0.02,
                'volatility_threshold': 0.015,
                'confidence_required': 0.8
            },
            'bear': {
                'description': 'Moderate downward trend',
                'trend_threshold': -0.01,
                'volatility_threshold': 0.025,
                'confidence_required': 0.7
            },
            'sideways': {
                'description': 'Range-bound market with no clear direction',
                'trend_threshold': 0.005,
                'volatility_threshold': 0.02,
                'confidence_required': 0.6
            },
            'volatile': {
                'description': 'High volatility with unclear direction',
                'trend_threshold': 0.01,
                'volatility_threshold': 0.04,
                'confidence_required': 0.7
            },
            'breakout': {
                'description': 'Recent strong price movement suggesting breakout',
                'trend_threshold': 0.015,
                'volatility_threshold': 0.035,
                'confidence_required': 0.75
            }
        }

        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        self.load_model()

    def load_model(self) -> bool:
        """Load trained regime detection model"""
        model_path = f"{self.models_dir}/regime_classifier.pkl"
        scaler_path = f"{self.models_dir}/regime_scaler.pkl"

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.regime_model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                logger.info("Loaded existing regime detection model")
                return True
            except Exception as e:
                logger.error(f"Error loading regime model: {e}")
                return False
        return False

    def save_model(self):
        """Save trained model to disk"""
        if self.regime_model:
            joblib.dump(self.regime_model, f"{self.models_dir}/regime_classifier.pkl")
            joblib.dump(self.scaler, f"{self.models_dir}/regime_scaler.pkl")
            logger.info("Saved regime detection model")

    def create_regime_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create comprehensive feature set for regime detection"""

        features = []

        # Price-based features
        if 'close' in df.columns:
            close_prices = df['close']

            # Trend features
            features.append(close_prices.pct_change(5).fillna(0))   # 5-period return
            features.append(close_prices.pct_change(20).fillna(0))  # 20-period return
            features.append(close_prices.pct_change(50).fillna(0))  # 50-period return

            # Momentum features
            features.append(close_prices / close_prices.shift(20).fillna(close_prices.iloc[0]))  # Price ratio
            features.append((close_prices - close_prices.rolling(20).mean()) / close_prices.rolling(20).std())  # Z-score

        # Volatility features
        if len(features) > 0:
            returns = features[0]  # 5-period returns
            features.append(returns.rolling(20).std().fillna(0))   # Rolling volatility
            features.append(returns.rolling(50).std().fillna(0))   # Long-term volatility

        # Volume features
        if 'volume' in df.columns:
            volume = df['volume']
            features.append(volume.pct_change(5).fillna(0))        # Volume change
            features.append(volume / volume.rolling(20).mean())     # Volume ratio

        # Technical indicators
        if 'sma_20' in df.columns and 'close' in df.columns:
            features.append((df['close'] - df['sma_20']) / df['sma_20'])  # Price vs SMA20

        if 'sma_50' in df.columns and 'close' in df.columns:
            features.append((df['close'] - df['sma_50']) / df['sma_50'])  # Price vs SMA50

        if 'rsi' in df.columns:
            features.append(df['rsi'] / 100.0)  # Normalized RSI

        if 'macd' in df.columns:
            features.append(df['macd'].fillna(0))  # MACD

        # Bollinger Band position
        if all(col in df.columns for col in ['close', 'bb_upper', 'bb_lower']):
            features.append((df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower']))

        # Average True Range (volatility measure)
        if all(col in df.columns for col in ['high', 'low', 'close']):
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift(1)).abs()
            low_close = (df['low'] - df['close'].shift(1)).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            features.append(tr.rolling(14).mean().fillna(0))  # ATR

        return np.column_stack(features) if features else np.array([])

    def train_regime_model(self, historical_data: Dict[str, pd.DataFrame],
                          labels: Optional[Dict[str, List[str]]] = None) -> Dict:
        """Train the regime detection model"""

        logger.info("Training market regime detection model...")

        # If no labels provided, use unsupervised learning to create synthetic labels
        if labels is None:
            labels = self._generate_synthetic_labels(historical_data)

        all_features = []
        all_labels = []

        # Process each asset's data
        for asset, df in historical_data.items():
            if asset not in labels or len(labels[asset]) != len(df):
                logger.warning(f"Skipping {asset} - mismatched data/labels")
                continue

            features = self.create_regime_features(df)
            if len(features) == 0:
                continue

            # Ensure labels match features length (accounting for lookback periods)
            label_array = np.array(labels[asset])
            min_length = min(len(features), len(label_array))
            features = features[:min_length]
            label_array = label_array[:min_length]

            all_features.append(features)
            all_labels.append(label_array)

        if not all_features:
            return {'error': 'No valid training data'}

        # Combine all assets
        X = np.vstack(all_features)
        y = np.concatenate(all_labels)

        # Encode string labels to integers
        unique_labels = list(self.regime_definitions.keys())
        label_to_int = {label: i for i, label in enumerate(unique_labels)}
        y_encoded = np.array([label_to_int.get(label, 0) for label in y])

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.regime_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )

        self.regime_model.fit(X_train_scaled, y_train)

        # Evaluate model
        train_score = self.regime_model.score(X_train_scaled, y_train)
        test_score = self.regime_model.score(X_test_scaled, y_test)

        y_pred = self.regime_model.predict(X_test_scaled)

        # Save model
        self.save_model()

        logger.info(f"Regime model trained - Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")

        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'feature_importance': dict(zip(range(X.shape[1]), self.regime_model.feature_importances_)),
            'classification_report': classification_report(y_test, y_pred, target_names=unique_labels[:len(np.unique(y_encoded))])
        }

    def _generate_synthetic_labels(self, historical_data: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
        """Generate synthetic regime labels using rule-based heuristics"""

        labels = {}

        for asset, df in historical_data.items():
            asset_labels = []

            # Calculate rolling metrics for each period
            for i in range(len(df)):
                if i < 50:  # Need some history
                    asset_labels.append('sideways')
                    continue

                window = df.iloc[max(0, i-50):i+1]

                # Calculate trend and volatility
                trend = (window['close'].iloc[-1] - window['close'].iloc[0]) / window['close'].iloc[0]
                volatility = window['close'].pct_change().std()

                # Classify regime
                if abs(trend) > 0.05 and volatility < 0.02:
                    regime = 'strong_bull' if trend > 0 else 'strong_bear'
                elif abs(trend) > 0.02:
                    regime = 'bull' if trend > 0 else 'bear'
                elif volatility > 0.04:
                    regime = 'volatile'
                elif abs(trend) < 0.005:
                    regime = 'sideways'
                else:
                    regime = 'breakout' if abs(trend) > 0.015 else 'sideways'

                asset_labels.append(regime)

            labels[asset] = asset_labels

        return labels

    def detect_regime(self, market_data: pd.DataFrame, asset_symbol: str = "current") -> Dict:
        """Detect current market regime"""

        if self.regime_model is None:
            # Fallback to rule-based detection
            return self._rule_based_regime_detection(market_data)

        # Create features for current market data
        features = self.create_regime_features(market_data)

        if len(features) == 0:
            return {'error': 'Could not create features from market data'}

        # Scale features
        features_scaled = self.scaler.transform(features)

        # Get latest feature vector
        latest_features = features_scaled[-1:].reshape(1, -1)

        # Predict regime
        regime_int = self.regime_model.predict(latest_features)[0]
        regime_proba = self.regime_model.predict_proba(latest_features)[0]

        # Convert back to regime name
        int_to_label = {i: label for i, label in enumerate(self.regime_definitions.keys())}
        detected_regime = int_to_label.get(regime_int, 'unknown')
        confidence = float(regime_proba[regime_int])

        # Get regime details
        regime_info = self.regime_definitions.get(detected_regime, {})

        # Calculate additional metrics
        trend = market_data['close'].pct_change(20).iloc[-1] if len(market_data) > 20 else 0
        volatility = market_data['close'].pct_change().rolling(20).std().iloc[-1] if len(market_data) > 20 else 0

        # Store in history
        regime_record = {
            'timestamp': datetime.now(),
            'asset': asset_symbol,
            'regime': detected_regime,
            'confidence': confidence,
            'trend': float(trend),
            'volatility': float(volatility),
            'additional_metrics': {
                'trend_strength': abs(trend),
                'volatility_level': volatility,
                'regime_description': regime_info.get('description', 'Unknown regime')
            }
        }

        self.regime_history.append(regime_record)

        # Keep only recent history
        if len(self.regime_history) > 10000:
            self.regime_history = self.regime_history[-5000:]

        return regime_record

    def _rule_based_regime_detection(self, market_data: pd.DataFrame) -> Dict:
        """Fallback rule-based regime detection when no ML model is available"""

        if len(market_data) < 20:
            return {
                'regime': 'unknown',
                'confidence': 0,
                'method': 'insufficient_data'
            }

        # Calculate key metrics
        recent_trend = market_data['close'].pct_change(20).iloc[-1]
        volatility = market_data['close'].pct_change().rolling(20).std().iloc[-1]

        # Determine regime based on rules
        if abs(recent_trend) > 0.03 and volatility < 0.02:
            regime = 'strong_bull' if recent_trend > 0 else 'strong_bear'
            confidence = 0.85
        elif abs(recent_trend) > 0.015:
            regime = 'bull' if recent_trend > 0 else 'bear'
            confidence = 0.75
        elif volatility > 0.04:
            regime = 'volatile'
            confidence = 0.8
        elif abs(recent_trend) < 0.005:
            regime = 'sideways'
            confidence = 0.7
        else:
            regime = 'breakout'
            confidence = 0.65

        return {
            'regime': regime,
            'confidence': confidence,
            'trend': float(recent_trend),
            'volatility': float(volatility),
            'method': 'rule_based',
            'description': self.regime_definitions.get(regime, {}).get('description', 'Unknown regime')
        }

    def get_regime_transition_probability(self, from_regime: str, to_regime: str) -> float:
        """Calculate probability of transitioning from one regime to another"""

        if not self.regime_history:
            return 0.0

        # Count transitions
        transitions = 0
        total_from_regime = 0

        prev_regime = None
        for record in self.regime_history:
            current_regime = record['regime']

            if prev_regime == from_regime:
                total_from_regime += 1
                if current_regime == to_regime:
                    transitions += 1

            prev_regime = current_regime

        if total_from_regime == 0:
            return 0.0

        return transitions / total_from_regime

    def predict_regime_transition(self, current_regime: str, steps_ahead: int = 1) -> Dict:
        """Predict likely regime transitions"""

        possible_transitions = {}
        total_probability = 0

        for target_regime in self.regime_definitions.keys():
            if target_regime != current_regime:
                prob = self.get_regime_transition_probability(current_regime, target_regime)
                if prob > 0:
                    possible_transitions[target_regime] = prob
                    total_probability += prob

        # Normalize probabilities
        if total_probability > 0:
            possible_transitions = {k: v/total_probability for k, v in possible_transitions.items()}

        # Sort by probability
        sorted_transitions = sorted(possible_transitions.items(), key=lambda x: x[1], reverse=True)

        return {
            'current_regime': current_regime,
            'predicted_transitions': dict(sorted_transitions[:5]),  # Top 5 most likely
            'most_likely_next': sorted_transitions[0][0] if sorted_transitions else None,
            'confidence': sorted_transitions[0][1] if sorted_transitions else 0
        }

    def get_regime_statistics(self) -> Dict:
        """Get comprehensive regime statistics"""

        if not self.regime_history:
            return {'error': 'No regime history available'}

        # Count regime occurrences
        regime_counts = {}
        for record in self.regime_history:
            regime = record['regime']
            regime_counts[regime] = regime_counts.get(regime, 0) + 1

        total_records = len(self.regime_history)

        # Calculate percentages
        regime_percentages = {k: v/total_records for k, v in regime_counts.items()}

        # Calculate average duration for each regime
        regime_durations = self._calculate_regime_durations()

        # Calculate regime performance metrics
        regime_performance = self._calculate_regime_performance()

        return {
            'total_observations': total_records,
            'regime_distribution': regime_percentages,
            'most_common_regime': max(regime_counts.items(), key=lambda x: x[1])[0],
            'regime_durations': regime_durations,
            'regime_performance': regime_performance,
            'regime_transitions': self._analyze_regime_transitions()
        }

    def _calculate_regime_durations(self) -> Dict:
        """Calculate average duration for each regime"""

        durations = {}
        current_regime = None
        current_start = None

        for record in self.regime_history:
            regime = record['regime']
            timestamp = record['timestamp']

            if regime != current_regime:
                # Record previous regime duration
                if current_regime and current_start:
                    duration = (timestamp - current_start).total_seconds() / 3600  # hours
                    if current_regime not in durations:
                        durations[current_regime] = []
                    durations[current_regime].append(duration)

                # Start new regime
                current_regime = regime
                current_start = timestamp

        # Calculate averages
        avg_durations = {}
        for regime, dur_list in durations.items():
            if dur_list:
                avg_durations[regime] = {
                    'average_hours': np.mean(dur_list),
                    'median_hours': np.median(dur_list),
                    'min_hours': min(dur_list),
                    'max_hours': max(dur_list)
                }

        return avg_durations

    def _calculate_regime_performance(self) -> Dict:
        """Calculate performance metrics for each regime"""

        performance = {}

        for record in self.regime_history:
            regime = record['regime']

            if regime not in performance:
                performance[regime] = {
                    'trend_sum': 0,
                    'volatility_sum': 0,
                    'count': 0,
                    'positive_trends': 0
                }

            perf = performance[regime]
            perf['trend_sum'] += record.get('trend', 0)
            perf['volatility_sum'] += record.get('volatility', 0)
            perf['count'] += 1

            if record.get('trend', 0) > 0:
                perf['positive_trends'] += 1

        # Calculate averages
        for regime, perf in performance.items():
            if perf['count'] > 0:
                perf['avg_trend'] = perf['trend_sum'] / perf['count']
                perf['avg_volatility'] = perf['volatility_sum'] / perf['count']
                perf['positive_trend_ratio'] = perf['positive_trends'] / perf['count']

        return performance

    def _analyze_regime_transitions(self) -> Dict:
        """Analyze regime transition patterns"""

        transitions = {}
        prev_regime = None

        for record in self.regime_history:
            current_regime = record['regime']

            if prev_regime:
                transition_key = f"{prev_regime}_to_{current_regime}"
                transitions[transition_key] = transitions.get(transition_key, 0) + 1

            prev_regime = current_regime

        # Convert to probabilities
        from_regime_counts = {}
        for transition, count in transitions.items():
            from_regime = transition.split('_to_')[0]
            from_regime_counts[from_regime] = from_regime_counts.get(from_regime, 0) + count

        transition_probs = {}
        for transition, count in transitions.items():
            from_regime = transition.split('_to_')[0]
            if from_regime in from_regime_counts:
                transition_probs[transition] = count / from_regime_counts[from_regime]

        return {
            'transition_counts': transitions,
            'transition_probabilities': transition_probs,
            'most_common_transition': max(transitions.items(), key=lambda x: x[1]) if transitions else None
        }


class AdaptiveRegimeStrategy:
    """Strategy that adapts based on detected market regime"""

    def __init__(self, regime_detector: MarketRegimeDetector):
        self.regime_detector = regime_detector
        self.regime_strategies = self._define_regime_strategies()

    def _define_regime_strategies(self) -> Dict:
        """Define optimal strategies for each market regime"""

        return {
            'strong_bull': {
                'position_size_multiplier': 1.3,
                'stop_loss_pct': 0.015,  # Wider stops in strong trends
                'take_profit_multiplier': 2.5,
                'max_hold_time': 168,  # Up to 1 week
                'entry_confidence_threshold': 0.75,
                'description': 'Aggressive long positions with wide stops'
            },
            'bull': {
                'position_size_multiplier': 1.1,
                'stop_loss_pct': 0.02,
                'take_profit_multiplier': 2.0,
                'max_hold_time': 96,  # Up to 4 days
                'entry_confidence_threshold': 0.7,
                'description': 'Moderate long bias with standard stops'
            },
            'strong_bear': {
                'position_size_multiplier': 1.3,
                'stop_loss_pct': 0.015,
                'take_profit_multiplier': 2.5,
                'max_hold_time': 168,
                'entry_confidence_threshold': 0.75,
                'description': 'Aggressive short positions with wide stops'
            },
            'bear': {
                'position_size_multiplier': 1.1,
                'stop_loss_pct': 0.02,
                'take_profit_multiplier': 2.0,
                'max_hold_time': 96,
                'entry_confidence_threshold': 0.7,
                'description': 'Moderate short bias with standard stops'
            },
            'sideways': {
                'position_size_multiplier': 0.7,
                'stop_loss_pct': 0.008,  # Tighter stops in ranging markets
                'take_profit_multiplier': 1.2,
                'max_hold_time': 24,  # Max 1 day
                'entry_confidence_threshold': 0.85,  # Higher confidence required
                'description': 'Conservative approach with tight stops and quick exits'
            },
            'volatile': {
                'position_size_multiplier': 0.6,
                'stop_loss_pct': 0.025,  # Wider stops for volatility
                'take_profit_multiplier': 1.8,
                'max_hold_time': 48,  # Max 2 days
                'entry_confidence_threshold': 0.9,  # Very high confidence required
                'description': 'Very conservative with wide stops and high conviction'
            },
            'breakout': {
                'position_size_multiplier': 1.2,
                'stop_loss_pct': 0.012,
                'take_profit_multiplier': 3.0,  # Higher targets for breakouts
                'max_hold_time': 120,  # Up to 5 days
                'entry_confidence_threshold': 0.8,
                'description': 'Aggressive breakout trading with higher targets'
            }
        }

    def get_regime_strategy(self, market_data: pd.DataFrame, asset_symbol: str = "current") -> Dict:
        """Get optimal strategy for current market regime"""

        # Detect current regime
        regime_info = self.regime_detector.detect_regime(market_data, asset_symbol)

        current_regime = regime_info.get('regime', 'sideways')

        # Get regime-specific strategy
        strategy = self.regime_strategies.get(current_regime, self.regime_strategies['sideways'])

        # Adjust based on regime confidence
        confidence = regime_info.get('confidence', 0)
        if confidence < 0.7:
            # Reduce aggressiveness if regime detection is uncertain
            strategy = strategy.copy()
            strategy['position_size_multiplier'] *= 0.8
            strategy['entry_confidence_threshold'] *= 1.1

        return {
            'regime': current_regime,
            'regime_confidence': confidence,
            'strategy': strategy,
            'recommended_actions': self._get_regime_actions(current_regime),
            'risk_adjustments': self._get_risk_adjustments(current_regime)
        }

    def _get_regime_actions(self, regime: str) -> List[str]:
        """Get recommended actions for current regime"""

        actions = {
            'strong_bull': [
                'Favor long positions with wider stop losses',
                'Consider increasing position sizes',
                'Look for continuation patterns',
                'Use trailing stops to lock in profits'
            ],
            'bull': [
                'Maintain bullish bias',
                'Enter on pullbacks',
                'Use standard position sizing',
                'Monitor for trend continuation'
            ],
            'strong_bear': [
                'Favor short positions with wider stop losses',
                'Consider increasing position sizes',
                'Look for continuation patterns',
                'Use trailing stops to lock in profits'
            ],
            'bear': [
                'Maintain bearish bias',
                'Enter on rallies',
                'Use standard position sizing',
                'Monitor for trend continuation'
            ],
            'sideways': [
                'Reduce position sizes',
                'Use very tight stop losses',
                'Focus on high-probability setups only',
                'Consider range trading strategies',
                'Exit positions quickly'
            ],
            'volatile': [
                'Significantly reduce position sizes',
                'Use wide stop losses',
                'Only trade with very high conviction',
                'Consider staying out of the market',
                'Monitor volatility indicators closely'
            ],
            'breakout': [
                'Increase position sizes for confirmed breakouts',
                'Use wider stops initially',
                'Set higher profit targets',
                'Monitor volume confirmation',
                'Be prepared for strong moves'
            ]
        }

        return actions.get(regime, ['Monitor market conditions carefully'])

    def _get_risk_adjustments(self, regime: str) -> Dict:
        """Get risk management adjustments for current regime"""

        adjustments = {
            'strong_bull': {
                'portfolio_risk_limit': 1.2,  # 20% increase
                'max_single_position': 0.15,  # 15% of portfolio
                'correlation_sensitivity': 0.7  # Less sensitive to correlations
            },
            'bull': {
                'portfolio_risk_limit': 1.0,
                'max_single_position': 0.12,
                'correlation_sensitivity': 0.8
            },
            'strong_bear': {
                'portfolio_risk_limit': 1.2,
                'max_single_position': 0.15,
                'correlation_sensitivity': 0.7
            },
            'bear': {
                'portfolio_risk_limit': 1.0,
                'max_single_position': 0.12,
                'correlation_sensitivity': 0.8
            },
            'sideways': {
                'portfolio_risk_limit': 0.6,  # 40% reduction
                'max_single_position': 0.06,  # 6% of portfolio
                'correlation_sensitivity': 1.0  # Very sensitive to correlations
            },
            'volatile': {
                'portfolio_risk_limit': 0.4,  # 60% reduction
                'max_single_position': 0.04,  # 4% of portfolio
                'correlation_sensitivity': 1.2  # Extremely sensitive
            },
            'breakout': {
                'portfolio_risk_limit': 1.1,
                'max_single_position': 0.10,
                'correlation_sensitivity': 0.9
            }
        }

        return adjustments.get(regime, adjustments['sideways'])


if __name__ == "__main__":
    # Example usage
    detector = MarketRegimeDetector()
    adaptive_strategy = AdaptiveRegimeStrategy(detector)

    print("AI Market Regime Detection initialized!")
    print("Ready to detect market regimes and adapt strategies accordingly")
