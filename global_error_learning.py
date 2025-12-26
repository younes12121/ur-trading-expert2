"""
Global Error Learning System for Professional Trading Bot
Integrates machine learning-based error prediction across all bot components
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import hashlib
import threading

# Optional ML imports - bot will work without them
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. ML features will be disabled.")

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

logger = logging.getLogger(__name__)

class GlobalErrorLearningManager:
    """Global ML-based error prediction and avoidance system for entire bot"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.model_path = os.path.join(os.path.dirname(__file__), "global_error_learning_model.pkl")
        self.error_history = []
        if SKLEARN_AVAILABLE:
            self.scaler = StandardScaler()
            self.label_encoder = LabelEncoder()
        else:
            self.scaler = None
            self.label_encoder = None
        self.model = None

        # Component-specific feature columns
        self.component_features = {
            'telegram_bot': [
                'command_type', 'user_tier', 'time_of_day', 'day_of_week',
                'system_load', 'memory_usage', 'api_calls_today', 'error_streak'
            ],
            'execution_manager': [
                'operation_type', 'asset_symbol', 'position_size', 'market_volatility',
                'time_of_day', 'spread_width', 'liquidity_score', 'error_streak'
            ],
            'risk_manager': [
                'operation_type', 'balance', 'confidence_level', 'market_regime',
                'volatility', 'correlation_risk', 'drawdown_pct', 'error_streak'
            ],
            'data_fetcher': [
                'operation_type', 'symbol', 'timeframe', 'api_endpoint',
                'rate_limit_status', 'network_latency', 'cache_hit_rate', 'error_streak'
            ],
            'backtest_engine': [
                'operation_type', 'strategy_type', 'timeframe', 'data_points',
                'memory_usage', 'computation_time', 'parallel_jobs', 'error_streak'
            ],
            'signal_generator': [
                'generator_type', 'asset_symbol', 'timeframe', 'market_condition',
                'data_quality', 'computation_load', 'cache_status', 'error_streak'
            ]
        }

        self.error_patterns = {}
        self.adaptation_rules = {}
        self.performance_metrics = {
            'total_operations': 0,
            'errors_avoided': 0,
            'successful_predictions': 0,
            'false_positives': 0,
            'learning_progress': 0.0
        }

        self._load_or_create_model()
        logger.info("[GLOBAL_ERROR_LEARNING] Global Error Learning Manager initialized")

    def _load_or_create_model(self):
        """Load existing model or create new one"""
        if not SKLEARN_AVAILABLE:
            logger.warning("[GLOBAL_ERROR_LEARNING] scikit-learn not available. ML features disabled.")
            return
            
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoder = model_data['label_encoder']
                self.error_history = model_data.get('error_history', [])
                self.error_patterns = model_data.get('error_patterns', {})
                self.performance_metrics = model_data.get('performance_metrics', self.performance_metrics)
                logger.info("[GLOBAL_ERROR_LEARNING] Loaded existing global error learning model")
            else:
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
                logger.info("[GLOBAL_ERROR_LEARNING] Created new global error learning model")
        except Exception as e:
            logger.warning(f"[GLOBAL_ERROR_LEARNING] Failed to load model, creating new: {e}")
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )

    def _extract_features(self, component: str, operation_context: Dict) -> Dict:
        """Extract features for error prediction based on component"""
        now = datetime.now()

        # Common features for all components
        common_features = {
            'time_of_day': now.hour + now.minute / 60.0,
            'day_of_week': now.weekday(),
            'system_load': operation_context.get('system_load', 0.5),
            'memory_usage': operation_context.get('memory_usage', 0.5),
            'error_streak': self._calculate_error_streak(component),
            'time_since_last_error': self._calculate_time_since_last_error(component)
        }

        # Component-specific features
        if component == 'telegram_bot':
            specific_features = {
                'command_type': operation_context.get('command_type', 'unknown'),
                'user_tier': operation_context.get('user_tier', 'free'),
                'api_calls_today': operation_context.get('api_calls_today', 0),
            }
        elif component == 'execution_manager':
            specific_features = {
                'operation_type': operation_context.get('operation_type', 'unknown'),
                'asset_symbol': operation_context.get('asset_symbol', 'unknown'),
                'position_size': operation_context.get('position_size', 1.0),
                'market_volatility': operation_context.get('market_volatility', 0.02),
                'spread_width': operation_context.get('spread_width', 0.0001),
                'liquidity_score': operation_context.get('liquidity_score', 0.8),
            }
        elif component == 'risk_manager':
            specific_features = {
                'operation_type': operation_context.get('operation_type', 'unknown'),
                'balance': operation_context.get('balance', 10000),
                'confidence_level': operation_context.get('confidence_level', 0.5),
                'market_regime': operation_context.get('market_regime', 'neutral'),
                'volatility': operation_context.get('volatility', 0.02),
                'correlation_risk': operation_context.get('correlation_risk', 0.1),
                'drawdown_pct': operation_context.get('drawdown_pct', 0.0),
            }
        elif component == 'data_fetcher':
            specific_features = {
                'operation_type': operation_context.get('operation_type', 'unknown'),
                'symbol': operation_context.get('symbol', 'unknown'),
                'timeframe': operation_context.get('timeframe', '1h'),
                'api_endpoint': operation_context.get('api_endpoint', 'unknown'),
                'rate_limit_status': operation_context.get('rate_limit_status', 0.1),
                'network_latency': operation_context.get('network_latency', 100),
                'cache_hit_rate': operation_context.get('cache_hit_rate', 0.8),
            }
        elif component == 'backtest_engine':
            specific_features = {
                'operation_type': operation_context.get('operation_type', 'unknown'),
                'strategy_type': operation_context.get('strategy_type', 'unknown'),
                'timeframe': operation_context.get('timeframe', '1h'),
                'data_points': operation_context.get('data_points', 1000),
                'computation_time': operation_context.get('computation_time', 60),
                'parallel_jobs': operation_context.get('parallel_jobs', 1),
            }
        elif component == 'signal_generator':
            specific_features = {
                'generator_type': operation_context.get('generator_type', 'unknown'),
                'asset_symbol': operation_context.get('asset_symbol', 'unknown'),
                'timeframe': operation_context.get('timeframe', '1h'),
                'market_condition': operation_context.get('market_condition', 'normal'),
                'data_quality': operation_context.get('data_quality', 0.9),
                'computation_load': operation_context.get('computation_load', 0.5),
                'cache_status': operation_context.get('cache_status', 1),
            }
        else:
            specific_features = {}

        return {**common_features, **specific_features}

    def _calculate_error_streak(self, component: str) -> int:
        """Calculate current error streak for a component"""
        if not self.error_history:
            return 0

        streak = 0
        for entry in reversed(self.error_history[-10:]):  # Check last 10 operations
            if entry.get('component') == component and entry.get('had_error', False):
                streak += 1
            else:
                break

        return streak

    def _calculate_time_since_last_error(self, component: str) -> float:
        """Calculate time in hours since last error for a component"""
        if not self.error_history:
            return 24.0

        last_error = None
        for entry in reversed(self.error_history):
            if entry.get('component') == component and entry.get('had_error', False):
                last_error = entry
                break

        if last_error and 'timestamp' in last_error:
            try:
                last_error_time = datetime.fromisoformat(last_error['timestamp'])
                return (datetime.now() - last_error_time).total_seconds() / 3600.0
            except:
                pass

        return 24.0

    def predict_error_likelihood(self, component: str, operation_context: Dict) -> Dict:
        """Predict the likelihood of an error occurring in a specific component"""
        if not SKLEARN_AVAILABLE or self.model is None or len(self.error_history) < 10:
            return {
                'error_probability': 0.05,  # Conservative default for new components
                'confidence': 0.2,
                'should_attempt': True,
                'alternative_suggestions': [],
                'risk_level': 'low'
            }

        try:
            features = self._extract_features(component, operation_context)
            feature_df = pd.DataFrame([features])

            # Prepare features for prediction
            if hasattr(self.scaler, 'mean_'):  # Check if scaler is fitted
                # Get numerical features only (exclude categorical for now)
                numerical_cols = [col for col in features.keys() if isinstance(features[col], (int, float))]
                feature_scaled = self.scaler.transform(feature_df[numerical_cols])
                X = feature_scaled
            else:
                # Fallback to basic numerical features
                basic_features = ['time_of_day', 'day_of_week', 'system_load', 'memory_usage', 'error_streak']
                X = feature_df[basic_features].values

            # Predict
            error_proba = self.model.predict_proba(X)[0][1]  # Probability of error (class 1)

            # Generate suggestions based on error patterns
            suggestions = self._generate_alternatives(component, operation_context, error_proba)

            # Determine risk level
            if error_proba > 0.7:
                risk_level = 'high'
            elif error_proba > 0.4:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            return {
                'error_probability': float(error_proba),
                'confidence': self._calculate_prediction_confidence(component),
                'should_attempt': error_proba < 0.8,  # Don't attempt if >80% error chance
                'alternative_suggestions': suggestions,
                'risk_level': risk_level,
                'component': component
            }

        except Exception as e:
            logger.warning(f"[GLOBAL_ERROR_LEARNING] Prediction failed for {component}: {e}")
            return {
                'error_probability': 0.1,  # Conservative fallback
                'confidence': 0.1,
                'should_attempt': True,
                'alternative_suggestions': ['Use conservative parameters', 'Enable fallback mode'],
                'risk_level': 'medium',
                'component': component
            }

    def _generate_alternatives(self, component: str, operation_context: Dict, error_proba: float) -> List[str]:
        """Generate alternative approaches to avoid predicted errors"""
        suggestions = []

        if error_proba > 0.6:
            if component == 'telegram_bot':
                suggestions.extend([
                    "Use cached responses",
                    "Limit concurrent users",
                    "Enable circuit breaker mode",
                    "Switch to maintenance mode"
                ])
            elif component == 'execution_manager':
                suggestions.extend([
                    "Use limit orders instead of market",
                    "Reduce position size",
                    "Enable slippage protection",
                    "Delay execution by 30 seconds"
                ])
            elif component == 'risk_manager':
                suggestions.extend([
                    "Use conservative risk limits",
                    "Enable emergency stop mode",
                    "Reduce maximum exposure",
                    "Switch to preservation mode"
                ])
            elif component == 'data_fetcher':
                suggestions.extend([
                    "Use cached data",
                    "Reduce request frequency",
                    "Switch to backup data source",
                    "Enable offline mode"
                ])
            elif component == 'backtest_engine':
                suggestions.extend([
                    "Use simplified strategy",
                    "Reduce data points",
                    "Enable memory optimization",
                    "Use sequential processing"
                ])
            elif component == 'signal_generator':
                suggestions.extend([
                    "Use basic signal logic",
                    "Skip complex calculations",
                    "Use cached signals",
                    "Reduce analysis depth"
                ])

        return suggestions

    def _calculate_prediction_confidence(self, component: str) -> float:
        """Calculate confidence in the error prediction for a component"""
        component_history = [e for e in self.error_history if e.get('component') == component]

        if len(component_history) < 5:
            return 0.2  # Low confidence with little data

        # Simple confidence based on data size and model performance
        base_confidence = min(0.9, len(component_history) / 50.0)
        return base_confidence

    def record_operation_result(self, component: str, operation_context: Dict, had_error: bool,
                              error_details: Optional[str] = None, success_metrics: Optional[Dict] = None,
                              execution_time: Optional[float] = None):
        """Record the result of an operation for learning"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'operation_context': operation_context.copy(),
            'had_error': had_error,
            'error_details': error_details,
            'success_metrics': success_metrics or {},
            'execution_time': execution_time,
            'features': self._extract_features(component, operation_context)
        }

        self.error_history.append(entry)
        self.performance_metrics['total_operations'] += 1

        # Keep only last 2000 entries to prevent memory issues
        if len(self.error_history) > 2000:
            self.error_history = self.error_history[-2000:]

        # Update error patterns
        self._update_error_patterns(entry)

        # Retrain model periodically
        if len(self.error_history) % 100 == 0:  # Retrain every 100 operations
            self._retrain_model()

        # Save model periodically
        if len(self.error_history) % 200 == 0:  # Save every 200 operations
            self._save_model()

        # Update performance metrics
        if had_error:
            if operation_context.get('error_predicted', False):
                self.performance_metrics['successful_predictions'] += 1
        else:
            if operation_context.get('error_predicted', False):
                self.performance_metrics['false_positives'] += 1
            elif operation_context.get('error_probability', 0) > 0.5:
                self.performance_metrics['errors_avoided'] += 1

        logger.info(f"[GLOBAL_ERROR_LEARNING] Recorded {component} operation result: error={had_error}")

    def _update_error_patterns(self, entry: Dict):
        """Update error pattern knowledge"""
        component = entry['component']
        had_error = entry['had_error']

        if component not in self.error_patterns:
            self.error_patterns[component] = {
                'total_operations': 0,
                'errors': 0,
                'error_rate': 0.0,
                'common_error_times': [],
                'avg_execution_time': 0,
                'error_recovery_time': [],
                'performance_trends': []
            }

        pattern = self.error_patterns[component]
        pattern['total_operations'] += 1

        if had_error:
            pattern['errors'] += 1
            # Track error contexts
            timestamp = datetime.fromisoformat(entry['timestamp'])
            pattern['common_error_times'].append(timestamp.hour)

            # Keep only recent patterns
            pattern['common_error_times'] = pattern['common_error_times'][-20:]

        pattern['error_rate'] = pattern['errors'] / pattern['total_operations']

        # Update execution time tracking
        if entry.get('execution_time'):
            exec_time = entry['execution_time']
            pattern['avg_execution_time'] = (
                (pattern['avg_execution_time'] * (pattern['total_operations'] - 1)) + exec_time
            ) / pattern['total_operations']

    def _retrain_model(self):
        """Retrain the error prediction model"""
        if not SKLEARN_AVAILABLE:
            return
            
        if len(self.error_history) < 30:
            logger.info("[GLOBAL_ERROR_LEARNING] Not enough data for retraining")
            return

        try:
            # Prepare training data
            df = pd.DataFrame([
                {**entry['features'], 'had_error': entry['had_error']}
                for entry in self.error_history
            ])

            if len(df) < 30 or df['had_error'].nunique() < 2:
                logger.warning("[GLOBAL_ERROR_LEARNING] Insufficient data diversity for retraining")
                return

            # Prepare features (focus on numerical features)
            numerical_cols = [col for col in df.columns if col != 'had_error' and df[col].dtype in ['int64', 'float64']]
            X = df[numerical_cols]
            y = df['had_error'].astype(int)

            # Scale features
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y
            )

            # Train model
            self.model.fit(X_train, y_train)

            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)

            # Update learning progress
            self.performance_metrics['learning_progress'] = min(1.0, len(self.error_history) / 500.0)

            logger.info(f"[GLOBAL_ERROR_LEARNING] Model retrained - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")

        except Exception as e:
            logger.error(f"[GLOBAL_ERROR_LEARNING] Model retraining failed: {e}")

    def _save_model(self):
        """Save the model and learning data"""
        if not SKLEARN_AVAILABLE:
            return
            
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'error_history': self.error_history[-1000:],  # Save last 1000 entries
                'error_patterns': self.error_patterns,
                'performance_metrics': self.performance_metrics,
                'component_features': self.component_features,
                'last_updated': datetime.now().isoformat()
            }

            joblib.dump(model_data, self.model_path)
            logger.debug("[GLOBAL_ERROR_LEARNING] Global error learning model saved successfully")

        except Exception as e:
            logger.warning(f"[GLOBAL_ERROR_LEARNING] Failed to save global model: {e}")

    def get_error_insights(self, component: Optional[str] = None) -> Dict:
        """Get error insights for a specific component or overall system"""
        if component:
            component_patterns = {component: self.error_patterns.get(component, {})}
            component_history = [e for e in self.error_history if e.get('component') == component]
        else:
            component_patterns = self.error_patterns
            component_history = self.error_history

        return {
            'total_operations': len(component_history),
            'error_patterns': component_patterns,
            'performance_metrics': self.performance_metrics,
            'model_trained': self.model is not None,
            'training_data_size': len(self.error_history),
            'learning_progress': self.performance_metrics['learning_progress'],
            'recent_error_rate': self._calculate_recent_error_rate(component),
            'most_problematic_components': self._get_most_problematic_components(),
            'system_health_score': self._calculate_system_health_score()
        }

    def _calculate_recent_error_rate(self, component: Optional[str] = None) -> float:
        """Calculate error rate in recent operations"""
        if not self.error_history:
            return 0.0

        # Filter by component if specified
        history = [e for e in self.error_history[-100:] if component is None or e.get('component') == component]
        if not history:
            return 0.0

        errors = sum(1 for entry in history if entry.get('had_error', False))
        return errors / len(history)

    def _get_most_problematic_components(self) -> List[Dict]:
        """Get components with highest error rates"""
        component_stats = []

        for comp, pattern in self.error_patterns.items():
            if pattern['total_operations'] >= 5:  # Only include components with enough data
                component_stats.append({
                    'component': comp,
                    'error_rate': pattern['error_rate'],
                    'total_operations': pattern['total_operations'],
                    'avg_execution_time': pattern.get('avg_execution_time', 0),
                    'recent_errors': len(pattern.get('common_error_times', []))
                })

        # Sort by error rate descending
        return sorted(component_stats, key=lambda x: x['error_rate'], reverse=True)[:5]

    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        if not self.error_history:
            return 100.0

        # Factors affecting health
        recent_error_rate = self._calculate_recent_error_rate()
        learning_progress = self.performance_metrics['learning_progress']
        total_operations = self.performance_metrics['total_operations']

        # Error rate penalty (0-40 points)
        error_penalty = recent_error_rate * 40

        # Learning bonus (0-30 points)
        learning_bonus = learning_progress * 30

        # Experience bonus (0-30 points, max at 1000 operations)
        experience_bonus = min(30, total_operations / 1000 * 30)

        health_score = 100 - error_penalty + learning_bonus + experience_bonus
        return max(0, min(100, health_score))

    def get_adaptive_recommendations(self, component: str, operation_context: Dict) -> Dict:
        """Get adaptive recommendations for a specific operation"""
        error_prediction = self.predict_error_likelihood(component, operation_context)

        recommendations = {
            'risk_assessment': error_prediction['risk_level'],
            'confidence_score': error_prediction['confidence'],
            'suggested_actions': [],
            'fallback_strategies': [],
            'monitoring_level': 'normal'
        }

        # Add specific recommendations based on risk level
        if error_prediction['risk_level'] == 'high':
            recommendations['suggested_actions'].extend([
                'Enable transaction logging',
                'Prepare rollback procedures',
                'Alert system administrators',
                'Use circuit breaker pattern'
            ])
            recommendations['fallback_strategies'].extend([
                'Switch to read-only mode',
                'Use cached data',
                'Defer non-critical operations'
            ])
            recommendations['monitoring_level'] = 'critical'

        elif error_prediction['risk_level'] == 'medium':
            recommendations['suggested_actions'].extend([
                'Increase logging verbosity',
                'Enable performance monitoring'
            ])
            recommendations['fallback_strategies'].extend([
                'Use backup systems',
                'Implement retry logic'
            ])
            recommendations['monitoring_level'] = 'elevated'

        return recommendations

# Global instance
global_error_manager = GlobalErrorLearningManager()

def predict_error(component: str, operation_context: Dict) -> Dict:
    """Convenience function to predict errors for any component"""
    return global_error_manager.predict_error_likelihood(component, operation_context)

def record_error(component: str, operation_context: Dict, had_error: bool,
                error_details: Optional[str] = None, success_metrics: Optional[Dict] = None,
                execution_time: Optional[float] = None):
    """Convenience function to record operation results"""
    return global_error_manager.record_operation_result(
        component, operation_context, had_error, error_details, success_metrics, execution_time
    )

def get_error_insights(component: Optional[str] = None) -> Dict:
    """Convenience function to get error insights"""
    return global_error_manager.get_error_insights(component)

def get_adaptive_recommendations(component: str, operation_context: Dict) -> Dict:
    """Convenience function to get adaptive recommendations"""
    return global_error_manager.get_adaptive_recommendations(component, operation_context)
