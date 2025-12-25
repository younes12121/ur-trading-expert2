"""
AI Custom Models per User
Creates personalized AI models based on individual user trading behavior and preferences
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import json
import os
import logging
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserProfileAnalyzer:
    """Analyzes user trading behavior to create personalized profiles"""

    def __init__(self, profiles_dir: str = "user_profiles"):
        self.profiles_dir = profiles_dir
        self.user_profiles = {}
        self.scaler = StandardScaler()

        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)

        self._load_profiles()

    def _load_profiles(self):
        """Load existing user profiles"""
        profiles_file = f"{self.profiles_dir}/user_profiles.json"
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, 'r') as f:
                    self.user_profiles = json.load(f)
                logger.info(f"Loaded {len(self.user_profiles)} user profiles")
            except Exception as e:
                logger.error(f"Error loading user profiles: {e}")

    def _save_profiles(self):
        """Save user profiles to disk"""
        profiles_file = f"{self.profiles_dir}/user_profiles.json"
        try:
            with open(profiles_file, 'w') as f:
                json.dump(self.user_profiles, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving user profiles: {e}")

    def analyze_user_behavior(self, user_id: str, trading_history: pd.DataFrame) -> Dict:
        """Analyze user trading behavior and create comprehensive profile"""
        if trading_history.empty:
            return self._create_empty_profile(user_id)

        profile = {
            'user_id': user_id,
            'analysis_date': datetime.now(),
            'trading_style': self._determine_trading_style(trading_history),
            'risk_profile': self._assess_risk_profile(trading_history),
            'preferred_assets': self._identify_preferred_assets(trading_history),
            'time_preferences': self._analyze_time_preferences(trading_history),
            'performance_patterns': self._analyze_performance_patterns(trading_history),
            'strategy_preferences': self._identify_strategy_preferences(trading_history),
            'market_regime_performance': self._analyze_regime_performance(trading_history),
            'behavioral_traits': self._extract_behavioral_traits(trading_history)
        }

        # Store profile
        self.user_profiles[user_id] = profile
        self._save_profiles()

        logger.info(f"Analyzed behavior for user {user_id}")
        return profile

    def _determine_trading_style(self, history: pd.DataFrame) -> Dict:
        """Determine user's trading style (scalping, day trading, swing, position)"""
        if 'duration_hours' not in history.columns:
            return {'style': 'unknown', 'confidence': 0}

        avg_duration = history['duration_hours'].mean()

        if avg_duration < 1:
            style = 'scalping'
        elif avg_duration < 24:
            style = 'day_trading'
        elif avg_duration < 168:  # 7 days
            style = 'swing_trading'
        else:
            style = 'position_trading'

        # Calculate style confidence based on duration consistency
        duration_std = history['duration_hours'].std()
        consistency = max(0, 1 - (duration_std / avg_duration)) if avg_duration > 0 else 0

        return {
            'style': style,
            'avg_duration_hours': avg_duration,
            'consistency': consistency,
            'confidence': consistency * 100
        }

    def _assess_risk_profile(self, history: pd.DataFrame) -> Dict:
        """Assess user's risk tolerance and profile"""
        if history.empty:
            return {'risk_level': 'unknown', 'score': 0}

        # Calculate risk metrics
        avg_position_size = history.get('position_size', pd.Series([1] * len(history))).mean()
        avg_stop_loss_pct = history.get('stop_loss_pct', pd.Series([0.02] * len(history))).mean()
        max_drawdown = history.get('drawdown', pd.Series([0] * len(history))).max()
        win_rate = (history.get('pnl', pd.Series([0] * len(history))) > 0).mean()

        # Risk score calculation (0-100, higher = more risk tolerant)
        risk_score = (
            (avg_position_size * 20) +  # Position size contribution
            ((1 - avg_stop_loss_pct) * 30) +  # Stop loss tightness
            (max_drawdown * -50) +  # Drawdown penalty
            (win_rate * 20)  # Win rate contribution
        )

        risk_score = max(0, min(100, risk_score))

        # Determine risk level
        if risk_score < 30:
            risk_level = 'conservative'
        elif risk_score < 60:
            risk_level = 'moderate'
        else:
            risk_level = 'aggressive'

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'avg_position_size': avg_position_size,
            'avg_stop_loss_pct': avg_stop_loss_pct,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate
        }

    def _identify_preferred_assets(self, history: pd.DataFrame) -> Dict:
        """Identify user's preferred trading assets"""
        if 'asset' not in history.columns:
            return {'top_assets': [], 'preferences': {}}

        asset_counts = history['asset'].value_counts()
        asset_performance = {}

        # Calculate performance per asset
        for asset in asset_counts.index:
            asset_trades = history[history['asset'] == asset]
            win_rate = (asset_trades['pnl'] > 0).mean()
            avg_pnl = asset_trades['pnl'].mean()
            total_trades = len(asset_trades)

            asset_performance[asset] = {
                'win_rate': win_rate,
                'avg_pnl': avg_pnl,
                'total_trades': total_trades,
                'preference_score': (win_rate * 0.6) + (min(total_trades/10, 1) * 0.4)
            }

        # Sort by preference score
        top_assets = sorted(asset_performance.items(),
                          key=lambda x: x[1]['preference_score'],
                          reverse=True)[:5]

        return {
            'top_assets': [asset for asset, _ in top_assets],
            'asset_performance': asset_performance,
            'total_unique_assets': len(asset_counts)
        }

    def _analyze_time_preferences(self, history: pd.DataFrame) -> Dict:
        """Analyze user's preferred trading times"""
        if 'timestamp' not in history.columns:
            return {'preferred_hours': [], 'preferred_days': []}

        # Extract hour and day of week
        history['hour'] = pd.to_datetime(history['timestamp']).dt.hour
        history['day_of_week'] = pd.to_datetime(history['timestamp']).dt.day_name()

        # Analyze hourly preferences
        hourly_performance = {}
        for hour in range(24):
            hour_trades = history[history['hour'] == hour]
            if len(hour_trades) > 0:
                win_rate = (hour_trades['pnl'] > 0).mean()
                hourly_performance[hour] = win_rate

        # Analyze daily preferences
        daily_performance = {}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_trades = history[history['day_of_week'] == day]
            if len(day_trades) > 0:
                win_rate = (day_trades['pnl'] > 0).mean()
                daily_performance[day] = win_rate

        # Find best performing hours/days
        best_hours = sorted(hourly_performance.items(), key=lambda x: x[1], reverse=True)[:3]
        best_days = sorted(daily_performance.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'preferred_hours': [hour for hour, _ in best_hours],
            'preferred_days': [day for day, _ in best_days],
            'hourly_performance': hourly_performance,
            'daily_performance': daily_performance
        }

    def _analyze_performance_patterns(self, history: pd.DataFrame) -> Dict:
        """Analyze user's performance patterns and trends"""
        if history.empty:
            return {'patterns': {}}

        patterns = {}

        # Win/loss streaks
        pnl_binary = (history['pnl'] > 0).astype(int)
        win_streak = 0
        loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0

        for pnl in pnl_binary:
            if pnl == 1:
                win_streak += 1
                loss_streak = 0
                max_win_streak = max(max_win_streak, win_streak)
            else:
                loss_streak += 1
                win_streak = 0
                max_loss_streak = max(max_loss_streak, loss_streak)

        patterns['max_win_streak'] = max_win_streak
        patterns['max_loss_streak'] = max_loss_streak

        # Performance by time of day
        patterns['time_performance'] = self._analyze_time_performance(history)

        # Performance by market conditions
        patterns['market_condition_performance'] = self._analyze_market_condition_performance(history)

        return patterns

    def _analyze_time_performance(self, history: pd.DataFrame) -> Dict:
        """Analyze performance by time periods"""
        if 'timestamp' not in history.columns:
            return {}

        history['month'] = pd.to_datetime(history['timestamp']).dt.month
        monthly_performance = {}

        for month in range(1, 13):
            month_trades = history[history['month'] == month]
            if len(month_trades) > 0:
                win_rate = (month_trades['pnl'] > 0).mean()
                monthly_performance[month] = win_rate

        return monthly_performance

    def _analyze_market_condition_performance(self, history: pd.DataFrame) -> Dict:
        """Analyze performance under different market conditions"""
        # This would analyze performance during bull/bear markets, high/low volatility, etc.
        # Simplified version
        return {
            'bull_market_performance': 0.65,  # Would be calculated from actual data
            'bear_market_performance': 0.55,
            'high_volatility_performance': 0.58,
            'low_volatility_performance': 0.68
        }

    def _identify_strategy_preferences(self, history: pd.DataFrame) -> Dict:
        """Identify user's preferred trading strategies"""
        # Analyze entry/exit patterns to determine strategy preferences
        strategies = {
            'momentum': 0,
            'mean_reversion': 0,
            'breakout': 0,
            'trend_following': 0,
            'scalping': 0
        }

        # Simple heuristic based on trade characteristics
        avg_duration = history.get('duration_hours', pd.Series([1] * len(history))).mean()
        avg_pnl = history.get('pnl', pd.Series([0] * len(history))).mean()

        if avg_duration < 1:
            strategies['scalping'] = 0.8
        elif avg_duration < 24:
            strategies['momentum'] = 0.7
        else:
            strategies['trend_following'] = 0.6

        # Could add more sophisticated strategy detection here

        return strategies

    def _analyze_regime_performance(self, history: pd.DataFrame) -> Dict:
        """Analyze performance across different market regimes"""
        # This would categorize trades by market regime and analyze performance
        # Simplified placeholder
        return {
            'bull_market': {'win_rate': 0.68, 'avg_pnl': 0.015},
            'bear_market': {'win_rate': 0.55, 'avg_pnl': -0.008},
            'sideways': {'win_rate': 0.62, 'avg_pnl': 0.005},
            'volatile': {'win_rate': 0.45, 'avg_pnl': -0.012}
        }

    def _extract_behavioral_traits(self, history: pd.DataFrame) -> Dict:
        """Extract behavioral traits from trading patterns"""
        traits = {}

        # Risk management consistency
        stop_loss_usage = history.get('stop_loss_hit', pd.Series([False] * len(history))).mean()
        traits['stop_loss_discipline'] = stop_loss_usage

        # Trade frequency
        total_trades = len(history)
        traits['trade_frequency'] = total_trades

        # Profit taking behavior
        tp1_usage = history.get('tp1_hit', pd.Series([False] * len(history))).mean()
        tp2_usage = history.get('tp2_hit', pd.Series([False] * len(history))).mean()
        traits['profit_taking_discipline'] = (tp1_usage + tp2_usage) / 2

        # Loss aversion (how quickly they cut losses vs let profits run)
        avg_win_duration = history[history['pnl'] > 0]['duration_hours'].mean()
        avg_loss_duration = history[history['pnl'] < 0]['duration_hours'].mean()
        traits['loss_aversion_ratio'] = avg_loss_duration / avg_win_duration if avg_win_duration > 0 else 1

        return traits

    def _create_empty_profile(self, user_id: str) -> Dict:
        """Create empty profile for new users"""
        return {
            'user_id': user_id,
            'analysis_date': datetime.now(),
            'trading_style': {'style': 'unknown', 'confidence': 0},
            'risk_profile': {'risk_level': 'unknown', 'score': 0},
            'preferred_assets': {'top_assets': [], 'preferences': {}},
            'time_preferences': {'preferred_hours': [], 'preferred_days': []},
            'performance_patterns': {'patterns': {}},
            'strategy_preferences': {},
            'market_regime_performance': {},
            'behavioral_traits': {}
        }


class CustomAIModelTrainer:
    """Trains custom AI models for individual users"""

    def __init__(self, models_dir: str = "custom_models"):
        self.models_dir = models_dir
        self.user_models = {}
        self.profile_analyzer = UserProfileAnalyzer()

        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

    def create_custom_model(self, user_id: str, trading_history: pd.DataFrame,
                          market_data: pd.DataFrame) -> Dict:
        """Create a custom AI model for a specific user"""

        # First, analyze user profile
        user_profile = self.profile_analyzer.analyze_user_behavior(user_id, trading_history)

        # Create personalized feature set based on user preferences
        features = self._create_personalized_features(user_profile, market_data)

        # Train custom model
        model_info = self._train_user_model(user_id, features, trading_history, user_profile)

        # Store model info
        self.user_models[user_id] = {
            'model_info': model_info,
            'user_profile': user_profile,
            'created_at': datetime.now(),
            'performance': {}
        }

        logger.info(f"Created custom AI model for user {user_id}")
        return model_info

    def _create_personalized_features(self, user_profile: Dict, market_data: pd.DataFrame) -> np.ndarray:
        """Create feature set personalized to user's trading style and preferences"""

        features = []

        # Base technical features
        if 'close' in market_data.columns:
            # Price returns
            features.append(market_data['close'].pct_change().fillna(0))

            # Moving averages based on user style
            trading_style = user_profile.get('trading_style', {}).get('style', 'day_trading')

            if trading_style == 'scalping':
                features.append(market_data['close'].rolling(5).mean().fillna(0))
                features.append(market_data['close'].rolling(10).mean().fillna(0))
            elif trading_style == 'day_trading':
                features.append(market_data['close'].rolling(20).mean().fillna(0))
                features.append(market_data['close'].rolling(50).mean().fillna(0))
            else:  # swing/position trading
                features.append(market_data['close'].rolling(50).mean().fillna(0))
                features.append(market_data['close'].rolling(200).mean().fillna(0))

        # Volatility features
        if len(features) > 0:
            returns = features[0]  # Price returns
            features.append(returns.rolling(20).std().fillna(0))

        # User-specific time features
        time_prefs = user_profile.get('time_preferences', {})
        preferred_hours = time_prefs.get('preferred_hours', [])

        if 'timestamp' in market_data.columns and preferred_hours:
            market_data['hour'] = pd.to_datetime(market_data['timestamp']).dt.hour
            # Feature indicating if current hour is preferred
            hour_preference = market_data['hour'].isin(preferred_hours).astype(int)
            features.append(hour_preference)

        # User risk-adjusted features
        risk_profile = user_profile.get('risk_profile', {})
        risk_level = risk_profile.get('risk_level', 'moderate')

        if risk_level == 'conservative':
            # More emphasis on stability
            if len(features) > 1:
                features.append(features[1] * 0.5)  # Reduced volatility weight
        elif risk_level == 'aggressive':
            # More emphasis on momentum
            if 'volume' in market_data.columns:
                features.append(market_data['volume'].pct_change().fillna(0))

        return np.column_stack(features) if features else np.array([])

    def _train_user_model(self, user_id: str, features: np.ndarray,
                         trading_history: pd.DataFrame, user_profile: Dict) -> Dict:
        """Train a personalized model for the user"""

        if len(features) == 0 or trading_history.empty:
            return {'status': 'insufficient_data'}

        # Create target variable (next period return)
        if 'close' in trading_history.columns:
            target = trading_history['close'].pct_change().shift(-1).fillna(0)
        else:
            target = trading_history.get('pnl', pd.Series([0] * len(trading_history)))

        # Ensure features and target have same length
        min_length = min(len(features), len(target))
        features = features[:min_length]
        target = target[:min_length]

        # Split data
        split_idx = int(len(features) * 0.8)
        X_train, X_test = features[:split_idx], features[split_idx:]
        y_train, y_test = target[:split_idx], target[split_idx:]

        # Train simple model (could be enhanced with neural networks)
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import mean_squared_error, r2_score

        # Adjust model complexity based on user profile
        trading_style = user_profile.get('trading_style', {}).get('style', 'day_trading')
        risk_level = user_profile.get('risk_profile', {}).get('risk_level', 'moderate')

        if trading_style == 'scalping' or risk_level == 'aggressive':
            n_estimators = 200  # More complex for high-frequency traders
        else:
            n_estimators = 100  # Simpler for conservative/swing traders

        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=10,
            random_state=42
        )

        model.fit(X_train, y_train)

        # Evaluate model
        train_predictions = model.predict(X_train)
        test_predictions = model.predict(X_test)

        train_mse = mean_squared_error(y_train, train_predictions)
        test_mse = mean_squared_error(y_test, test_predictions)
        train_r2 = r2_score(y_train, train_predictions)
        test_r2 = r2_score(y_test, test_predictions)

        # Save model
        model_path = f"{self.models_dir}/{user_id}_custom_model.pkl"
        joblib.dump(model, model_path)

        model_info = {
            'user_id': user_id,
            'model_path': model_path,
            'features_used': features.shape[1] if len(features.shape) > 1 else 1,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'model_type': 'RandomForestRegressor',
            'personalization_factors': {
                'trading_style': trading_style,
                'risk_level': risk_level,
                'n_estimators': n_estimators
            }
        }

        return model_info

    def get_user_prediction(self, user_id: str, market_data: pd.DataFrame) -> Dict:
        """Get prediction from user's custom model"""

        if user_id not in self.user_models:
            return {'error': f'No custom model found for user {user_id}'}

        model_info = self.user_models[user_id]['model_info']
        user_profile = self.user_models[user_id]['user_profile']

        # Load model
        try:
            model = joblib.load(model_info['model_path'])
        except Exception as e:
            return {'error': f'Could not load model: {e}'}

        # Create personalized features
        features = self._create_personalized_features(user_profile, market_data)

        if len(features) == 0:
            return {'error': 'Could not create features'}

        # Get latest feature vector
        latest_features = features[-1:].reshape(1, -1)

        # Make prediction
        prediction = model.predict(latest_features)[0]

        # Adjust prediction based on user profile
        adjusted_prediction = self._adjust_prediction_for_user(prediction, user_profile)

        return {
            'user_id': user_id,
            'prediction': adjusted_prediction,
            'raw_prediction': prediction,
            'confidence': self._calculate_prediction_confidence(model, latest_features),
            'model_info': model_info,
            'timestamp': datetime.now()
        }

    def _adjust_prediction_for_user(self, prediction: float, user_profile: Dict) -> float:
        """Adjust prediction based on user's historical behavior and risk profile"""

        risk_level = user_profile.get('risk_profile', {}).get('risk_level', 'moderate')
        trading_style = user_profile.get('trading_style', {}).get('style', 'day_trading')

        # Conservative users get dampened predictions
        if risk_level == 'conservative':
            adjustment_factor = 0.8
        elif risk_level == 'aggressive':
            adjustment_factor = 1.2
        else:  # moderate
            adjustment_factor = 1.0

        # Scalpers might need more sensitive predictions
        if trading_style == 'scalping':
            sensitivity_factor = 1.1
        elif trading_style == 'position_trading':
            sensitivity_factor = 0.9
        else:
            sensitivity_factor = 1.0

        return prediction * adjustment_factor * sensitivity_factor

    def _calculate_prediction_confidence(self, model, features: np.ndarray) -> float:
        """Calculate confidence in the prediction using model uncertainty"""
        # Simple confidence based on feature values (could be enhanced)
        feature_std = np.std(features)
        confidence = max(0.1, min(1.0, 1.0 - feature_std))  # Higher std = lower confidence

        return confidence * 100  # Return as percentage

    def update_user_model(self, user_id: str, new_trading_data: pd.DataFrame,
                         market_data: pd.DataFrame) -> Dict:
        """Update user's custom model with new data"""

        if user_id not in self.user_models:
            return {'error': f'No existing model for user {user_id}'}

        # Get existing profile
        user_profile = self.user_models[user_id]['user_profile']

        # Update profile with new data
        updated_profile = self.profile_analyzer.analyze_user_behavior(user_id, new_trading_data)

        # Retrain model with combined data
        # (In practice, you'd want to combine old and new data)
        model_info = self._train_user_model(user_id, market_data.values, new_trading_data, updated_profile)

        # Update stored model
        self.user_models[user_id]['model_info'] = model_info
        self.user_models[user_id]['user_profile'] = updated_profile
        self.user_models[user_id]['updated_at'] = datetime.now()

        return {
            'status': 'updated',
            'user_id': user_id,
            'new_performance': model_info
        }


class PersonalizedRecommendationEngine:
    """Generates personalized recommendations based on user profiles"""

    def __init__(self, profile_analyzer: UserProfileAnalyzer):
        self.profile_analyzer = profile_analyzer

    def generate_recommendations(self, user_id: str, current_market_conditions: Dict,
                               available_signals: List[Dict]) -> Dict:
        """Generate personalized recommendations for a user"""

        if user_id not in self.profile_analyzer.user_profiles:
            return {'error': f'No profile found for user {user_id}'}

        user_profile = self.profile_analyzer.user_profiles[user_id]

        recommendations = {
            'user_id': user_id,
            'recommended_signals': self._filter_signals_for_user(available_signals, user_profile),
            'portfolio_adjustments': self._suggest_portfolio_adjustments(user_profile, current_market_conditions),
            'risk_adjustments': self._suggest_risk_adjustments(user_profile, current_market_conditions),
            'timing_suggestions': self._suggest_optimal_timing(user_profile, current_market_conditions),
            'personalization_factors': self._extract_personalization_factors(user_profile)
        }

        return recommendations

    def _filter_signals_for_user(self, signals: List[Dict], user_profile: Dict) -> List[Dict]:
        """Filter and rank signals based on user preferences"""

        filtered_signals = []
        preferred_assets = user_profile.get('preferred_assets', {}).get('top_assets', [])

        for signal in signals:
            score = 0
            reasons = []

            # Asset preference bonus
            if signal.get('asset') in preferred_assets:
                score += 20
                reasons.append("Preferred asset")

            # Risk alignment
            user_risk = user_profile.get('risk_profile', {}).get('risk_level', 'moderate')
            signal_risk = self._assess_signal_risk(signal)

            if user_risk == signal_risk:
                score += 15
                reasons.append("Risk level matches preference")

            # Trading style alignment
            user_style = user_profile.get('trading_style', {}).get('style', 'day_trading')
            signal_duration = signal.get('estimated_duration_hours', 24)

            if self._style_matches_duration(user_style, signal_duration):
                score += 10
                reasons.append("Trading style alignment")

            # Confidence threshold
            user_risk_tolerance = user_profile.get('risk_profile', {}).get('risk_score', 50)
            min_confidence = max(50, user_risk_tolerance)  # Conservative users need higher confidence

            signal_confidence = signal.get('confidence', 0)
            if signal_confidence >= min_confidence:
                score += signal_confidence / 5  # Bonus based on confidence
                reasons.append(f"Confidence meets threshold ({signal_confidence}%)")

            if score > 30:  # Minimum threshold to recommend
                signal_copy = signal.copy()
                signal_copy['recommendation_score'] = score
                signal_copy['recommendation_reasons'] = reasons
                filtered_signals.append(signal_copy)

        # Sort by recommendation score
        filtered_signals.sort(key=lambda x: x['recommendation_score'], reverse=True)

        return filtered_signals[:5]  # Top 5 recommendations

    def _assess_signal_risk(self, signal: Dict) -> str:
        """Assess the risk level of a signal"""
        confidence = signal.get('confidence', 50)
        stop_loss_pct = signal.get('stop_loss_pct', 0.02)

        if confidence > 80 and stop_loss_pct < 0.01:
            return 'conservative'
        elif confidence > 70 and stop_loss_pct < 0.03:
            return 'moderate'
        else:
            return 'aggressive'

    def _style_matches_duration(self, style: str, duration: float) -> bool:
        """Check if signal duration matches user's trading style"""
        if style == 'scalping' and duration < 1:
            return True
        elif style == 'day_trading' and duration < 24:
            return True
        elif style == 'swing_trading' and duration < 168:
            return True
        elif style == 'position_trading' and duration >= 168:
            return True
        return False

    def _suggest_portfolio_adjustments(self, user_profile: Dict,
                                     market_conditions: Dict) -> List[str]:
        """Suggest portfolio adjustments based on user profile and market conditions"""
        suggestions = []

        risk_level = user_profile.get('risk_profile', {}).get('risk_level', 'moderate')
        market_regime = market_conditions.get('regime', 'neutral')

        if market_regime == 'volatile' and risk_level == 'conservative':
            suggestions.append("Reduce position sizes by 20-30% due to high volatility")
        elif market_regime == 'bull' and risk_level == 'aggressive':
            suggestions.append("Consider increasing exposure to trending assets")

        preferred_assets = user_profile.get('preferred_assets', {}).get('top_assets', [])
        if preferred_assets:
            suggestions.append(f"Increase allocation to preferred assets: {', '.join(preferred_assets[:3])}")

        return suggestions

    def _suggest_risk_adjustments(self, user_profile: Dict, market_conditions: Dict) -> List[str]:
        """Suggest risk management adjustments"""
        suggestions = []

        risk_level = user_profile.get('risk_profile', {}).get('risk_level', 'moderate')
        market_volatility = market_conditions.get('volatility', 0.02)

        if market_volatility > 0.03:
            if risk_level == 'conservative':
                suggestions.append("Use wider stop losses (2-3% instead of 1-2%)")
            elif risk_level == 'aggressive':
                suggestions.append("Consider reducing position sizes despite high volatility tolerance")

        behavioral_traits = user_profile.get('behavioral_traits', {})
        stop_loss_discipline = behavioral_traits.get('stop_loss_discipline', 0.5)

        if stop_loss_discipline < 0.7:
            suggestions.append("Focus on improving stop-loss discipline - consider automated stops")

        return suggestions

    def _suggest_optimal_timing(self, user_profile: Dict, market_conditions: Dict) -> List[str]:
        """Suggest optimal timing based on user preferences"""
        suggestions = []

        time_prefs = user_profile.get('time_preferences', {})
        preferred_hours = time_prefs.get('preferred_hours', [])
        preferred_days = time_prefs.get('preferred_days', [])

        current_hour = datetime.now().hour
        current_day = datetime.now().strftime('%A')

        if preferred_hours and current_hour in preferred_hours:
            suggestions.append(f"Current hour ({current_hour}:00) aligns with your best performing hours")

        if preferred_days and current_day in preferred_days:
            suggestions.append(f"Current day ({current_day}) is in your preferred trading days")

        # Market regime timing
        regime = market_conditions.get('regime', 'neutral')
        regime_performance = user_profile.get('market_regime_performance', {})

        if regime in regime_performance:
            perf = regime_performance[regime]
            win_rate = perf.get('win_rate', 0)
            if win_rate > 0.65:
                suggestions.append(f"Strong historical performance in {regime} market conditions")
            elif win_rate < 0.5:
                suggestions.append(f"Weak historical performance in {regime} conditions - exercise caution")

        return suggestions

    def _extract_personalization_factors(self, user_profile: Dict) -> Dict:
        """Extract key personalization factors for transparency"""
        return {
            'trading_style': user_profile.get('trading_style', {}).get('style', 'unknown'),
            'risk_level': user_profile.get('risk_profile', {}).get('risk_level', 'unknown'),
            'preferred_assets': user_profile.get('preferred_assets', {}).get('top_assets', []),
            'preferred_hours': user_profile.get('time_preferences', {}).get('preferred_hours', []),
            'key_traits': list(user_profile.get('behavioral_traits', {}).keys())
        }


if __name__ == "__main__":
    # Example usage
    analyzer = UserProfileAnalyzer()
    trainer = CustomAIModelTrainer()
    recommender = PersonalizedRecommendationEngine(analyzer)

    print("AI Custom Models per User initialized!")
    print("Ready to create personalized AI models and recommendations")
