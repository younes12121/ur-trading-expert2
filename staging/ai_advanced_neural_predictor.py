"""
Advanced Neural Network Predictor - Quantum Elite AI Enhancement
Implements state-of-the-art deep learning models for market prediction and signal enhancement
Features: Transformer models, GANs for synthetic data, quantum-inspired optimization
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Dense, Dropout, LayerNormalization, MultiHeadAttention,
    GlobalAveragePooling1D, Concatenate, LSTM, Bidirectional, Conv1D,
    MaxPooling1D, Flatten, BatchNormalization, GaussianNoise
)
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam, AdamW
from tensorflow.keras import backend as K
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import TimeSeriesSplit
import joblib
import os
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import warnings

# Suppress TensorFlow warnings
warnings.filterwarnings('ignore')
tf.get_logger().setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionalEncoding(tf.keras.layers.Layer):
    """Positional encoding for transformer models"""
    def __init__(self, max_len, d_model):
        super(PositionalEncoding, self).__init__()
        self.max_len = max_len
        self.d_model = d_model

    def build(self, input_shape):
        positions = np.arange(self.max_len)[:, np.newaxis]
        depths = np.arange(self.d_model)[np.newaxis, :] / self.d_model

        angle_rates = 1 / (10000 ** depths)
        angle_rads = positions * angle_rates

        pos_encoding = np.concatenate([np.sin(angle_rads), np.cos(angle_rads)], axis=-1)
        self.pos_encoding = tf.constant(pos_encoding, dtype=tf.float32)

    def call(self, inputs):
        return inputs + self.pos_encoding[:tf.shape(inputs)[1], :]

class TransformerBlock(tf.keras.layers.Layer):
    """Transformer encoder block"""
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            Dense(ff_dim, activation="relu"),
            Dense(embed_dim),
        ])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)

class QuantumInspiredOptimizer:
    """Quantum-inspired optimization for neural networks"""
    def __init__(self, population_size=50, max_iterations=100):
        self.population_size = population_size
        self.max_iterations = max_iterations

    def optimize_hyperparameters(self, model_builder, X, y, validation_data=None):
        """Optimize hyperparameters using quantum-inspired algorithm"""
        # Initialize quantum particles
        particles = self._initialize_particles()
        best_fitness = float('-inf')
        best_particle = None

        for iteration in range(self.max_iterations):
            for particle in particles:
                # Evaluate fitness
                fitness = self._evaluate_particle(particle, model_builder, X, y, validation_data)

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_particle = particle.copy()

            # Update particles using quantum-inspired operators
            particles = self._update_particles(particles, best_particle)

            logger.info(f"Quantum Optimization Iteration {iteration + 1}/{self.max_iterations}, Best Fitness: {best_fitness:.4f}")

        return best_particle

    def _initialize_particles(self):
        """Initialize quantum particles with random hyperparameters"""
        particles = []
        for _ in range(self.population_size):
            particle = {
                'learning_rate': np.random.uniform(1e-5, 1e-2),
                'dropout_rate': np.random.uniform(0.1, 0.5),
                'batch_size': np.random.choice([16, 32, 64, 128]),
                'lstm_units': np.random.choice([32, 64, 128, 256]),
                'attention_heads': np.random.choice([4, 8, 12, 16]),
                'ff_dim': np.random.choice([64, 128, 256, 512])
            }
            particles.append(particle)
        return particles

    def _evaluate_particle(self, particle, model_builder, X, y, validation_data):
        """Evaluate particle fitness"""
        try:
            model = model_builder(particle)
            history = model.fit(
                X, y,
                validation_data=validation_data,
                epochs=10,
                batch_size=particle['batch_size'],
                verbose=0,
                callbacks=[EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)]
            )
            return -history.history['val_loss'][-1]  # Negative loss as fitness
        except Exception as e:
            logger.warning(f"Particle evaluation failed: {e}")
            return float('-inf')

    def _update_particles(self, particles, best_particle):
        """Update particles using quantum-inspired operators"""
        new_particles = []
        for particle in particles:
            new_particle = {}
            for key in particle.keys():
                if key in ['batch_size', 'lstm_units', 'attention_heads', 'ff_dim']:
                    # Discrete parameters - use crossover
                    if np.random.random() < 0.7:
                        new_particle[key] = best_particle[key]
                    else:
                        new_particle[key] = particle[key]
                else:
                    # Continuous parameters - use quantum rotation
                    direction = best_particle[key] - particle[key]
                    step = np.random.uniform(0.1, 0.9) * direction
                    new_particle[key] = particle[key] + step

                    # Ensure bounds
                    if key == 'learning_rate':
                        new_particle[key] = np.clip(new_particle[key], 1e-5, 1e-2)
                    elif key == 'dropout_rate':
                        new_particle[key] = np.clip(new_particle[key], 0.1, 0.5)

            new_particles.append(new_particle)
        return new_particles

class AdvancedGAN:
    """Generative Adversarial Network for synthetic market data generation"""
    def __init__(self, sequence_length, feature_dim):
        self.sequence_length = sequence_length
        self.feature_dim = feature_dim
        self.generator = self._build_generator()
        self.discriminator = self._build_discriminator()
        self.gan = self._build_gan()

    def _build_generator(self):
        """Build generator network"""
        noise_input = Input(shape=(100,))
        x = Dense(128, activation='relu')(noise_input)
        x = BatchNormalization()(x)
        x = Dense(256, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dense(self.sequence_length * self.feature_dim, activation='tanh')(x)
        output = tf.reshape(x, (-1, self.sequence_length, self.feature_dim))

        return Model(noise_input, output, name='generator')

    def _build_discriminator(self):
        """Build discriminator network"""
        input_layer = Input(shape=(self.sequence_length, self.feature_dim))
        x = LSTM(128, return_sequences=True)(input_layer)
        x = Dropout(0.3)(x)
        x = LSTM(64)(x)
        x = Dropout(0.3)(x)
        x = Dense(32, activation='relu')(x)
        output = Dense(1, activation='sigmoid')(x)

        return Model(input_layer, output, name='discriminator')

    def _build_gan(self):
        """Build GAN model"""
        self.discriminator.compile(optimizer=Adam(0.0002, 0.5), loss='binary_crossentropy', metrics=['accuracy'])
        self.discriminator.trainable = False

        noise_input = Input(shape=(100,))
        generated_data = self.generator(noise_input)
        validity = self.discriminator(generated_data)

        return Model(noise_input, validity, name='gan')

    def train(self, real_data, epochs=1000, batch_size=32):
        """Train the GAN"""
        for epoch in range(epochs):
            # Train discriminator
            idx = np.random.randint(0, real_data.shape[0], batch_size)
            real_batch = real_data[idx]

            noise = np.random.normal(0, 1, (batch_size, 100))
            fake_batch = self.generator.predict(noise, verbose=0)

            d_loss_real = self.discriminator.train_on_batch(real_batch, np.ones((batch_size, 1)))
            d_loss_fake = self.discriminator.train_on_batch(fake_batch, np.zeros((batch_size, 1)))
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

            # Train generator
            noise = np.random.normal(0, 1, (batch_size, 100))
            g_loss = self.gan.train_on_batch(noise, np.ones((batch_size, 1)))

            if epoch % 100 == 0:
                logger.info(f"GAN Epoch {epoch}, D Loss: {d_loss[0]:.4f}, G Loss: {g_loss:.4f}")

    def generate_synthetic_data(self, num_samples):
        """Generate synthetic market data"""
        noise = np.random.normal(0, 1, (num_samples, 100))
        return self.generator.predict(noise, verbose=0)

class QuantumEliteNeuralPredictor:
    """Advanced neural network predictor with quantum-inspired optimization and GAN augmentation"""

    def __init__(self, model_dir: str = "quantum_elite_models"):
        self.model_dir = model_dir
        self.scaler = RobustScaler()
        self.target_scaler = StandardScaler()
        self.models = {}
        self.sequence_length = 120  # Extended sequence length
        self.prediction_horizons = [1, 3, 6, 12, 24]  # Multiple prediction horizons

        # Initialize advanced components
        self.quantum_optimizer = QuantumInspiredOptimizer()
        self.gan_augmenter = None  # Will be initialized per asset

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        # Model architectures
        self.architectures = {
            'transformer_lstm': self._build_transformer_lstm,
            'attention_cnn': self._build_attention_cnn,
            'ensemble': self._build_ensemble_model
        }

    def _build_transformer_lstm(self, params):
        """Build transformer-LSTM hybrid model"""
        input_layer = Input(shape=(self.sequence_length, None))

        # CNN feature extraction
        cnn_features = Conv1D(filters=64, kernel_size=3, activation='relu')(input_layer)
        cnn_features = MaxPooling1D(pool_size=2)(cnn_features)
        cnn_features = Dropout(params['dropout_rate'])(cnn_features)

        # Transformer blocks
        transformer_input = PositionalEncoding(self.sequence_length // 2, 64)(cnn_features)
        for _ in range(2):
            transformer_input = TransformerBlock(
                embed_dim=64,
                num_heads=params['attention_heads'],
                ff_dim=params['ff_dim'],
                rate=params['dropout_rate']
            )(transformer_input, training=True)

        # LSTM processing
        lstm_out = Bidirectional(LSTM(params['lstm_units'], return_sequences=True))(transformer_input)
        lstm_out = Dropout(params['dropout_rate'])(lstm_out)
        lstm_out = LSTM(params['lstm_units'] // 2)(lstm_out)

        # Output layers for multiple horizons
        outputs = []
        for horizon in self.prediction_horizons:
            dense_out = Dense(32, activation='relu')(lstm_out)
            dense_out = Dropout(params['dropout_rate'])(dense_out)
            output = Dense(1, activation='linear', name=f'output_h{horizon}')(dense_out)
            outputs.append(output)

        model = Model(inputs=input_layer, outputs=outputs)
        optimizer = AdamW(learning_rate=params['learning_rate'], weight_decay=1e-4)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

        return model

    def _build_attention_cnn(self, params):
        """Build attention-based CNN model"""
        input_layer = Input(shape=(self.sequence_length, None))

        # Multi-scale CNN features
        conv1 = Conv1D(32, 3, activation='relu', padding='same')(input_layer)
        conv1 = BatchNormalization()(conv1)
        conv2 = Conv1D(64, 5, activation='relu', padding='same')(input_layer)
        conv2 = BatchNormalization()(conv2)
        conv3 = Conv1D(128, 7, activation='relu', padding='same')(input_layer)
        conv3 = BatchNormalization()(conv3)

        # Concatenate multi-scale features
        concat = Concatenate()([conv1, conv2, conv3])
        concat = Dropout(params['dropout_rate'])(concat)

        # Self-attention mechanism
        attention = MultiHeadAttention(num_heads=params['attention_heads'], key_dim=64)(concat, concat)
        attention = Dropout(params['dropout_rate'])(attention)
        attention = LayerNormalization()(concat + attention)

        # Global pooling and dense layers
        pooled = GlobalAveragePooling1D()(attention)
        dense = Dense(params['ff_dim'], activation='relu')(pooled)
        dense = Dropout(params['dropout_rate'])(dense)

        # Output layers for multiple horizons
        outputs = []
        for horizon in self.prediction_horizons:
            output = Dense(1, activation='linear', name=f'output_h{horizon}')(dense)
            outputs.append(output)

        model = Model(inputs=input_layer, outputs=outputs)
        optimizer = AdamW(learning_rate=params['learning_rate'], weight_decay=1e-4)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

        return model

    def _build_ensemble_model(self, params):
        """Build ensemble model combining multiple architectures"""
        input_layer = Input(shape=(self.sequence_length, None))

        # Multiple model branches
        branch1 = self._build_transformer_lstm(params)(input_layer)
        branch2 = self._build_attention_cnn(params)(input_layer)

        # Ensemble combination
        if isinstance(branch1, list):
            ensemble_outputs = []
            for i, horizon in enumerate(self.prediction_horizons):
                combined = Concatenate()([branch1[i], branch2[i]])
                ensemble_out = Dense(1, activation='linear', name=f'ensemble_h{horizon}')(combined)
                ensemble_outputs.append(ensemble_out)
        else:
            combined = Concatenate()([branch1, branch2])
            ensemble_outputs = Dense(1, activation='linear')(combined)

        model = Model(inputs=input_layer, outputs=ensemble_outputs)
        optimizer = AdamW(learning_rate=params['learning_rate'], weight_decay=1e-4)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

        return model

    def prepare_enhanced_data(self, df: pd.DataFrame, asset_symbol: str) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Prepare enhanced data with GAN augmentation"""
        # Create comprehensive features
        features = self._create_enhanced_features(df)

        # Scale features
        scaled_features = self.scaler.fit_transform(features)

        # Initialize GAN for this asset if not exists
        if self.gan_augmenter is None or asset_symbol not in self.models:
            feature_dim = scaled_features.shape[1]
            self.gan_augmenter = AdvancedGAN(self.sequence_length, feature_dim)

        # Generate synthetic data to augment training
        if len(scaled_features) > self.sequence_length:
            real_sequences = self._create_sequences(scaled_features, np.zeros(len(scaled_features)))
            if len(real_sequences[0]) > 100:  # Only train GAN if we have enough data
                self.gan_augmenter.train(real_sequences[0][:1000], epochs=500)

                # Generate synthetic data
                synthetic_data = self.gan_augmenter.generate_synthetic_data(500)
                augmented_data = np.concatenate([real_sequences[0], synthetic_data])
                augmented_targets = [real_sequences[1]] * len(self.prediction_horizons)  # Same targets for all horizons
            else:
                augmented_data = real_sequences[0]
                augmented_targets = [real_sequences[1]] * len(self.prediction_horizons)
        else:
            augmented_data = self._create_sequences(scaled_features, np.zeros(len(scaled_features)))[0]
            augmented_targets = [np.zeros(len(augmented_data))] * len(self.prediction_horizons)

        # Create targets for multiple horizons
        targets = []
        for horizon in self.prediction_horizons:
            target_values = ((df['close'].shift(-horizon) - df['close']) / df['close']).fillna(0).values
            scaled_target = self.target_scaler.fit_transform(target_values.reshape(-1, 1)).flatten()
            target_sequences = scaled_target[self.sequence_length:]
            targets.append(target_sequences[:len(augmented_data)])

        return augmented_data, targets

    def _create_enhanced_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create enhanced feature set with advanced technical indicators"""
        features = []

        # Price-based features
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                features.extend([
                    df[col].pct_change().fillna(0),
                    df[col].rolling(5).mean().fillna(0),
                    df[col].rolling(20).mean().fillna(0),
                    df[col].rolling(50).mean().fillna(0),
                    df[col].rolling(5).std().fillna(0),
                    df[col].rolling(20).std().fillna(0),
                ])

        # Volume features
        if 'volume' in df.columns:
            vol = df['volume']
            features.extend([
                vol.pct_change().fillna(0),
                vol.rolling(5).mean().fillna(0),
                vol.rolling(20).mean().fillna(0),
                vol / vol.rolling(20).mean().fillna(1),
            ])

        # Advanced technical indicators
        close = df['close']

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        features.append(rsi.fillna(50) / 100.0)

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        features.extend([macd.fillna(0), signal.fillna(0), (macd - signal).fillna(0)])

        # Bollinger Bands
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        bb_upper = sma20 + (2 * std20)
        bb_lower = sma20 - (2 * std20)
        bb_position = (close - bb_lower) / (bb_upper - bb_lower)
        features.extend([bb_upper.fillna(close), bb_lower.fillna(close), bb_position.fillna(0.5)])

        # Stochastic Oscillator
        lowest_low = close.rolling(14).min()
        highest_high = close.rolling(14).max()
        stoch_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        stoch_d = stoch_k.rolling(3).mean()
        features.extend([stoch_k.fillna(50) / 100.0, stoch_d.fillna(50) / 100.0])

        # Williams %R
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        features.append(williams_r.fillna(-50) / 100.0 + 0.5)

        # Commodity Channel Index (CCI)
        typical_price = (close + df['high'] + df['low']) / 3
        sma_tp = typical_price.rolling(20).mean()
        mad = (typical_price - sma_tp).abs().rolling(20).mean()
        cci = (typical_price - sma_tp) / (0.015 * mad)
        features.append(cci.fillna(0) / 100.0)

        # Momentum indicators
        for period in [5, 10, 15, 20]:
            features.append(close.pct_change(period).fillna(0))

        # Volatility measures
        returns = close.pct_change().fillna(0)
        for period in [5, 10, 20]:
            features.append(returns.rolling(period).std().fillna(0))

        # Volume indicators (if volume exists)
        if 'volume' in df.columns:
            # On-Balance Volume (OBV)
            obv = (np.sign(close.diff()) * vol).fillna(0).cumsum()
            features.append(obv / obv.abs().max() if obv.abs().max() > 0 else obv)

            # Volume Rate of Change
            features.append(vol.pct_change(10).fillna(0))

        return np.column_stack(features)

    def _create_sequences(self, features: np.ndarray, targets: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for time series prediction"""
        X, y = [], []
        for i in range(len(features) - self.sequence_length):
            X.append(features[i:i + self.sequence_length])
            y.append(targets[i + self.sequence_length])
        return np.array(X), np.array(y)

    def train_quantum_optimized_model(self, df: pd.DataFrame, asset_symbol: str) -> Dict[str, Any]:
        """Train model with quantum-inspired optimization"""
        logger.info(f"Training quantum-optimized model for {asset_symbol}")

        # Prepare data with GAN augmentation
        X, y_list = self.prepare_enhanced_data(df, asset_symbol)

        # Create validation split
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train_list = [y[:split_idx] for y in y_list]
        y_val_list = [y[split_idx:] for y in y_list]

        validation_data = (X_val, y_val_list) if len(X_val) > 0 else None

        # Quantum-inspired hyperparameter optimization
        def model_builder(params):
            return self._build_transformer_lstm(params)

        best_params = self.quantum_optimizer.optimize_hyperparameters(
            model_builder, X_train, y_train_list, validation_data
        )

        # Train final model with best parameters
        final_model = model_builder(best_params)

        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ModelCheckpoint(
                f"{self.model_dir}/{asset_symbol}_quantum_elite.h5",
                monitor='val_loss',
                save_best_only=True
            ),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
        ]

        history = final_model.fit(
            X_train, y_train_list,
            validation_data=validation_data,
            epochs=200,
            batch_size=best_params['batch_size'],
            callbacks=callbacks,
            verbose=1
        )

        # Save model and scalers
        model_path = f"{self.model_dir}/{asset_symbol}_quantum_elite"
        final_model.save(model_path)
        joblib.dump(self.scaler, f"{model_path}_scaler.pkl")
        joblib.dump(self.target_scaler, f"{model_path}_target_scaler.pkl")

        self.models[asset_symbol] = {
            'model': final_model,
            'scaler': self.scaler,
            'target_scaler': self.target_scaler,
            'params': best_params,
            'training_history': history.history
        }

        logger.info(f"Quantum Elite model trained for {asset_symbol} with validation loss: {min(history.history['val_loss']):.4f}")

        return self.models[asset_symbol]

    def predict_multi_horizon(self, df: pd.DataFrame, asset_symbol: str) -> Dict[str, Dict[str, float]]:
        """Make multi-horizon predictions with confidence intervals"""
        if asset_symbol not in self.models:
            raise ValueError(f"Model not trained for {asset_symbol}")

        model_info = self.models[asset_symbol]
        model = model_info['model']
        scaler = model_info['scaler']
        target_scaler = model_info['target_scaler']

        # Prepare recent data
        features = self._create_enhanced_features(df)
        if len(features) < self.sequence_length:
            raise ValueError("Insufficient data for prediction")

        # Scale features
        scaled_features = scaler.transform(features[-self.sequence_length:])
        X_pred = scaled_features.reshape(1, self.sequence_length, -1)

        # Make predictions
        predictions = model.predict(X_pred, verbose=0)

        # Inverse transform predictions
        results = {}
        for i, horizon in enumerate(self.prediction_horizons):
            pred_value = predictions[i][0][0] if isinstance(predictions[i], np.ndarray) and predictions[i].ndim > 1 else predictions[i][0]
            pred_scaled = target_scaler.inverse_transform([[pred_value]])[0][0]

            # Calculate confidence intervals using model uncertainty
            confidence = self._calculate_prediction_confidence(model, X_pred, horizon)

            results[f'h{horizon}'] = {
                'prediction': pred_scaled,
                'confidence': confidence,
                'direction': 'bullish' if pred_scaled > 0.001 else 'bearish' if pred_scaled < -0.001 else 'neutral',
                'magnitude': abs(pred_scaled)
            }

        return results

    def _calculate_prediction_confidence(self, model, X, horizon_idx: int) -> float:
        """Calculate prediction confidence using Monte Carlo dropout"""
        # Enable dropout during inference for uncertainty estimation
        predictions = []
        for _ in range(50):  # Monte Carlo samples
            pred = model(X, training=True)
            if isinstance(pred, list):
                pred_value = pred[horizon_idx].numpy().flatten()[0]
            else:
                pred_value = pred.numpy().flatten()[0]
            predictions.append(pred_value)

        predictions = np.array(predictions)
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)

        # Confidence based on inverse of coefficient of variation
        confidence = 1.0 / (1.0 + abs(std_pred / (abs(mean_pred) + 1e-6)))
        return min(confidence, 0.95)  # Cap at 95%

    def get_model_performance_metrics(self, asset_symbol: str) -> Dict[str, Any]:
        """Get comprehensive performance metrics for the model"""
        if asset_symbol not in self.models:
            return {}

        model_info = self.models[asset_symbol]
        history = model_info.get('training_history', {})

        metrics = {
            'final_training_loss': history.get('loss', [])[-1] if history.get('loss') else None,
            'final_validation_loss': history.get('val_loss', [])[-1] if history.get('val_loss') else None,
            'best_validation_loss': min(history.get('val_loss', [float('inf')])) if history.get('val_loss') else None,
            'training_epochs': len(history.get('loss', [])),
            'hyperparameters': model_info.get('params', {}),
            'model_type': 'Quantum Elite Transformer-LSTM with GAN Augmentation',
            'features_count': self.scaler.n_features_in_ if hasattr(self.scaler, 'n_features_in_') else None,
            'sequence_length': self.sequence_length,
            'prediction_horizons': self.prediction_horizons
        }

        return metrics

    def generate_signal_enhancement(self, df: pd.DataFrame, asset_symbol: str,
                                  base_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance trading signals with AI predictions"""
        try:
            predictions = self.predict_multi_horizon(df, asset_symbol)

            # Combine predictions across horizons for signal strength
            short_term = predictions['h1']
            medium_term = predictions['h3']
            long_term = predictions['h6']

            # Calculate composite signal strength
            signal_weights = {'short': 0.5, 'medium': 0.3, 'long': 0.2}
            composite_direction = np.average([
                1 if short_term['direction'] == 'bullish' else -1 if short_term['direction'] == 'bearish' else 0,
                1 if medium_term['direction'] == 'bullish' else -1 if medium_term['direction'] == 'bearish' else 0,
                1 if long_term['direction'] == 'bullish' else -1 if long_term['direction'] == 'bearish' else 0
            ], weights=[signal_weights['short'], signal_weights['medium'], signal_weights['long']])

            composite_magnitude = np.average([
                short_term['magnitude'],
                medium_term['magnitude'],
                long_term['magnitude']
            ], weights=[signal_weights['short'], signal_weights['medium'], signal_weights['long']])

            composite_confidence = np.average([
                short_term['confidence'],
                medium_term['confidence'],
                long_term['confidence']
            ], weights=[signal_weights['short'], signal_weights['medium'], signal_weights['long']])

            # Enhance original signal
            enhanced_signal = base_signal.copy()
            enhanced_signal.update({
                'ai_enhanced': True,
                'quantum_elite_prediction': predictions,
                'composite_direction': 'bullish' if composite_direction > 0.1 else 'bearish' if composite_direction < -0.1 else 'neutral',
                'composite_strength': abs(composite_direction),
                'composite_magnitude': composite_magnitude,
                'ai_confidence': composite_confidence,
                'enhancement_timestamp': datetime.now().isoformat(),
                'model_version': 'Quantum Elite v2.0'
            })

            return enhanced_signal

        except Exception as e:
            logger.warning(f"AI enhancement failed for {asset_symbol}: {e}")
            return base_signal
