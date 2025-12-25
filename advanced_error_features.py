"""
ADVANCED ERROR LEARNING FEATURES
Anomaly Detection, Predictive Maintenance, and Advanced Analytics
"""

import sys
import os
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from scipy import stats
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from global_error_learning import global_error_manager, get_error_insights

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Advanced anomaly detection for error patterns"""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.anomaly_history = deque(maxlen=1000)

    def train(self, data: pd.DataFrame):
        """Train the anomaly detection model"""
        try:
            if len(data) < 10:
                logger.warning("[ANOMALY] Insufficient data for training")
                return False

            # Prepare features for anomaly detection
            features = self._extract_anomaly_features(data)
            if features.empty:
                return False

            # Scale features
            scaled_features = self.scaler.fit_transform(features)

            # Train isolation forest
            self.isolation_forest.fit(scaled_features)
            self.is_trained = True

            logger.info(f"[ANOMALY] Trained on {len(features)} samples")
            return True

        except Exception as e:
            logger.error(f"[ANOMALY] Training failed: {e}")
            return False

    def detect_anomalies(self, data: pd.DataFrame) -> List[Dict]:
        """Detect anomalies in the data"""
        if not self.is_trained:
            return []

        try:
            features = self._extract_anomaly_features(data)
            if features.empty:
                return []

            scaled_features = self.scaler.transform(features)

            # Predict anomalies (-1 for anomaly, 1 for normal)
            predictions = self.isolation_forest.predict(scaled_features)
            scores = self.isolation_forest.decision_function(scaled_features)

            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly detected
                    anomaly = {
                        'index': i,
                        'timestamp': data.index[i] if hasattr(data, 'index') else datetime.now(),
                        'anomaly_score': float(score),
                        'confidence': float(abs(score)),
                        'features': features.iloc[i].to_dict(),
                        'severity': self._calculate_severity(score)
                    }
                    anomalies.append(anomaly)
                    self.anomaly_history.append(anomaly)

            return anomalies

        except Exception as e:
            logger.error(f"[ANOMALY] Detection failed: {e}")
            return []

    def _extract_anomaly_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for anomaly detection"""
        features = pd.DataFrame()

        try:
            # Time-based features
            if hasattr(data, 'index') and isinstance(data.index, pd.DatetimeIndex):
                features['hour'] = data.index.hour
                features['day_of_week'] = data.index.dayofweek
                features['is_weekend'] = (data.index.dayofweek >= 5).astype(int)

            # Error pattern features
            if 'had_error' in data.columns:
                features['error_rate'] = data['had_error'].rolling(window=10, min_periods=1).mean()
                features['error_streak'] = data['had_error'].groupby(
                    (data['had_error'] != data['had_error'].shift()).cumsum()
                ).cumsum()

            # Performance features
            if 'execution_time' in data.columns:
                features['execution_time'] = data['execution_time']
                features['time_zscore'] = stats.zscore(data['execution_time'].fillna(0))

            # Component-specific features
            if 'component' in data.columns:
                # One-hot encode components (simplified)
                component_dummies = pd.get_dummies(data['component'], prefix='component')
                features = pd.concat([features, component_dummies], axis=1)

            # Operation type features
            if 'operation_type' in data.columns:
                operation_dummies = pd.get_dummies(data['operation_type'], prefix='operation')
                features = pd.concat([features, operation_dummies], axis=1)

            return features.fillna(0)

        except Exception as e:
            logger.error(f"[ANOMALY] Feature extraction failed: {e}")
            return pd.DataFrame()

    def _calculate_severity(self, anomaly_score: float) -> str:
        """Calculate anomaly severity"""
        abs_score = abs(anomaly_score)

        if abs_score > 0.8:
            return 'critical'
        elif abs_score > 0.6:
            return 'high'
        elif abs_score > 0.4:
            return 'medium'
        else:
            return 'low'

class PredictiveMaintenance:
    """Predictive maintenance for system components"""

    def __init__(self):
        self.component_health = {}
        self.failure_predictions = {}
        self.maintenance_schedule = {}
        self.health_history = deque(maxlen=5000)

    def update_component_health(self, component: str, metrics: Dict):
        """Update health metrics for a component"""
        if component not in self.component_health:
            self.component_health[component] = {
                'health_score': 100.0,
                'last_updated': datetime.now(),
                'failure_probability': 0.0,
                'maintenance_due': None,
                'anomaly_count': 0
            }

        health = self.component_health[component]

        # Update health score based on metrics
        health_score = self._calculate_health_score(component, metrics)
        health['health_score'] = health_score
        health['last_updated'] = datetime.now()

        # Predict failure probability
        failure_prob = self._predict_failure_probability(component, metrics)
        health['failure_probability'] = failure_prob

        # Schedule maintenance if needed
        if health_score < 70.0 or failure_prob > 0.3:
            self._schedule_maintenance(component, health_score, failure_prob)

        # Store in history
        self.health_history.append({
            'timestamp': datetime.now(),
            'component': component,
            'health_score': health_score,
            'failure_probability': failure_prob,
            'metrics': metrics
        })

    def _calculate_health_score(self, component: str, metrics: Dict) -> float:
        """Calculate health score based on metrics"""
        base_score = 100.0
        penalties = []

        # Error rate penalty
        if 'error_rate' in metrics:
            error_rate = metrics['error_rate']
            if error_rate > 0.2:
                penalties.append(min(error_rate * 200, 40))  # Max 40 points penalty

        # Performance penalty
        if 'avg_execution_time' in metrics:
            exec_time = metrics['avg_execution_time']
            if exec_time > 10.0:  # More than 10 seconds
                penalties.append(min((exec_time - 10) * 2, 20))

        # Resource usage penalty
        if 'memory_usage' in metrics:
            memory_usage = metrics['memory_usage']
            if memory_usage > 0.9:  # Over 90%
                penalties.append((memory_usage - 0.9) * 100)

        # Apply penalties
        for penalty in penalties:
            base_score -= penalty

        return max(0.0, min(100.0, base_score))

    def _predict_failure_probability(self, component: str, metrics: Dict) -> float:
        """Predict failure probability using historical patterns"""
        # Get historical data for this component
        component_history = [h for h in self.health_history if h['component'] == component]

        if len(component_history) < 5:
            return 0.05  # Default low probability with little data

        # Analyze trends
        recent_scores = [h['health_score'] for h in component_history[-10:]]
        trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]

        # Calculate failure probability based on trend and current health
        current_health = metrics.get('health_score', 100.0)

        # Rapid decline increases failure probability
        if trend < -2.0:  # Health declining by more than 2 points per measurement
            base_prob = 0.4
        elif trend < -1.0:
            base_prob = 0.2
        elif trend < 0:
            base_prob = 0.1
        else:
            base_prob = 0.05

        # Low health score increases probability
        if current_health < 50:
            base_prob *= 2.0
        elif current_health < 70:
            base_prob *= 1.5

        return min(base_prob, 0.9)  # Cap at 90%

    def _schedule_maintenance(self, component: str, health_score: float, failure_prob: float):
        """Schedule maintenance based on health metrics"""
        if health_score < 50 or failure_prob > 0.5:
            urgency = 'critical'
            due_date = datetime.now() + timedelta(hours=1)
        elif health_score < 70 or failure_prob > 0.3:
            urgency = 'high'
            due_date = datetime.now() + timedelta(hours=24)
        else:
            urgency = 'medium'
            due_date = datetime.now() + timedelta(days=7)

        self.maintenance_schedule[component] = {
            'due_date': due_date,
            'urgency': urgency,
            'reason': f'Health: {health_score:.1f}, Failure Risk: {failure_prob:.1%}',
            'scheduled_at': datetime.now()
        }

    def get_maintenance_schedule(self) -> Dict:
        """Get current maintenance schedule"""
        return dict(self.maintenance_schedule)

    def get_component_health(self, component: str = None) -> Dict:
        """Get health status for component(s)"""
        if component:
            return self.component_health.get(component, {})

        return dict(self.component_health)

    def get_failure_predictions(self) -> Dict:
        """Get failure predictions for all components"""
        predictions = {}

        for component, health in self.component_health.items():
            predictions[component] = {
                'failure_probability': health['failure_probability'],
                'predicted_failure_time': self._estimate_failure_time(component),
                'health_score': health['health_score'],
                'last_updated': health['last_updated']
            }

        return predictions

    def _estimate_failure_time(self, component: str) -> Optional[datetime]:
        """Estimate when component might fail"""
        health = self.component_health.get(component, {})
        failure_prob = health.get('failure_probability', 0)

        if failure_prob < 0.1:
            return None  # No imminent failure

        # Estimate time based on current health and failure probability
        health_score = health.get('health_score', 100.0)
        decline_rate = max(0.1, (100.0 - health_score) / 10.0)  # Points per day

        if decline_rate > 0:
            days_to_failure = health_score / decline_rate
            return datetime.now() + timedelta(days=min(days_to_failure, 30))  # Cap at 30 days

        return None

class ErrorPatternAnalyzer:
    """Advanced error pattern analysis and clustering"""

    def __init__(self):
        self.error_clusters = {}
        self.pattern_evolution = {}
        self.correlation_matrix = {}

    def analyze_error_patterns(self, error_data: pd.DataFrame) -> Dict:
        """Analyze error patterns using clustering"""
        try:
            # Prepare data for clustering
            features = self._prepare_clustering_features(error_data)

            if len(features) < 5:
                return {'status': 'insufficient_data'}

            # Perform DBSCAN clustering
            clustering = DBSCAN(eps=0.5, min_samples=3)
            clusters = clustering.fit_predict(features)

            # Analyze clusters
            cluster_analysis = self._analyze_clusters(error_data, clusters)

            # Update pattern evolution
            self._update_pattern_evolution(cluster_analysis)

            return {
                'status': 'success',
                'n_clusters': len(set(clusters)) - (1 if -1 in clusters else 0),  # Exclude noise
                'noise_points': list(clusters).count(-1),
                'cluster_analysis': cluster_analysis,
                'pattern_evolution': self.pattern_evolution
            }

        except Exception as e:
            logger.error(f"[PATTERN_ANALYSIS] Analysis failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def _prepare_clustering_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for clustering"""
        features = []

        for col in data.columns:
            if data[col].dtype in ['int64', 'float64']:
                # Normalize numeric features
                if data[col].std() > 0:
                    features.append((data[col] - data[col].mean()) / data[col].std())
                else:
                    features.append(data[col])

        return np.column_stack(features) if features else np.array([])

    def _analyze_clusters(self, data: pd.DataFrame, clusters: np.ndarray) -> Dict:
        """Analyze characteristics of each cluster"""
        analysis = {}

        unique_clusters = set(clusters)
        unique_clusters.discard(-1)  # Remove noise cluster

        for cluster_id in unique_clusters:
            cluster_mask = clusters == cluster_id
            cluster_data = data[cluster_mask]

            analysis[f'cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'error_rate': cluster_data['had_error'].mean() if 'had_error' in cluster_data.columns else 0,
                'avg_execution_time': cluster_data.get('execution_time', pd.Series()).mean(),
                'common_components': cluster_data.get('component', pd.Series()).mode().tolist(),
                'common_operations': cluster_data.get('operation_type', pd.Series()).mode().tolist(),
                'temporal_pattern': self._analyze_temporal_pattern(cluster_data)
            }

        return analysis

    def _analyze_temporal_pattern(self, cluster_data: pd.DataFrame) -> Dict:
        """Analyze temporal patterns in cluster data"""
        if 'timestamp' not in cluster_data.columns:
            return {}

        try:
            timestamps = pd.to_datetime(cluster_data['timestamp'])

            return {
                'peak_hour': timestamps.dt.hour.mode().iloc[0] if not timestamps.empty else None,
                'peak_day': timestamps.dt.dayofweek.mode().iloc[0] if not timestamps.empty else None,
                'frequency': len(cluster_data) / max(1, (timestamps.max() - timestamps.min()).total_seconds() / 3600)  # per hour
            }
        except:
            return {}

    def _update_pattern_evolution(self, cluster_analysis: Dict):
        """Update pattern evolution tracking"""
        current_time = datetime.now()

        for cluster_name, analysis in cluster_analysis.items():
            if cluster_name not in self.pattern_evolution:
                self.pattern_evolution[cluster_name] = []

            self.pattern_evolution[cluster_name].append({
                'timestamp': current_time,
                'metrics': analysis
            })

            # Keep only last 50 entries per cluster
            if len(self.pattern_evolution[cluster_name]) > 50:
                self.pattern_evolution[cluster_name] = self.pattern_evolution[cluster_name][-50:]

    def detect_correlations(self, error_data: pd.DataFrame) -> Dict:
        """Detect correlations between different error types and conditions"""
        try:
            # Calculate correlation matrix for numeric columns
            numeric_data = error_data.select_dtypes(include=[np.number])
            if len(numeric_data.columns) > 1:
                corr_matrix = numeric_data.corr()
                self.correlation_matrix = corr_matrix.to_dict()

            # Find highly correlated features
            correlations = {}
            if hasattr(self, 'correlation_matrix'):
                for col1 in self.correlation_matrix:
                    for col2 in self.correlation_matrix[col1]:
                        corr_value = abs(self.correlation_matrix[col1][col2])
                        if col1 != col2 and corr_value > 0.7:  # Strong correlation
                            key = f"{col1}_vs_{col2}"
                            correlations[key] = {
                                'correlation': self.correlation_matrix[col1][col2],
                                'strength': 'strong' if corr_value > 0.8 else 'moderate'
                            }

            return {
                'correlation_matrix': self.correlation_matrix,
                'strong_correlations': correlations,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"[PATTERN_ANALYSIS] Correlation detection failed: {e}")
            return {'status': 'error', 'message': str(e)}

class AdvancedErrorAnalytics:
    """Main class for advanced error analytics"""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.predictive_maintenance = PredictiveMaintenance()
        self.pattern_analyzer = ErrorPatternAnalyzer()
        self.analytics_cache = {}
        self.last_update = datetime.now()

    def run_full_analysis(self) -> Dict:
        """Run complete advanced error analysis"""
        try:
            # Get error data
            insights = get_error_insights()
            error_history = global_error_manager.error_history

            if not error_history:
                return {'status': 'no_data', 'message': 'No error history available'}

            # Convert to DataFrame
            error_df = pd.DataFrame([
                {
                    'timestamp': entry.get('timestamp'),
                    'component': entry.get('component', 'unknown'),
                    'operation_type': entry.get('operation_context', {}).get('operation_type', 'unknown'),
                    'had_error': entry.get('had_error', False),
                    'execution_time': entry.get('execution_time', 0),
                    'error_details': entry.get('error_details')
                }
                for entry in error_history[-1000:]  # Last 1000 entries
            ])

            # Train anomaly detector
            self.anomaly_detector.train(error_df)

            # Detect anomalies
            anomalies = self.anomaly_detector.detect_anomalies(error_df)

            # Update predictive maintenance
            for component in insights.get('error_patterns', {}):
                component_data = insights['error_patterns'][component]
                self.predictive_maintenance.update_component_health(component, {
                    'error_rate': component_data.get('error_rate', 0),
                    'avg_execution_time': component_data.get('avg_execution_time', 0),
                    'total_operations': component_data.get('total_operations', 0)
                })

            # Analyze patterns
            pattern_analysis = self.pattern_analyzer.analyze_error_patterns(error_df)

            # Detect correlations
            correlations = self.pattern_analyzer.detect_correlations(error_df)

            # Get maintenance schedule
            maintenance = self.predictive_maintenance.get_maintenance_schedule()

            # Get failure predictions
            failure_predictions = self.predictive_maintenance.get_failure_predictions()

            # Compile results
            analysis_results = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies[-10:],  # Last 10 anomalies
                'maintenance_schedule': maintenance,
                'failure_predictions': failure_predictions,
                'pattern_analysis': pattern_analysis,
                'correlations': correlations,
                'system_health': self.predictive_maintenance.get_component_health(),
                'recommendations': self._generate_recommendations(anomalies, maintenance, failure_predictions)
            }

            self.analytics_cache = analysis_results
            self.last_update = datetime.now()

            return analysis_results

        except Exception as e:
            logger.error(f"[ADVANCED_ANALYTICS] Full analysis failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _generate_recommendations(self, anomalies: List, maintenance: Dict,
                                failure_predictions: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Anomaly-based recommendations
        if anomalies:
            recent_anomalies = [a for a in anomalies if a.get('severity') in ['critical', 'high']]
            if recent_anomalies:
                recommendations.append(
                    f"🔴 CRITICAL: {len(recent_anomalies)} high-severity anomalies detected. "
                    "Immediate investigation required."
                )

        # Maintenance recommendations
        urgent_maintenance = [
            comp for comp, schedule in maintenance.items()
            if schedule.get('urgency') == 'critical'
        ]
        if urgent_maintenance:
            recommendations.append(
                f"🛠️ URGENT: Critical maintenance required for: {', '.join(urgent_maintenance[:3])}"
            )

        # Failure prediction recommendations
        high_risk_components = [
            comp for comp, pred in failure_predictions.items()
            if pred.get('failure_probability', 0) > 0.4
        ]
        if high_risk_components:
            recommendations.append(
                f"⚠️ HIGH RISK: Components at risk of failure: {', '.join(high_risk_components[:3])}"
            )

        # Pattern-based recommendations
        if not recommendations:
            recommendations.append("✅ System operating normally. Continue monitoring.")

        return recommendations

    def get_real_time_insights(self) -> Dict:
        """Get real-time advanced insights"""
        # Return cached results if recent (within 5 minutes)
        if (datetime.now() - self.last_update).total_seconds() < 300:
            return self.analytics_cache

        # Otherwise run fresh analysis
        return self.run_full_analysis()

    def get_anomaly_report(self, hours: int = 24) -> Dict:
        """Get detailed anomaly report"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_anomalies = [
            anomaly for anomaly in self.anomaly_detector.anomaly_history
            if anomaly.get('timestamp', datetime.min) > cutoff_time
        ]

        # Group by severity
        severity_counts = {}
        for anomaly in recent_anomalies:
            severity = anomaly.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Group by component
        component_counts = {}
        for anomaly in recent_anomalies:
            component = anomaly.get('component', 'unknown')
            component_counts[component] = component_counts.get(component, 0) + 1

        return {
            'total_anomalies': len(recent_anomalies),
            'severity_breakdown': severity_counts,
            'component_breakdown': component_counts,
            'time_period_hours': hours,
            'anomalies': recent_anomalies[-20:]  # Last 20 anomalies
        }

# Global advanced analytics instance
advanced_analytics = AdvancedErrorAnalytics()

def get_advanced_insights():
    """Convenience function for advanced insights"""
    return advanced_analytics.get_real_time_insights()

def get_anomaly_report(hours: int = 24):
    """Convenience function for anomaly reports"""
    return advanced_analytics.get_anomaly_report(hours)

if __name__ == "__main__":
    print("🧠 ADVANCED ERROR LEARNING FEATURES TEST")
    print("=" * 50)

    # Test advanced analytics
    print("Running full analysis...")
    results = advanced_analytics.run_full_analysis()

    print(f"Status: {results.get('status', 'unknown')}")
    print(f"Anomalies Detected: {results.get('anomalies_detected', 0)}")
    print(f"Maintenance Items: {len(results.get('maintenance_schedule', {}))}")

    if results.get('recommendations'):
        print("\n💡 Recommendations:")
        for rec in results['recommendations'][:3]:
            print(f"  • {rec}")

    # Test anomaly detection
    print("\nTesting anomaly detection...")
    anomaly_report = get_anomaly_report(hours=1)
    print(f"Anomalies in last hour: {anomaly_report['total_anomalies']}")

    print("\n✅ Advanced error learning features test completed!")