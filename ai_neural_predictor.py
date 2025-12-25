"""
Advanced AI Neural Network Predictor
Implements deep learning models for market prediction and signal enhancement
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, Conv1D, MaxPooling1D, Flatten, Input, Concatenate
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuralPredictor:
    """Advanced neural network for market direction and probability prediction"""

    def __init__(self, model_dir: str = "models", performance_mode: bool = False):
        self.model_dir = model_dir
        self.performance_mode = performance_mode
        self.scaler = StandardScaler()
        self.price_scaler = MinMaxScaler()
        self.models = {}
        self.sequence_length = 60  # 60 periods for prediction
        self.prediction_horizon = 12  # Predict 12 periods ahead

        # Performance optimizations
        self._feature_cache = {}
        self._prediction_cache = {}
        self._cache_ttl = 30 if performance_mode else 60  # seconds

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

    def prepare_data(self, df: pd.DataFrame, target_col: str = 'close') -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for neural network training"""
        # Feature engineering
        features = self._create_features(df)

        # Create target (direction and magnitude)
        target = self._create_target(df, target_col)

        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        scaled_target = self.price_scaler.fit_transform(target.reshape(-1, 1)).flatten()

        # Create sequences
        X, y = self._create_sequences(scaled_features, scaled_target)

        return X, y

    def _create_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create comprehensive feature set for neural network - OPTIMIZED"""
        # Check cache first
        if self.performance_mode:
            cache_key = hash(df.values.tobytes()) if hasattr(df, 'values') else hash(str(df))
            current_time = time.time()

            if cache_key in self._feature_cache:
                cache_entry = self._feature_cache[cache_key]
                if current_time - cache_entry['timestamp'] < self._cache_ttl:
                    return cache_entry['features']

        features = []

        # Price features
        features.extend([
            df['close'].pct_change().fillna(0),  # Returns
            df['high'].pct_change().fillna(0),   # High returns
            df['low'].pct_change().fillna(0),    # Low returns
            df['volume'].pct_change().fillna(0), # Volume changes
        ])

        # Technical indicators
        if 'sma_20' in df.columns:
            features.append((df['close'] - df['sma_20']) / df['sma_20'])  # Price vs SMA20
        if 'sma_50' in df.columns:
            features.append((df['close'] - df['sma_50']) / df['sma_50'])  # Price vs SMA50
        if 'rsi' in df.columns:
            features.append(df['rsi'] / 100.0)  # Normalized RSI
        if 'macd' in df.columns:
            features.append(df['macd'].fillna(0))  # MACD
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            features.append((df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower']))  # Bollinger position

        # Volatility features
        returns = df['close'].pct_change().fillna(0)
        features.append(returns.rolling(20).std().fillna(0))  # Rolling volatility

        # Volume features
        if 'volume' in df.columns:
            features.append(df['volume'] / df['volume'].rolling(20).mean())  # Volume ratio

        # Momentum features
        for period in [5, 10, 20]:
            features.append(df['close'].pct_change(period).fillna(0))  # Momentum

        feature_array = np.column_stack(features)

        # Cache the result
        if self.performance_mode:
            self._feature_cache[cache_key] = {
                'features': feature_array,
                'timestamp': current_time
            }

            # Limit cache size
            if len(self._feature_cache) > 50:
                oldest_key = min(self._feature_cache.keys(),
                               key=lambda k: self._feature_cache[k]['timestamp'])
                del self._feature_cache[oldest_key]

        return feature_array

    def _create_target(self, df: pd.DataFrame, target_col: str) -> np.ndarray:
        """Create prediction target"""
        # Future price direction and magnitude
        future_price = df[target_col].shift(-self.prediction_horizon)
        current_price = df[target_col]

        # Target: future price change percentage
        target = ((future_price - current_price) / current_price).fillna(0)

        return target.values

    def _create_sequences(self, features: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create input sequences for LSTM"""
        X, y = [], []

        for i in range(len(features) - self.sequence_length - self.prediction_horizon):
            X.append(features[i:i+self.sequence_length])
            y.append(target[i+self.sequence_length])

        return np.array(X), np.array(y)

    def build_direction_model(self) -> Model:
        """Build LSTM model for price direction prediction"""
        model = Sequential([
            Input(shape=(self.sequence_length, None)),  # Flexible feature count

            # Convolutional layers for feature extraction
            Conv1D(64, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            Dropout(0.2),

            # Bidirectional LSTM layers
            Bidirectional(LSTM(128, return_sequences=True)),
            Dropout(0.3),
            Bidirectional(LSTM(64, return_sequences=False)),
            Dropout(0.3),

            # Dense layers
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='tanh')  # Output between -1 and 1 (direction strength)
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mse']
        )

        return model

    def build_probability_model(self) -> Model:
        """Build model for probability estimation"""
        input_layer = Input(shape=(self.sequence_length, None))

        # Feature extraction
        conv = Conv1D(64, kernel_size=3, activation='relu')(input_layer)
        pool = MaxPooling1D(pool_size=2)(conv)
        drop1 = Dropout(0.2)(pool)

        # LSTM layers
        lstm1 = Bidirectional(LSTM(128, return_sequences=True))(drop1)
        drop2 = Dropout(0.3)(lstm1)
        lstm2 = Bidirectional(LSTM(64, return_sequences=False))(drop2)
        drop3 = Dropout(0.3)(lstm2)

        # Dense layers for direction
        direction_dense = Dense(32, activation='relu')(drop3)
        direction_output = Dense(1, activation='tanh', name='direction')(direction_dense)

        # Dense layers for confidence
        confidence_dense = Dense(32, activation='relu')(drop3)
        confidence_output = Dense(1, activation='sigmoid', name='confidence')(confidence_dense)

        # Combine outputs
        combined = Concatenate()([direction_output, confidence_output])
        final_output = Dense(1, activation='sigmoid', name='probability')(combined)

        model = Model(inputs=input_layer, outputs=[direction_output, confidence_output, final_output])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss={
                'direction': 'mse',
                'confidence': 'mse',
                'probability': 'binary_crossentropy'
            },
            loss_weights={
                'direction': 1.0,
                'confidence': 0.5,
                'probability': 2.0
            },
            metrics=['mae']
        )

        return model

    def train_model(self, df: pd.DataFrame, asset_symbol: str, epochs: int = 100) -> Dict:
        """Train neural network model for specific asset"""
        logger.info(f"Training neural network for {asset_symbol}")

        # Prepare data
        X, y = self.prepare_data(df)

        if len(X) < 100:  # Minimum data requirement
            logger.warning(f"Insufficient data for {asset_symbol}: {len(X)} sequences")
            return {'status': 'insufficient_data'}

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Build model
        model = self.build_direction_model()

        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ModelCheckpoint(
                f"{self.model_dir}/{asset_symbol}_best.h5",
                monitor='val_loss',
                save_best_only=True
            )
        ]

        # Train model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )

        # Save model and scaler
        model.save(f"{self.model_dir}/{asset_symbol}_model.h5")
        joblib.dump(self.scaler, f"{self.model_dir}/{asset_symbol}_scaler.pkl")
        joblib.dump(self.price_scaler, f"{self.model_dir}/{asset_symbol}_price_scaler.pkl")

        # Store model reference
        self.models[asset_symbol] = model

        # Evaluate model
        test_loss = model.evaluate(X_test, y_test, verbose=0)

        return {
            'status': 'trained',
            'asset': asset_symbol,
            'test_loss': test_loss,
            'epochs_trained': len(history.history['loss']),
            'final_val_loss': history.history['val_loss'][-1]
        }

    def predict_direction(self, df: pd.DataFrame, asset_symbol: str) -> Dict:
        """Predict market direction using trained model - OPTIMIZED"""
        # Check prediction cache
        if self.performance_mode:
            cache_key = f"{asset_symbol}_{hash(df.values.tobytes()) if hasattr(df, 'values') else hash(str(df))}"
            current_time = time.time()

            if cache_key in self._prediction_cache:
                cache_entry = self._prediction_cache[cache_key]
                if current_time - cache_entry['timestamp'] < self._cache_ttl:
                    return cache_entry['prediction']

        if asset_symbol not in self.models:
            if not self.load_model(asset_symbol):
                return {'error': f'No trained model for {asset_symbol}'}

        model = self.models[asset_symbol]

        # Prepare recent data for prediction (features now cached)
        features = self._create_features(df)
        scaled_features = self.scaler.transform(features)

        # Get last sequence
        if len(scaled_features) < self.sequence_length:
            return {'error': 'Insufficient data for prediction'}

        recent_sequence = scaled_features[-self.sequence_length:].reshape(1, self.sequence_length, -1)

        # Make prediction
        prediction = model.predict(recent_sequence, verbose=0)[0][0]

        # Convert to direction and confidence
        direction = 'bullish' if prediction > 0.1 else 'bearish' if prediction < -0.1 else 'neutral'
        confidence = min(abs(prediction) * 100, 95)  # Scale to 0-95%

        result = {
            'asset': asset_symbol,
            'direction': direction,
            'prediction_strength': float(prediction),
            'confidence': float(confidence),
            'timestamp': df.index[-1] if hasattr(df, 'index') else None
        }

        # Cache the prediction
        if self.performance_mode:
            self._prediction_cache[cache_key] = {
                'prediction': result,
                'timestamp': current_time
            }

            # Limit cache size
            if len(self._prediction_cache) > 30:
                oldest_key = min(self._prediction_cache.keys(),
                               key=lambda k: self._prediction_cache[k]['timestamp'])
                del self._prediction_cache[oldest_key]

        return result

    def load_model(self, asset_symbol: str) -> bool:
        """Load trained model from disk"""
        model_path = f"{self.model_dir}/{asset_symbol}_model.h5"
        scaler_path = f"{self.model_dir}/{asset_symbol}_scaler.pkl"
        price_scaler_path = f"{self.model_dir}/{asset_symbol}_price_scaler.pkl"

        if not all(os.path.exists(p) for p in [model_path, scaler_path, price_scaler_path]):
            return False

        try:
            self.models[asset_symbol] = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            self.price_scaler = joblib.load(price_scaler_path)
            return True
        except Exception as e:
            logger.error(f"Error loading model for {asset_symbol}: {e}")
            return False

    def get_model_performance(self, asset_symbol: str) -> Dict:
        """Get performance metrics for trained model"""
        # This would require storing validation metrics during training
        # For now, return basic info
        if asset_symbol in self.models:
            return {
                'asset': asset_symbol,
                'status': 'loaded',
                'architecture': 'LSTM-CNN Hybrid',
                'sequence_length': self.sequence_length,
                'prediction_horizon': self.prediction_horizon
            }
        else:
            return {'asset': asset_symbol, 'status': 'not_trained'}


class AdvancedAIPredictor:
    """Advanced AI predictor combining multiple models"""

    def __init__(self):
        self.neural_predictor = NeuralPredictor()
        self.ensemble_models = {}
        self.confidence_threshold = 0.7

    def predict_signal_quality(self, signal_data: Dict, market_data: pd.DataFrame) -> Dict:
        """Use AI to enhance signal quality assessment"""
        asset = signal_data.get('asset', 'unknown')

        # Get neural network prediction
        nn_prediction = self.neural_predictor.predict_direction(market_data, asset)

        if 'error' in nn_prediction:
            # Fallback to rule-based assessment
            return self._rule_based_quality(signal_data)

        # Combine neural prediction with existing signal criteria
        ai_enhanced_score = self._combine_predictions(signal_data, nn_prediction)

        return {
            'original_score': signal_data.get('score', 0),
            'ai_enhanced_score': ai_enhanced_score,
            'neural_direction': nn_prediction['direction'],
            'neural_confidence': nn_prediction['confidence'],
            'prediction_strength': nn_prediction['prediction_strength'],
            'final_confidence': min(ai_enhanced_score / 20.0 * 100, 98),  # Scale to percentage
            'ai_boost': ai_enhanced_score > signal_data.get('score', 0)
        }

    def _combine_predictions(self, signal_data: Dict, nn_prediction: Dict) -> float:
        """Combine neural network prediction with rule-based signals"""
        base_score = signal_data.get('score', 15)  # Default to Elite level

        # Neural network contribution
        nn_strength = abs(nn_prediction['prediction_strength'])
        nn_confidence = nn_prediction['confidence'] / 100.0

        # Direction alignment bonus
        direction_match = 1.0
        if 'direction' in signal_data:
            signal_direction = 'bullish' if signal_data['direction'].lower() == 'buy' else 'bearish'
            if signal_direction == nn_prediction['direction']:
                direction_match = 1.2  # 20% bonus for agreement
            else:
                direction_match = 0.8  # 20% penalty for disagreement

        # Calculate enhanced score
        ai_boost = nn_strength * nn_confidence * 2  # Scale neural contribution
        enhanced_score = base_score * direction_match + ai_boost

        return min(enhanced_score, 20.0)  # Cap at maximum possible score

    def _rule_based_quality(self, signal_data: Dict) -> Dict:
        """Fallback rule-based quality assessment"""
        score = signal_data.get('score', 15)
        return {
            'original_score': score,
            'ai_enhanced_score': score,
            'neural_direction': 'unknown',
            'neural_confidence': 0,
            'prediction_strength': 0,
            'final_confidence': score / 20.0 * 100,
            'ai_boost': False
        }

    def predict_market_regime(self, market_data: pd.DataFrame) -> Dict:
        """Predict current market regime using AI"""
        # This would use a separate regime detection model
        # For now, use simple heuristics enhanced by neural predictions

        # Get predictions for multiple assets/timeframes
        regime_signals = []

        # Analyze trend strength
        recent_returns = market_data['close'].pct_change(20).iloc[-1]
        volatility = market_data['close'].pct_change().rolling(20).std().iloc[-1]

        # Neural network input for regime
        nn_input = {
            'trend_strength': abs(recent_returns),
            'volatility': volatility,
            'volume_trend': market_data['volume'].pct_change(10).iloc[-1] if 'volume' in market_data else 0
        }

        # Simple regime classification (would be enhanced with ML)
        if recent_returns > 0.05 and volatility < 0.02:
            regime = 'strong_bull'
            confidence = 85
        elif recent_returns > 0.02:
            regime = 'bull'
            confidence = 70
        elif recent_returns < -0.05 and volatility < 0.02:
            regime = 'strong_bear'
            confidence = 85
        elif recent_returns < -0.02:
            regime = 'bear'
            confidence = 70
        else:
            regime = 'sideways'
            confidence = 60

        return {
            'regime': regime,
            'confidence': confidence,
            'trend_strength': float(recent_returns),
            'volatility': float(volatility),
            'regime_description': self._get_regime_description(regime)
        }

    def _get_regime_description(self, regime: str) -> str:
        """Get human-readable regime description"""
        descriptions = {
            'strong_bull': 'Strong upward trend with low volatility',
            'bull': 'Moderate upward trend',
            'strong_bear': 'Strong downward trend with low volatility',
            'bear': 'Moderate downward trend',
            'sideways': 'Range-bound market with no clear direction'
        }
        return descriptions.get(regime, 'Unknown regime')


if __name__ == "__main__":
    # Example usage
    predictor = AdvancedAIPredictor()
    print("Advanced AI Neural Predictor initialized!")
    print("Ready for market prediction and signal enhancement")
