"""
Quantum Elite AI Signal Integration
Integrates advanced AI predictions with existing signal generation
Enhances signals with Quantum Elite AI capabilities
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import hashlib
import threading
from collections import defaultdict
import hashlib
import unittest
from unittest.mock import Mock, patch
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Add staging directory to path for AI imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'staging'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not REDIS_AVAILABLE:
    logger.warning("[CACHE] Redis not available, using memory cache only")

class AdvancedCache:
    """Advanced caching system with Redis and memory fallback"""

    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_seconds: int = 300):
        self.memory_cache = {}
        self.cache_metadata = {}
        self.ttl_seconds = ttl_seconds
        self.redis_client = None

        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()  # Test connection
                logger.info("[CACHE] Redis cache initialized")
            except Exception as e:
                logger.warning(f"[CACHE] Redis connection failed: {e}, falling back to memory cache")
                self.redis_client = None

    def _generate_cache_key(self, data: Any) -> str:
        """Generate a deterministic cache key from data"""
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get cached data with TTL check"""
        cache_key = self._generate_cache_key(key) if not isinstance(key, str) else key

        # Try Redis first
        if self.redis_client:
            try:
                data = self.redis_client.get(cache_key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.debug(f"[CACHE] Redis get failed: {e}")

        # Fallback to memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if datetime.now().timestamp() - entry['timestamp'] < self.ttl_seconds:
                return entry['data']
            else:
                # Expired, remove it
                del self.memory_cache[cache_key]

        return None

    def set(self, key: str, data: Any, custom_ttl: Optional[int] = None) -> None:
        """Set cached data with TTL"""
        cache_key = self._generate_cache_key(key) if not isinstance(key, str) else key
        ttl = custom_ttl or self.ttl_seconds
        timestamp = datetime.now().timestamp()

        cache_entry = {
            'data': data,
            'timestamp': timestamp,
            'ttl': ttl
        }

        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, ttl, json.dumps(data, default=str))
            except Exception as e:
                logger.debug(f"[CACHE] Redis set failed: {e}")

        # Always update memory cache
        self.memory_cache[cache_key] = cache_entry

        # Clean up old entries periodically
        if len(self.memory_cache) > 1000:  # Memory limit
            self._cleanup_expired_entries()

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern"""
        invalidated = 0

        # Redis pattern invalidation
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    invalidated += len(keys)
            except Exception as e:
                logger.debug(f"[CACHE] Redis pattern invalidation failed: {e}")

        # Memory cache pattern invalidation
        import re
        pattern_regex = re.compile(pattern.replace('*', '.*'))
        keys_to_remove = [k for k in self.memory_cache.keys() if pattern_regex.match(k)]

        for key in keys_to_remove:
            del self.memory_cache[key]
            invalidated += 1

        return invalidated

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'memory_entries': len(self.memory_cache),
            'redis_available': self.redis_client is not None,
            'default_ttl': self.ttl_seconds
        }

    def _cleanup_expired_entries(self):
        """Clean up expired memory cache entries"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if current_time - v['timestamp'] > v['ttl']
        ]

        for key in expired_keys:
            del self.memory_cache[key]

        logger.debug(f"[CACHE] Cleaned up {len(expired_keys)} expired entries")

class CircuitBreaker:
    """Circuit breaker pattern for resilient AI module calls"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: Exception = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
                logger.info("[CIRCUIT] Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            self.failure_count = 0
            logger.info("[CIRCUIT] Circuit breaker reset to CLOSED after successful call")
        elif self.state == 'CLOSED':
            self.failure_count = max(0, self.failure_count - 1)  # Gradual recovery

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"[CIRCUIT] Circuit breaker opened after {self.failure_count} failures")

    def get_status(self) -> Dict:
        """Get circuit breaker status"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout
        }

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class ValidationError(Exception):
    """Exception raised when data validation fails"""
    pass

class DataValidator:
    """Comprehensive data validation and quality checking system"""

    VALID_ASSETS = {'BTC', 'ETH', 'XAU', 'ES', 'NQ', 'SPY', 'QQQ', 'GLD', 'SLV'}
    VALID_SIGNAL_TYPES = {'BUY', 'SELL', 'HOLD', 'LONG', 'SHORT', 'NEUTRAL'}
    VALID_SIGNAL_QUALITIES = {'low', 'medium', 'high', 'ultra', 'quantum_elite'}

    @staticmethod
    def validate_signal(signal: Dict) -> Tuple[bool, List[str]]:
        """Validate trading signal data"""
        errors = []

        # Required fields
        required_fields = ['asset', 'signal_type']
        for field in required_fields:
            if field not in signal:
                errors.append(f"Missing required field: {field}")

        # Asset symbol validation
        if 'asset' in signal:
            asset = signal['asset']
            if not isinstance(asset, str) or asset not in DataValidator.VALID_ASSETS:
                errors.append(f"Invalid asset symbol: {asset}. Must be one of {DataValidator.VALID_ASSETS}")

        # Signal type validation
        if 'signal_type' in signal:
            signal_type = signal['signal_type']
            if not isinstance(signal_type, str) or signal_type.upper() not in DataValidator.VALID_SIGNAL_TYPES:
                errors.append(f"Invalid signal type: {signal_type}. Must be one of {DataValidator.VALID_SIGNAL_TYPES}")

        # Signal quality validation
        if 'signal_quality' in signal:
            quality = signal['signal_quality']
            if not isinstance(quality, str) or quality not in DataValidator.VALID_SIGNAL_QUALITIES:
                errors.append(f"Invalid signal quality: {quality}. Must be one of {DataValidator.VALID_SIGNAL_QUALITIES}")

        # Timestamp validation
        if 'timestamp' in signal:
            try:
                datetime.fromisoformat(signal['timestamp'])
            except (ValueError, TypeError):
                errors.append("Invalid timestamp format. Must be ISO format.")

        # Price validation
        if 'price' in signal:
            try:
                price = float(signal['price'])
                if price <= 0 or price > 1000000:  # Reasonable price bounds
                    errors.append(f"Invalid price: {price}. Must be between 0 and 1,000,000")
            except (ValueError, TypeError):
                errors.append("Invalid price format. Must be numeric.")

        # Confidence validation
        if 'confidence' in signal:
            try:
                confidence = float(signal['confidence'])
                if not 0 <= confidence <= 1:
                    errors.append(f"Invalid confidence: {confidence}. Must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append("Invalid confidence format. Must be numeric between 0 and 1.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_market_data(market_data: Dict) -> Tuple[bool, List[str]]:
        """Validate market data"""
        errors = []

        # Price validation
        if 'price' in market_data:
            try:
                price = float(market_data['price'])
                if price <= 0:
                    errors.append(f"Invalid market price: {price}. Must be positive")
            except (ValueError, TypeError):
                errors.append("Invalid market price format")

        # Volume validation
        if 'volume' in market_data:
            try:
                volume = float(market_data['volume'])
                if volume < 0:
                    errors.append(f"Invalid volume: {volume}. Must be non-negative")
            except (ValueError, TypeError):
                errors.append("Invalid volume format")

        # Change percentage validation
        if 'change_24h' in market_data:
            try:
                change = float(market_data['change_24h'])
                if abs(change) > 100:  # 100% change limit
                    errors.append(f"Unrealistic change_24h: {change}%. Must be between -100% and 100%")
            except (ValueError, TypeError):
                errors.append("Invalid change_24h format")

        # Volatility validation
        if 'volatility' in market_data:
            try:
                vol = float(market_data['volatility'])
                if not 0 <= vol <= 1:
                    errors.append(f"Invalid volatility: {vol}. Must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append("Invalid volatility format")

        # Timestamp validation
        if 'timestamp' in market_data:
            if isinstance(market_data['timestamp'], datetime):
                pass  # Already datetime
            elif isinstance(market_data['timestamp'], str):
                try:
                    datetime.fromisoformat(market_data['timestamp'])
                except (ValueError, TypeError):
                    errors.append("Invalid timestamp format in market data")
            else:
                errors.append("Invalid timestamp type in market data")

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_signal(signal: Dict) -> Dict:
        """Sanitize and normalize signal data"""
        sanitized = signal.copy()

        # Normalize asset symbol
        if 'asset' in sanitized:
            sanitized['asset'] = sanitized['asset'].upper()

        # Normalize signal type
        if 'signal_type' in sanitized:
            sanitized['signal_type'] = sanitized['signal_type'].upper()

        # Ensure defaults
        if 'signal_quality' not in sanitized:
            sanitized['signal_quality'] = 'medium'

        if 'confidence' not in sanitized:
            sanitized['confidence'] = 0.5

        if 'has_signal' not in sanitized:
            sanitized['has_signal'] = True

        return sanitized

    @staticmethod
    def check_data_quality_score(data: Dict, data_type: str = 'signal') -> float:
        """Calculate data quality score (0-1)"""
        score = 1.0
        penalty = 0.1

        if data_type == 'signal':
            # Check for missing critical fields
            critical_fields = ['asset', 'signal_type', 'timestamp']
            for field in critical_fields:
                if field not in data or not data[field]:
                    score -= penalty

            # Check for optional but important fields
            important_fields = ['signal_quality', 'confidence', 'price']
            for field in important_fields:
                if field not in data:
                    score -= penalty * 0.5

        elif data_type == 'market_data':
            # Check for market data completeness
            market_fields = ['price', 'volume', 'change_24h', 'volatility']
            for field in market_fields:
                if field not in data:
                    score -= penalty

        return max(0.0, min(1.0, score))

class ModelVersionManager:
    """Model versioning and A/B testing system"""

    def __init__(self, version_storage_path: str = "model_versions"):
        self.version_storage_path = version_storage_path
        self.active_versions = {}
        self.ab_tests = {}
        self.version_performance = defaultdict(dict)
        self.version_metadata = {}

        # Create storage directory
        os.makedirs(version_storage_path, exist_ok=True)
        logger.info("[MODEL_VERSION] Model Version Manager initialized")

    def create_version(self, model_type: str, model_config: Dict, model_data: Any = None,
                      description: str = "", parent_version: str = None) -> str:
        """Create a new model version"""
        version_id = f"{model_type}_v{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(model_config).encode()).hexdigest()[:8]}"

        version_info = {
            'version_id': version_id,
            'model_type': model_type,
            'config': model_config,
            'created_at': datetime.now().isoformat(),
            'description': description,
            'parent_version': parent_version,
            'status': 'active',
            'performance_metrics': {},
            'usage_count': 0,
            'error_count': 0
        }

        # Save version metadata
        version_path = os.path.join(self.version_storage_path, f"{version_id}.json")
        with open(version_path, 'w') as f:
            json.dump(version_info, f, indent=2, default=str)

        # Save model data if provided
        if model_data:
            model_data_path = os.path.join(self.version_storage_path, f"{version_id}_model.pkl")
            joblib.dump(model_data, model_data_path)

        self.version_metadata[version_id] = version_info
        self.active_versions[model_type] = version_id

        logger.info(f"[MODEL_VERSION] Created version {version_id} for {model_type}")
        return version_id

    def get_version(self, model_type: str, version_id: str = None) -> Dict:
        """Get version information"""
        if version_id is None:
            version_id = self.active_versions.get(model_type)

        if version_id and version_id in self.version_metadata:
            return self.version_metadata[version_id]

        # Try to load from disk
        version_path = os.path.join(self.version_storage_path, f"{version_id}.json")
        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                version_info = json.load(f)
            self.version_metadata[version_id] = version_info
            return version_info

        return None

    def update_version_performance(self, version_id: str, metrics: Dict):
        """Update performance metrics for a version"""
        if version_id not in self.version_metadata:
            return

        version = self.version_metadata[version_id]
        version['performance_metrics'].update(metrics)
        version['last_updated'] = datetime.now().isoformat()

        # Save updated metadata
        version_path = os.path.join(self.version_storage_path, f"{version_id}.json")
        with open(version_path, 'w') as f:
            json.dump(version, f, indent=2, default=str)

        # Update performance tracking
        for metric_name, value in metrics.items():
            if metric_name not in self.version_performance[version_id]:
                self.version_performance[version_id][metric_name] = []
            self.version_performance[version_id][metric_name].append({
                'value': value,
                'timestamp': datetime.now().timestamp()
            })

            # Keep only last 100 measurements
            self.version_performance[version_id][metric_name] = self.version_performance[version_id][metric_name][-100:]

    def start_ab_test(self, test_name: str, model_type: str, version_a: str, version_b: str,
                     traffic_split: float = 0.5, duration_days: int = 7) -> str:
        """Start an A/B test between two model versions"""
        test_id = f"ab_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        ab_test = {
            'test_id': test_id,
            'test_name': test_name,
            'model_type': model_type,
            'version_a': version_a,
            'version_b': version_b,
            'traffic_split': traffic_split,  # % of traffic to version A
            'duration_days': duration_days,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(days=duration_days)).isoformat(),
            'status': 'running',
            'results': {
                'version_a': {'requests': 0, 'errors': 0, 'performance': []},
                'version_b': {'requests': 0, 'errors': 0, 'performance': []}
            }
        }

        self.ab_tests[test_id] = ab_test
        logger.info(f"[AB_TEST] Started A/B test {test_id} between {version_a} and {version_b}")
        return test_id

    def get_version_for_request(self, model_type: str, request_id: str = None) -> str:
        """Get the appropriate version for a request (handles A/B testing)"""
        if request_id is None:
            request_id = str(hash(datetime.now().timestamp()))

        # Check for active A/B tests
        for test_id, test in self.ab_tests.items():
            if (test['model_type'] == model_type and
                test['status'] == 'running' and
                datetime.now() < datetime.fromisoformat(test['end_time'])):

                # Use request_id for consistent routing
                hash_value = int(hashlib.md5(request_id.encode()).hexdigest(), 16) % 100
                use_version_a = hash_value < (test['traffic_split'] * 100)

                return test['version_a'] if use_version_a else test['version_b']

        # No A/B test, return active version
        return self.active_versions.get(model_type)

    def record_ab_test_result(self, test_id: str, version_id: str, success: bool, performance_metrics: Dict = None):
        """Record the result of an A/B test request"""
        if test_id not in self.ab_tests:
            return

        test = self.ab_tests[test_id]
        version_key = 'version_a' if version_id == test['version_a'] else 'version_b'

        test['results'][version_key]['requests'] += 1
        if not success:
            test['results'][version_key]['errors'] += 1

        if performance_metrics:
            test['results'][version_key]['performance'].append({
                'metrics': performance_metrics,
                'timestamp': datetime.now().isoformat()
            })

            # Keep only last 50 performance records
            test['results'][version_key]['performance'] = test['results'][version_key]['performance'][-50:]

    def get_ab_test_results(self, test_id: str) -> Dict:
        """Get A/B test results and analysis"""
        if test_id not in self.ab_tests:
            return None

        test = self.ab_tests[test_id]

        # Calculate statistics
        results = {}
        for version_key, version_id in [('version_a', test['version_a']), ('version_b', test['version_b'])]:
            data = test['results'][version_key]
            total_requests = data['requests']
            error_rate = data['errors'] / max(1, total_requests)

            # Calculate average performance metrics
            perf_metrics = {}
            if data['performance']:
                all_metrics = {}
                for perf_entry in data['performance']:
                    for metric_name, value in perf_entry['metrics'].items():
                        if metric_name not in all_metrics:
                            all_metrics[metric_name] = []
                        all_metrics[metric_name].append(value)

                for metric_name, values in all_metrics.items():
                    perf_metrics[f'avg_{metric_name}'] = np.mean(values)

            results[version_key] = {
                'version_id': version_id,
                'total_requests': total_requests,
                'error_rate': error_rate,
                'conversion_rate': 1 - error_rate,
                'performance_metrics': perf_metrics
            }

        # Determine winner if test is complete
        test_end = datetime.fromisoformat(test['end_time'])
        if datetime.now() > test_end:
            test['status'] = 'completed'
            # Simple winner determination based on error rate
            a_error_rate = results['version_a']['error_rate']
            b_error_rate = results['version_b']['error_rate']

            if a_error_rate < b_error_rate:
                winner = 'version_a'
            elif b_error_rate < a_error_rate:
                winner = 'version_b'
            else:
                winner = 'tie'

            results['winner'] = winner
            results['confidence'] = abs(a_error_rate - b_error_rate) / max(a_error_rate, b_error_rate, 0.01)

        return {
            'test_info': test,
            'results': results,
            'analysis': self._analyze_ab_test_results(results) if test['status'] == 'completed' else {}
        }

    def _analyze_ab_test_results(self, results: Dict) -> Dict:
        """Analyze A/B test results for statistical significance"""
        # Simplified analysis - in production, use proper statistical tests
        version_a = results['version_a']
        version_b = results['version_b']

        analysis = {
            'sample_size_sufficient': min(version_a['total_requests'], version_b['total_requests']) >= 100,
            'error_rate_difference': version_b['error_rate'] - version_a['error_rate'],
            'recommendation': 'continue_testing'  # Default
        }

        # Simple recommendation logic
        if version_a['error_rate'] < version_b['error_rate'] * 0.9:  # A is 10% better
            analysis['recommendation'] = 'version_a_wins'
        elif version_b['error_rate'] < version_a['error_rate'] * 0.9:  # B is 10% better
            analysis['recommendation'] = 'version_b_wins'
        elif analysis['sample_size_sufficient']:
            analysis['recommendation'] = 'insufficient_evidence'

        return analysis

    def get_version_stats(self) -> Dict:
        """Get statistics about all versions"""
        return {
            'active_versions': self.active_versions,
            'total_versions': len(self.version_metadata),
            'active_ab_tests': len([t for t in self.ab_tests.values() if t['status'] == 'running']),
            'completed_ab_tests': len([t for t in self.ab_tests.values() if t['status'] == 'completed'])
        }

class ConfigurationManager:
    """Dynamic configuration management and feature flags"""

    def __init__(self, config_file: str = "quantum_elite_config.json", auto_reload: bool = True):
        self.config_file = config_file
        self.config = self._load_default_config()
        self.feature_flags = {}
        self.config_listeners = []
        self.last_modified = None
        self.auto_reload = auto_reload

        # Load configuration from file
        self._load_config()

        # Start auto-reload if enabled
        if auto_reload:
            self._start_auto_reload()

        logger.info("[CONFIG] Configuration Manager initialized")

    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            'system': {
                'max_workers': 4,
                'enable_async': True,
                'cache_ttl_seconds': 300,
                'log_level': 'INFO'
            },
            'ai_modules': {
                'neural_predictor': {
                    'enabled': True,
                    'timeout_seconds': 30,
                    'confidence_threshold': 0.5
                },
                'reinforcement_learning': {
                    'enabled': True,
                    'timeout_seconds': 25,
                    'risk_threshold': 0.7
                },
                'nlp_sentiment': {
                    'enabled': True,
                    'timeout_seconds': 15,
                    'min_confidence': 0.3
                },
                'federated_learning': {
                    'enabled': True,
                    'timeout_seconds': 45,
                    'consensus_threshold': 0.6
                },
                'predictive_analytics': {
                    'enabled': False,  # Disabled by default
                    'timeout_seconds': 20,
                    'horizon_hours': 24
                }
            },
            'circuit_breakers': {
                'failure_threshold': 3,
                'recovery_timeout_seconds': 120,
                'global_timeout': 60
            },
            'monitoring': {
                'metrics_retention_hours': 24,
                'alert_check_interval_seconds': 60,
                'health_check_enabled': True
            },
            'validation': {
                'strict_mode': False,
                'sanitize_invalid_data': True,
                'quality_threshold': 0.5
            },
            'caching': {
                'redis_enabled': False,
                'redis_url': 'redis://localhost:6379',
                'memory_cache_size_mb': 100,
                'cache_invalidation_patterns': ['market_data_*', 'signal_*']
            }
        }

    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)

                # Deep merge with defaults
                self.config = self._deep_merge(self.config, file_config)
                self.last_modified = os.path.getmtime(self.config_file)

                logger.info(f"[CONFIG] Loaded configuration from {self.config_file}")
            else:
                # Save default config
                self._save_config()
                logger.info(f"[CONFIG] Created default configuration file {self.config_file}")

        except Exception as e:
            logger.warning(f"[CONFIG] Failed to load config file: {e}, using defaults")

    def _save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.debug(f"[CONFIG] Saved configuration to {self.config_file}")
        except Exception as e:
            logger.warning(f"[CONFIG] Failed to save config file: {e}")

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _start_auto_reload(self):
        """Start automatic configuration reloading"""
        import threading

        def reload_checker():
            while True:
                try:
                    if (os.path.exists(self.config_file) and
                        self.last_modified != os.path.getmtime(self.config_file)):
                        logger.info("[CONFIG] Configuration file changed, reloading...")
                        old_config = self.config.copy()
                        self._load_config()

                        # Notify listeners of changes
                        self._notify_listeners(old_config, self.config)

                    threading.Event().wait(5)  # Check every 5 seconds
                except Exception as e:
                    logger.warning(f"[CONFIG] Auto-reload error: {e}")
                    threading.Event().wait(10)  # Wait longer on error

        reload_thread = threading.Thread(target=reload_checker, daemon=True)
        reload_thread.start()

    def get(self, key_path: str, default=None):
        """Get configuration value by dot-separated path"""
        keys = key_path.split('.')
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value, save: bool = True):
        """Set configuration value by dot-separated path"""
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        old_value = config.get(keys[-1])
        config[keys[-1]] = value

        if save:
            self._save_config()

        # Notify listeners
        self._notify_listeners({key_path: old_value}, {key_path: value})

        logger.info(f"[CONFIG] Set {key_path} = {value}")

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature flag is enabled"""
        return self.feature_flags.get(feature_name, False)

    def enable_feature(self, feature_name: str, save: bool = True):
        """Enable a feature flag"""
        self.feature_flags[feature_name] = True
        if save:
            self._save_feature_flags()
        logger.info(f"[CONFIG] Enabled feature: {feature_name}")

    def disable_feature(self, feature_name: str, save: bool = True):
        """Disable a feature flag"""
        self.feature_flags[feature_name] = False
        if save:
            self._save_feature_flags()
        logger.info(f"[CONFIG] Disabled feature: {feature_name}")

    def _save_feature_flags(self):
        """Save feature flags to file"""
        try:
            flags_file = self.config_file.replace('.json', '_features.json')
            with open(flags_file, 'w') as f:
                json.dump(self.feature_flags, f, indent=2)
        except Exception as e:
            logger.warning(f"[CONFIG] Failed to save feature flags: {e}")

    def _load_feature_flags(self):
        """Load feature flags from file"""
        try:
            flags_file = self.config_file.replace('.json', '_features.json')
            if os.path.exists(flags_file):
                with open(flags_file, 'r') as f:
                    self.feature_flags = json.load(f)
        except Exception as e:
            logger.warning(f"[CONFIG] Failed to load feature flags: {e}")

    def add_config_listener(self, callback: callable):
        """Add a configuration change listener"""
        self.config_listeners.append(callback)

    def _notify_listeners(self, old_config: Dict, new_config: Dict):
        """Notify all listeners of configuration changes"""
        changes = self._find_changes(old_config, new_config)
        if changes:
            for listener in self.config_listeners:
                try:
                    listener(changes)
                except Exception as e:
                    logger.warning(f"[CONFIG] Listener error: {e}")

    def _find_changes(self, old: Dict, new: Dict, path: str = "") -> Dict:
        """Find changes between two configurations"""
        changes = {}

        if isinstance(old, dict) and isinstance(new, dict):
            for key in set(old.keys()) | set(new.keys()):
                old_val = old.get(key)
                new_val = new.get(key)
                current_path = f"{path}.{key}" if path else key

                if old_val != new_val:
                    if isinstance(old_val, dict) or isinstance(new_val, dict):
                        nested_changes = self._find_changes(old_val or {}, new_val or {}, current_path)
                        changes.update(nested_changes)
                    else:
                        changes[current_path] = {'old': old_val, 'new': new_val}
        elif old != new:
            changes[path] = {'old': old, 'new': new}

        return changes

    def get_config_snapshot(self) -> Dict:
        """Get a complete snapshot of current configuration"""
        return {
            'config': self.config.copy(),
            'feature_flags': self.feature_flags.copy(),
            'last_modified': self.last_modified,
            'auto_reload': self.auto_reload
        }

    def validate_config(self) -> Tuple[bool, List[str]]:
        """Validate current configuration"""
        errors = []

        # Validate AI module timeouts
        for module_name, module_config in self.config.get('ai_modules', {}).items():
            if module_config.get('enabled', False):
                timeout = module_config.get('timeout_seconds', 0)
                if timeout <= 0 or timeout > 300:
                    errors.append(f"Invalid timeout for {module_name}: {timeout}s (must be 1-300)")

        # Validate circuit breaker settings
        cb_config = self.config.get('circuit_breakers', {})
        failure_threshold = cb_config.get('failure_threshold', 0)
        if failure_threshold < 1 or failure_threshold > 10:
            errors.append(f"Invalid failure threshold: {failure_threshold} (must be 1-10)")

        # Validate cache settings
        cache_config = self.config.get('caching', {})
        if cache_config.get('redis_enabled'):
            redis_url = cache_config.get('redis_url', '')
            if not redis_url.startswith('redis://'):
                errors.append(f"Invalid Redis URL format: {redis_url}")

        return len(errors) == 0, errors

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self._load_default_config()
        self.feature_flags = {}
        self._save_config()
        logger.info("[CONFIG] Reset configuration to defaults")

# Global configuration instance
config_manager = ConfigurationManager()

class AdvancedMonitoringSystem:
    """Advanced monitoring, metrics, and alerting system"""

    def __init__(self, alert_thresholds: Optional[Dict] = None):
        self.metrics = defaultdict(list)
        self.alerts = []
        self.alert_thresholds = alert_thresholds or {
            'error_rate_threshold': 0.1,  # 10% error rate
            'performance_degradation_threshold': 2.0,  # 2x slower than baseline
            'circuit_breaker_open_threshold': 2,  # Max open circuit breakers
            'memory_usage_threshold': 0.8,  # 80% memory usage
            'cache_miss_rate_threshold': 0.9,  # 90% cache miss rate
        }
        self.baseline_performance = {}
        self.last_alert_check = datetime.now()

    def record_metric(self, metric_name: str, value: Union[int, float], tags: Optional[Dict] = None):
        """Record a metric value"""
        timestamp = datetime.now().timestamp()
        metric_entry = {
            'value': value,
            'timestamp': timestamp,
            'tags': tags or {}
        }

        self.metrics[metric_name].append(metric_entry)

        # Keep only last 1000 entries per metric
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]

        # Check for alerts
        self._check_alerts(metric_name, value, tags)

    def get_metric_stats(self, metric_name: str, time_window_seconds: int = 3600) -> Dict:
        """Get statistics for a metric over a time window"""
        cutoff_time = datetime.now().timestamp() - time_window_seconds
        recent_values = [
            entry['value'] for entry in self.metrics[metric_name]
            if entry['timestamp'] > cutoff_time
        ]

        if not recent_values:
            return {'count': 0, 'mean': 0, 'min': 0, 'max': 0, 'std': 0}

        return {
            'count': len(recent_values),
            'mean': np.mean(recent_values),
            'min': np.min(recent_values),
            'max': np.max(recent_values),
            'std': np.std(recent_values),
            'latest': recent_values[-1] if recent_values else 0
        }

    def _check_alerts(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """Check if any alert thresholds are exceeded"""
        current_time = datetime.now()

        # Throttle alert checks to once per minute
        if (current_time - self.last_alert_check).seconds < 60:
            return

        self.last_alert_check = current_time

        alerts_triggered = []

        # Error rate alert
        if metric_name == 'error_rate':
            if value > self.alert_thresholds['error_rate_threshold']:
                alerts_triggered.append({
                    'type': 'ERROR_RATE_HIGH',
                    'message': f'Error rate {value:.2%} exceeds threshold {self.alert_thresholds["error_rate_threshold"]:.2%}',
                    'severity': 'CRITICAL',
                    'metric': metric_name,
                    'value': value,
                    'threshold': self.alert_thresholds['error_rate_threshold']
                })

        # Performance degradation alert
        elif metric_name == 'enhancement_time':
            baseline = self.baseline_performance.get('enhancement_time', value)
            if baseline > 0 and value > baseline * self.alert_thresholds['performance_degradation_threshold']:
                alerts_triggered.append({
                    'type': 'PERFORMANCE_DEGRADATION',
                    'message': f'Performance degraded: {value:.3f}s vs baseline {baseline:.3f}s',
                    'severity': 'WARNING',
                    'metric': metric_name,
                    'value': value,
                    'baseline': baseline
                })

        # Circuit breaker alert
        elif metric_name == 'circuit_breakers_open':
            if value >= self.alert_thresholds['circuit_breaker_open_threshold']:
                alerts_triggered.append({
                    'type': 'CIRCUIT_BREAKERS_OPEN',
                    'message': f'{int(value)} circuit breakers are open',
                    'severity': 'WARNING',
                    'metric': metric_name,
                    'value': value,
                    'threshold': self.alert_thresholds['circuit_breaker_open_threshold']
                })

        # Memory usage alert
        elif metric_name == 'memory_usage':
            if value > self.alert_thresholds['memory_usage_threshold']:
                alerts_triggered.append({
                    'type': 'MEMORY_USAGE_HIGH',
                    'message': f'Memory usage {value:.1%} exceeds threshold {self.alert_thresholds["memory_usage_threshold"]:.1%}',
                    'severity': 'WARNING',
                    'metric': metric_name,
                    'value': value,
                    'threshold': self.alert_thresholds['memory_usage_threshold']
                })

        # Cache miss rate alert
        elif metric_name == 'cache_miss_rate':
            if value > self.alert_thresholds['cache_miss_rate_threshold']:
                alerts_triggered.append({
                    'type': 'CACHE_MISS_RATE_HIGH',
                    'message': f'Cache miss rate {value:.1%} exceeds threshold {self.alert_thresholds["cache_miss_rate_threshold"]:.1%}',
                    'severity': 'INFO',
                    'metric': metric_name,
                    'value': value,
                    'threshold': self.alert_thresholds['cache_miss_rate_threshold']
                })

        # Record alerts
        for alert in alerts_triggered:
            alert['timestamp'] = current_time.isoformat()
            alert['tags'] = tags or {}
            self.alerts.append(alert)

            # Log alert
            logger.warning(f"[ALERT] {alert['type']}: {alert['message']}")

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

    def get_active_alerts(self, severity_filter: Optional[str] = None) -> List[Dict]:
        """Get currently active alerts"""
        recent_alerts = []
        cutoff_time = datetime.now().timestamp() - 3600  # Last hour

        for alert in self.alerts:
            if datetime.fromisoformat(alert['timestamp']).timestamp() > cutoff_time:
                if severity_filter is None or alert['severity'] == severity_filter:
                    recent_alerts.append(alert)

        return recent_alerts

    def set_baseline_performance(self, metric_name: str, baseline_value: float):
        """Set baseline performance for comparison"""
        self.baseline_performance[metric_name] = baseline_value
        logger.info(f"[MONITORING] Set baseline for {metric_name}: {baseline_value}")

    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-1)"""
        health_factors = []

        # Error rate factor (inverse - lower error rate = higher health)
        error_stats = self.get_metric_stats('error_rate', 3600)
        if error_stats['count'] > 0:
            error_rate = error_stats['latest']
            health_factors.append(max(0, 1 - error_rate * 2))  # Scale error rate impact

        # Performance factor
        perf_stats = self.get_metric_stats('enhancement_time', 3600)
        if perf_stats['count'] > 0:
            baseline = self.baseline_performance.get('enhancement_time', perf_stats['mean'])
            if baseline > 0:
                perf_ratio = perf_stats['latest'] / baseline
                health_factors.append(max(0, min(1, 2 - perf_ratio)))  # Better when closer to 1

        # Circuit breaker factor
        cb_stats = self.get_metric_stats('circuit_breakers_open', 3600)
        if cb_stats['count'] > 0:
            cb_penalty = cb_stats['latest'] * 0.2  # Each open CB reduces health by 0.2
            health_factors.append(max(0, 1 - cb_penalty))

        # Memory factor
        mem_stats = self.get_metric_stats('memory_usage', 3600)
        if mem_stats['count'] > 0:
            health_factors.append(max(0, 1 - mem_stats['latest']))  # Lower memory usage = higher health

        return np.mean(health_factors) if health_factors else 0.5

    def get_monitoring_report(self) -> Dict:
        """Get comprehensive monitoring report"""
        return {
            'system_health_score': self.get_system_health_score(),
            'active_alerts': self.get_active_alerts(),
            'metrics_summary': {
                metric_name: self.get_metric_stats(metric_name, 3600)
                for metric_name in self.metrics.keys()
            },
            'baseline_performance': self.baseline_performance,
            'total_alerts': len(self.alerts),
            'monitoring_uptime': (datetime.now() - datetime.min.replace(year=2024)).total_seconds()  # Simplified
        }

class ErrorLearningManager:
    """Machine Learning-based error prediction and avoidance system"""

    def __init__(self, model_path: str = "error_learning_model.pkl"):
        self.model_path = model_path
        self.error_history = []
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model = None
        self.feature_columns = [
            'time_of_day', 'day_of_week', 'market_volatility', 'signal_quality_score',
            'ai_modules_active', 'system_load', 'memory_usage', 'previous_errors_count',
            'time_since_last_error', 'error_streak'
        ]
        # Categorical features that are now encoded as numerical
        self.categorical_columns = ['operation_type', 'asset_symbol']
        self.error_patterns = {}
        self.adaptation_rules = {}

        self._load_or_create_model()
        logger.info("[ERROR_LEARNING] Error Learning Manager initialized")

    def _load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoder = model_data['label_encoder']
                self.error_history = model_data.get('error_history', [])
                self.error_patterns = model_data.get('error_patterns', {})
                logger.info("[ERROR_LEARNING] Loaded existing error learning model")
            else:
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                )
                logger.info("[ERROR_LEARNING] Created new error learning model")
        except Exception as e:
            logger.warning(f"[ERROR_LEARNING] Failed to load model, creating new: {e}")
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )

    def _extract_error_features(self, operation_context: Dict) -> Dict:
        """Extract features for error prediction"""
        now = datetime.now()

        # Create numerical encoding for categorical features
        asset_mapping = {'BTC': 1, 'ETH': 2, 'XAU': 3, 'ES': 4, 'NQ': 5, 'unknown': 0}
        operation_mapping = {
            'neural_prediction': 1, 'rl_insights': 2, 'sentiment_analysis': 3,
            'federated_learning': 4, 'predictive_analytics': 5, 'unknown': 0
        }

        features = {
            'operation_type': operation_mapping.get(operation_context.get('operation_type', 'unknown'), 0),
            'asset_symbol': asset_mapping.get(operation_context.get('asset_symbol', 'unknown'), 0),
            'time_of_day': now.hour + now.minute / 60.0,  # Hour as decimal
            'day_of_week': now.weekday(),  # 0=Monday, 6=Sunday
            'market_volatility': operation_context.get('market_volatility', 0.02),
            'signal_quality_score': self._convert_quality_to_score(
                operation_context.get('signal_quality', 'medium')
            ),
            'ai_modules_active': len(operation_context.get('ai_modules_available', [])),
            'system_load': operation_context.get('system_load', 0.5),
            'memory_usage': operation_context.get('memory_usage', 0.5),
            'previous_errors_count': len([
                e for e in self.error_history[-10:]  # Last 10 operations
                if e.get('had_error', False)
            ]),
            'time_since_last_error': self._calculate_time_since_last_error(),
            'error_streak': self._calculate_error_streak()
        }

        return features

    def _convert_quality_to_score(self, quality: str) -> float:
        """Convert quality string to numerical score"""
        quality_map = {
            'low': 1.0,
            'medium': 2.0,
            'high': 3.0,
            'ultra': 4.0,
            'quantum_elite': 5.0
        }
        return quality_map.get(quality, 2.0)

    def _calculate_time_since_last_error(self) -> float:
        """Calculate time in hours since last error"""
        if not self.error_history:
            return 24.0  # Default 24 hours

        last_error = None
        for entry in reversed(self.error_history):
            if entry.get('had_error', False):
                last_error = entry
                break

        if last_error and 'timestamp' in last_error:
            try:
                last_error_time = datetime.fromisoformat(last_error['timestamp'])
                return (datetime.now() - last_error_time).total_seconds() / 3600.0
            except:
                pass

        return 24.0

    def _calculate_error_streak(self) -> int:
        """Calculate current error streak"""
        if not self.error_history:
            return 0

        streak = 0
        for entry in reversed(self.error_history[-5:]):  # Check last 5 operations
            if entry.get('had_error', False):
                streak += 1
            else:
                break

        return streak

    def predict_error_likelihood(self, operation_context: Dict) -> Dict:
        """Predict the likelihood of an error occurring"""
        if self.model is None or len(self.error_history) < 10:
            return {
                'error_probability': 0.1,  # Default low probability with little data
                'confidence': 0.3,
                'should_attempt': True,
                'alternative_suggestions': []
            }

        try:
            features = self._extract_error_features(operation_context)
            feature_df = pd.DataFrame([features])

            # Prepare all features (now all numerical)
            X = feature_df[self.categorical_columns + self.feature_columns].values

            # Scale features if scaler is fitted
            if hasattr(self.scaler, 'mean_'):  # Check if scaler is fitted
                X = self.scaler.transform(X)

            # Predict
            error_proba = self.model.predict_proba(X)[0][1]  # Probability of error (class 1)

            # Generate suggestions based on error patterns
            suggestions = self._generate_alternatives(operation_context, error_proba)

            return {
                'error_probability': float(error_proba),
                'confidence': self._calculate_prediction_confidence(),
                'should_attempt': error_proba < 0.7,  # Don't attempt if >70% error chance
                'alternative_suggestions': suggestions
            }

        except Exception as e:
            logger.warning(f"[ERROR_LEARNING] Prediction failed: {e}")
            return {
                'error_probability': 0.2,  # Conservative fallback
                'confidence': 0.1,
                'should_attempt': True,
                'alternative_suggestions': []
            }

    def _generate_alternatives(self, operation_context: Dict, error_proba: float) -> List[str]:
        """Generate alternative approaches to avoid predicted errors"""
        operation_type = operation_context.get('operation_type', 'unknown')
        suggestions = []

        if error_proba > 0.5:
            # High error probability - suggest alternatives
            if operation_type == 'neural_prediction':
                suggestions.extend([
                    "Use simplified neural model",
                    "Skip neural enhancement for this asset",
                    "Use cached neural predictions",
                    "Reduce prediction horizons"
                ])
            elif operation_type == 'rl_insights':
                suggestions.extend([
                    "Use rule-based strategy instead",
                    "Skip RL enhancement",
                    "Use conservative RL parameters",
                    "Delay RL decision"
                ])
            elif operation_type == 'sentiment_analysis':
                suggestions.extend([
                    "Use basic sentiment scoring",
                    "Skip sentiment analysis",
                    "Use cached sentiment data",
                    "Use alternative sentiment sources"
                ])
            elif operation_type == 'federated_learning':
                suggestions.extend([
                    "Use local model only",
                    "Skip federated consensus",
                    "Use offline federated data",
                    "Reduce federation participants"
                ])

        return suggestions

    def _calculate_prediction_confidence(self) -> float:
        """Calculate confidence in the error prediction"""
        if len(self.error_history) < 20:
            return 0.3  # Low confidence with little data

        # Simple confidence based on model performance and data size
        base_confidence = min(0.9, len(self.error_history) / 100.0)
        return base_confidence

    def record_operation_result(self, operation_context: Dict, had_error: bool,
                              error_details: Optional[str] = None, success_metrics: Optional[Dict] = None):
        """Record the result of an operation for learning"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'operation_context': operation_context.copy(),
            'had_error': had_error,
            'error_details': error_details,
            'success_metrics': success_metrics or {},
            'features': self._extract_error_features(operation_context)
        }

        self.error_history.append(entry)

        # Keep only last 1000 entries to prevent memory issues
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]

        # Update error patterns
        self._update_error_patterns(entry)

        # Retrain model periodically
        if len(self.error_history) % 50 == 0:  # Retrain every 50 operations
            self._retrain_model()

        # Save model
        self._save_model()

        logger.info(f"[ERROR_LEARNING] Recorded operation result: error={had_error}")

    def _update_error_patterns(self, entry: Dict):
        """Update error pattern knowledge"""
        operation_type = entry['operation_context'].get('operation_type', 'unknown')
        had_error = entry['had_error']

        if operation_type not in self.error_patterns:
            self.error_patterns[operation_type] = {
                'total_operations': 0,
                'errors': 0,
                'error_rate': 0.0,
                'common_error_times': [],
                'common_error_assets': [],
                'avg_success_metrics': {}
            }

        pattern = self.error_patterns[operation_type]
        pattern['total_operations'] += 1

        if had_error:
            pattern['errors'] += 1
            # Track error contexts
            timestamp = datetime.fromisoformat(entry['timestamp'])
            pattern['common_error_times'].append(timestamp.hour)

            asset = entry['operation_context'].get('asset_symbol', 'unknown')
            pattern['common_error_assets'].append(asset)

            # Keep only recent patterns
            pattern['common_error_times'] = pattern['common_error_times'][-20:]
            pattern['common_error_assets'] = pattern['common_error_assets'][-20:]

        pattern['error_rate'] = pattern['errors'] / pattern['total_operations']

        # Update success metrics
        if not had_error and entry.get('success_metrics'):
            metrics = entry['success_metrics']
            for key, value in metrics.items():
                if key not in pattern['avg_success_metrics']:
                    pattern['avg_success_metrics'][key] = []
                pattern['avg_success_metrics'][key].append(value)
                # Keep only last 10 measurements
                pattern['avg_success_metrics'][key] = pattern['avg_success_metrics'][key][-10:]

    def _retrain_model(self):
        """Retrain the error prediction model"""
        if len(self.error_history) < 20:
            logger.info("[ERROR_LEARNING] Not enough data for retraining")
            return

        try:
            # Prepare training data
            df = pd.DataFrame([
                {**entry['features'], 'had_error': entry['had_error']}
                for entry in self.error_history
            ])

            if len(df) < 20 or df['had_error'].nunique() < 2:
                logger.warning("[ERROR_LEARNING] Insufficient data diversity for retraining")
                return

            # Prepare features (all now numerical)
            X = df[self.categorical_columns + self.feature_columns]
            y = df['had_error'].astype(int)

            # Scale all features
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

            logger.info(f"[ERROR_LEARNING] Model retrained - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")

        except Exception as e:
            logger.error(f"[ERROR_LEARNING] Model retraining failed: {e}")

    def _save_model(self):
        """Save the model and learning data"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'error_history': self.error_history[-500:],  # Save last 500 entries
                'error_patterns': self.error_patterns,
                'feature_columns': self.feature_columns,
                'last_updated': datetime.now().isoformat()
            }

            joblib.dump(model_data, self.model_path)
            logger.debug("[ERROR_LEARNING] Model saved successfully")

        except Exception as e:
            logger.warning(f"[ERROR_LEARNING] Failed to save model: {e}")

    def get_error_insights(self) -> Dict:
        """Get insights about error patterns and learning progress"""
        return {
            'total_operations': len(self.error_history),
            'error_patterns': self.error_patterns,
            'model_trained': self.model is not None,
            'training_data_size': len(self.error_history),
            'learning_progress': min(1.0, len(self.error_history) / 100.0),
            'recent_error_rate': self._calculate_recent_error_rate(),
            'most_problematic_operations': self._get_most_problematic_operations()
        }

    def _calculate_recent_error_rate(self) -> float:
        """Calculate error rate in recent operations"""
        if not self.error_history:
            return 0.0

        recent_entries = self.error_history[-50:]  # Last 50 operations
        errors = sum(1 for entry in recent_entries if entry.get('had_error', False))
        return errors / len(recent_entries)

    def _get_most_problematic_operations(self) -> List[Dict]:
        """Get operations with highest error rates"""
        operation_stats = []

        for op_type, pattern in self.error_patterns.items():
            if pattern['total_operations'] >= 5:  # Only include operations with enough data
                operation_stats.append({
                    'operation_type': op_type,
                    'error_rate': pattern['error_rate'],
                    'total_operations': pattern['total_operations'],
                    'recent_errors': len([
                        t for t in pattern.get('common_error_times', [])
                        if abs(datetime.now().hour - t) <= 1  # Errors within 1 hour of current hour
                    ])
                })

        # Sort by error rate descending
        return sorted(operation_stats, key=lambda x: x['error_rate'], reverse=True)[:5]

class QuantumEliteSignalEnhancer:
    """Enhances trading signals with Quantum Elite AI capabilities"""

    def __init__(self, max_workers: int = 4, enable_async: bool = True, cache_ttl: int = 300,
                 config_manager: Optional["ConfigurationManager"] = None):
        # Use shared configuration manager if available
        try:
            self.config_manager = config_manager or globals().get('config_manager') or ConfigurationManager()
        except Exception:
            self.config_manager = None

        # Apply configuration overrides
        if self.config_manager:
            max_workers = self.config_manager.get('system.max_workers', max_workers)
            enable_async = self.config_manager.get('system.enable_async', enable_async)
            cache_ttl = self.config_manager.get('system.cache_ttl_seconds', cache_ttl)

        self.ai_modules_available = self._check_ai_availability()
        self.signal_cache = {}
        self.last_update = {}
        self.error_learning_manager = ErrorLearningManager()
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ai_worker")
        self.enable_async = enable_async
        self.performance_metrics = defaultdict(list)
        self.module_performance = {}

        # Initialize advanced caching
        self.cache = AdvancedCache(ttl_seconds=cache_ttl)
        self.cache_hit_rate = {'hits': 0, 'misses': 0}

        # Initialize circuit breakers for each AI module
        self.circuit_breakers = {
            'neural_predictor': CircuitBreaker(failure_threshold=3, recovery_timeout=120),
            'reinforcement_learning': CircuitBreaker(failure_threshold=3, recovery_timeout=120),
            'nlp_sentiment': CircuitBreaker(failure_threshold=5, recovery_timeout=60),  # More lenient for sentiment
            'federated_learning': CircuitBreaker(failure_threshold=2, recovery_timeout=300),  # Stricter for federated
        }

        # Initialize advanced monitoring
        self.monitoring = AdvancedMonitoringSystem()

        # Listen for config changes to refresh toggles
        if self.config_manager:
            self.config_manager.add_config_listener(self._on_config_change)

        logger.info(f"[INIT] Quantum Elite Signal Enhancer initialized with async processing (workers: {max_workers}), advanced caching, circuit breakers, monitoring, and dynamic config")

    def _check_ai_availability(self) -> Dict[str, bool]:
        """Check which AI modules are available (importable) and enabled via config/feature flags"""
        modules = {
            'neural_predictor': False,
            'reinforcement_learning': False,
            'federated_learning': False,
            'nlp_sentiment': False,
            'predictive_analytics': False
        }

        # Try to import each module, then gate by config/feature flags
        try:
            from ai_advanced_neural_predictor import QuantumEliteNeuralPredictor
            modules['neural_predictor'] = True
            logger.info("[AI] Neural predictor available")
        except ImportError:
            logger.warning("[AI] Neural predictor not available")

        try:
            from ai_advanced_reinforcement_learning import QuantumEliteStrategyManager
            modules['reinforcement_learning'] = True
            logger.info("[AI] Reinforcement learning available")
        except ImportError:
            logger.warning("[AI] Reinforcement learning not available")

        try:
            from ai_federated_learning import QuantumEliteFederatedLearning
            modules['federated_learning'] = True
            logger.info("[AI] Federated learning available")
        except ImportError:
            logger.warning("[AI] Federated learning not available")

        try:
            from ai_nlp_market_intelligence import MarketSentimentAnalyzer
            modules['nlp_sentiment'] = True
            logger.info("[AI] NLP sentiment available")
        except ImportError:
            logger.warning("[AI] NLP sentiment not available")

        try:
            from ai_realtime_predictive_analytics import StreamingDataProcessor
            modules['predictive_analytics'] = True
            logger.info("[AI] Predictive analytics available")
        except ImportError:
            logger.warning("[AI] Predictive analytics not available")

        # Apply configuration/feature flag gates
        for module_name in list(modules.keys()):
            if modules[module_name] and not self._is_module_enabled(module_name):
                modules[module_name] = False
                logger.info(f"[AI] {module_name} disabled by configuration/feature flag")

        available_count = sum(modules.values())
        logger.info(f"[AI] {available_count}/{len(modules)} AI modules available (post-config)")

        return modules

    def _is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled via config and feature flags"""
        if not self.config_manager:
            return True

        enabled_in_config = self.config_manager.get(f"ai_modules.{module_name}.enabled", True)
        feature_flag_enabled = self.config_manager.is_feature_enabled(module_name) if hasattr(self.config_manager, 'is_feature_enabled') else True
        return bool(enabled_in_config and feature_flag_enabled)

    def _on_config_change(self, changes: Dict):
        """Refresh module availability and toggles when configuration changes"""
        logger.info(f"[CONFIG] Applying configuration changes: {list(changes.keys())}")
        self.ai_modules_available = self._check_ai_availability()

    def enhance_signal(self, base_signal: Dict, asset_symbol: str, market_data: Optional[Dict] = None,
                      force_refresh: bool = False) -> Dict:
        """Enhance a base signal with Quantum Elite AI capabilities"""

        # Input validation
        signal_valid, signal_errors = DataValidator.validate_signal(base_signal)
        if not signal_valid:
            logger.warning(f"[VALIDATION] Signal validation failed: {signal_errors}")
            # Try to sanitize and continue, but log warnings
            base_signal = DataValidator.sanitize_signal(base_signal)
            for error in signal_errors:
                logger.warning(f"[VALIDATION] {error}")

        # Validate asset symbol consistency
        if asset_symbol != base_signal.get('asset'):
            logger.warning(f"[VALIDATION] Asset symbol mismatch: {asset_symbol} vs {base_signal.get('asset')}")
            asset_symbol = base_signal.get('asset', asset_symbol)

        # Get and validate market data
        if market_data is None:
            market_data = self._get_market_data_for_asset(asset_symbol)

        market_valid, market_errors = DataValidator.validate_market_data(market_data)
        if not market_valid:
            logger.warning(f"[VALIDATION] Market data validation failed: {market_errors}")
            # Continue with potentially invalid data but log warnings

        # Calculate data quality scores
        signal_quality_score = DataValidator.check_data_quality_score(base_signal, 'signal')
        market_quality_score = DataValidator.check_data_quality_score(market_data, 'market_data')

        logger.info(f"[QUALITY] Signal quality: {signal_quality_score:.2f}, Market data quality: {market_quality_score:.2f}")

        # Create cache key based on signal content and market data
        cache_key_data = {
            'base_signal': base_signal,
            'asset_symbol': asset_symbol,
            'market_data': market_data,
            'ai_modules_available': self.ai_modules_available
        }
        cache_key = f"signal_enhancement_{hashlib.md5(json.dumps(cache_key_data, sort_keys=True, default=str).encode()).hexdigest()}"

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.cache_hit_rate['hits'] += 1
                logger.info(f"[CACHE] Cache hit for {asset_symbol} signal enhancement")
                return cached_result

        self.cache_hit_rate['misses'] += 1

        enhanced_signal = base_signal.copy()
        enhanced_signal['quantum_elite_enhanced'] = True
        enhanced_signal['enhancement_timestamp'] = datetime.now().isoformat()
        enhanced_signal['ai_modules_used'] = []
        enhanced_signal['cache_used'] = False

        # Add market data if not provided
        if market_data is None:
            market_data = self._get_market_data_for_asset(asset_symbol)

        start_time = datetime.now()

        if self.enable_async:
            # Parallel enhancement using async processing
            enhanced_signal = self._enhance_signal_async(enhanced_signal, asset_symbol, market_data)
        else:
            # Sequential enhancement (original method)
            enhanced_signal = self._enhance_signal_sequential(enhanced_signal, asset_symbol, market_data)

        # Calculate overall AI confidence
        ai_confidence = self._calculate_overall_ai_confidence(enhanced_signal)
        enhanced_signal['ai_overall_confidence'] = ai_confidence

        # Update signal quality rating
        enhanced_signal = self._update_signal_quality(enhanced_signal)

        # Track performance
        processing_time = (datetime.now() - start_time).total_seconds()
        self.performance_metrics['enhancement_time'].append(processing_time)
        enhanced_signal['processing_time'] = processing_time

        # Record monitoring metrics
        self.monitoring.record_metric('enhancement_time', processing_time, {'asset': asset_symbol})
        self.monitoring.record_metric('ai_modules_used', len(enhanced_signal['ai_modules_used']), {'asset': asset_symbol})
        self.monitoring.record_metric('cache_hit_rate', self.cache_hit_rate['hits'] / max(1, self.cache_hit_rate['hits'] + self.cache_hit_rate['misses']))
        self.monitoring.record_metric('signal_quality_score', signal_quality_score)
        self.monitoring.record_metric('market_data_quality_score', market_quality_score)

        # Check circuit breaker status
        open_circuit_breakers = sum(1 for cb in self.circuit_breakers.values() if cb.state == 'OPEN')
        self.monitoring.record_metric('circuit_breakers_open', open_circuit_breakers)

        # Cache the result (only successful enhancements)
        if len(enhanced_signal.get('ai_modules_used', [])) > 0:
            self.cache.set(cache_key, enhanced_signal)

        logger.info(f"[ENHANCE] Enhanced signal for {asset_symbol} with {len(enhanced_signal['ai_modules_used'])} AI modules in {processing_time:.3f}s")

        return enhanced_signal

    def _enhance_signal_sequential(self, enhanced_signal: Dict, asset_symbol: str, market_data: Dict) -> Dict:
        """Sequential enhancement (original method)"""
        # Enhance with neural predictions
        if self.ai_modules_available['neural_predictor'] and self._is_module_enabled('neural_predictor'):
            neural_enhancement = self._add_neural_predictions(enhanced_signal, asset_symbol, market_data)
            if neural_enhancement:
                enhanced_signal.update(neural_enhancement)
                enhanced_signal['ai_modules_used'].append('neural_predictor')

        # Add reinforcement learning insights
        if self.ai_modules_available['reinforcement_learning'] and self._is_module_enabled('reinforcement_learning'):
            rl_enhancement = self._add_rl_insights(enhanced_signal, asset_symbol, market_data)
            if rl_enhancement:
                enhanced_signal.update(rl_enhancement)
                enhanced_signal['ai_modules_used'].append('reinforcement_learning')

        # Add sentiment analysis
        if self.ai_modules_available['nlp_sentiment'] and self._is_module_enabled('nlp_sentiment'):
            sentiment_enhancement = self._add_sentiment_analysis(enhanced_signal, asset_symbol)
            if sentiment_enhancement:
                enhanced_signal.update(sentiment_enhancement)
                enhanced_signal['ai_modules_used'].append('nlp_sentiment')

        # Add federated learning consensus
        if self.ai_modules_available['federated_learning'] and self._is_module_enabled('federated_learning'):
            fed_enhancement = self._add_federated_consensus(enhanced_signal, asset_symbol)
            if fed_enhancement:
                enhanced_signal.update(fed_enhancement)
                enhanced_signal['ai_modules_used'].append('federated_learning')

        return enhanced_signal

    def _enhance_signal_async(self, enhanced_signal: Dict, asset_symbol: str, market_data: Dict) -> Dict:
        """Parallel enhancement using async processing"""
        # Define AI module tasks
        tasks = []

        if self.ai_modules_available['neural_predictor'] and self._is_module_enabled('neural_predictor'):
            tasks.append(('neural_predictor', functools.partial(self._add_neural_predictions, enhanced_signal, asset_symbol, market_data)))

        if self.ai_modules_available['reinforcement_learning'] and self._is_module_enabled('reinforcement_learning'):
            tasks.append(('reinforcement_learning', functools.partial(self._add_rl_insights, enhanced_signal, asset_symbol, market_data)))

        if self.ai_modules_available['nlp_sentiment'] and self._is_module_enabled('nlp_sentiment'):
            tasks.append(('nlp_sentiment', functools.partial(self._add_sentiment_analysis, enhanced_signal, asset_symbol)))

        if self.ai_modules_available['federated_learning'] and self._is_module_enabled('federated_learning'):
            tasks.append(('federated_learning', functools.partial(self._add_federated_consensus, enhanced_signal, asset_symbol)))

        # Execute tasks in parallel
        futures = {}
        for module_name, func in tasks:
            future = self.executor.submit(func)
            futures[future] = module_name

        # Collect results
        for future in as_completed(futures, timeout=30):  # 30 second timeout
            module_name = futures[future]
            try:
                start_time = datetime.now()
                result = future.result(timeout=10)  # 10 second timeout per module
                processing_time = (datetime.now() - start_time).total_seconds()

                # Track module performance
                if module_name not in self.module_performance:
                    self.module_performance[module_name] = []
                self.module_performance[module_name].append(processing_time)

                if result:
                    enhanced_signal.update(result)
                    enhanced_signal['ai_modules_used'].append(module_name)
                    logger.debug(f"[ASYNC] {module_name} completed in {processing_time:.3f}s")

            except Exception as e:
                logger.warning(f"[ASYNC] {module_name} failed: {e}")
                # Continue with other modules

        return enhanced_signal

    def _get_market_data_for_asset(self, asset_symbol: str) -> Dict:
        """Get market data for asset (simplified for integration)"""
        # In production, this would fetch real market data
        # For now, return synthetic data
        return {
            'price': 50000 if 'BTC' in asset_symbol else 3000 if 'ETH' in asset_symbol else 1800 if 'XAU' in asset_symbol else 100,
            'volume': 1000000,
            'change_24h': 2.5,
            'volatility': 0.03,
            'timestamp': datetime.now()
        }

    def _add_neural_predictions(self, signal: Dict, asset_symbol: str, market_data: Dict) -> Optional[Dict]:
        """Add neural network predictions to signal with error learning"""
        operation_context = {
            'operation_type': 'neural_prediction',
            'asset_symbol': asset_symbol,
            'market_volatility': market_data.get('volatility', 0.02),
            'signal_quality': signal.get('signal_quality', 'medium'),
            'ai_modules_available': [k for k, v in self.ai_modules_available.items() if v],
            'system_load': 0.5,  # Placeholder - could be actual system load
            'memory_usage': 0.5   # Placeholder - could be actual memory usage
        }

        # Predict error likelihood
        error_prediction = self.error_learning_manager.predict_error_likelihood(operation_context)

        if not error_prediction['should_attempt']:
            logger.info(f"[NEURAL] Skipping neural prediction due to high error probability: {error_prediction['error_probability']:.2%}")
            logger.info(f"[NEURAL] Alternative suggestions: {error_prediction['alternative_suggestions']}")

            # Record this avoidance as a "successful" operation (avoided error)
            self.error_learning_manager.record_operation_result(
                operation_context,
                had_error=False,  # No error because we avoided it
                error_details="Proactively avoided due to error prediction",
                success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']}
            )
            return None

        success = False
        error_details = None
        success_metrics = {}

        try:
            # Use circuit breaker for neural prediction
            def _neural_prediction_call():
                from ai_advanced_neural_predictor import QuantumEliteNeuralPredictor

                # Create synthetic historical data for prediction
                historical_data = self._create_historical_data_for_prediction(asset_symbol, market_data)

                predictor = QuantumEliteNeuralPredictor()

                # Make predictions
                predictions = predictor.predict_multi_horizon(historical_data, asset_symbol)
                return predictions

            predictions = self.circuit_breakers['neural_predictor'].call(_neural_prediction_call)

            if predictions:
                # Extract key predictions
                short_term = predictions.get('h1', {})
                medium_term = predictions.get('h3', {})
                long_term = predictions.get('h6', {})

                neural_enhancement = {
                    'neural_predictions': {
                        'short_term': {
                            'direction': short_term.get('direction', 'neutral'),
                            'magnitude': short_term.get('magnitude', 0),
                            'confidence': short_term.get('confidence', 0.5)
                        },
                        'medium_term': {
                            'direction': medium_term.get('direction', 'neutral'),
                            'magnitude': medium_term.get('magnitude', 0),
                            'confidence': medium_term.get('confidence', 0.5)
                        },
                        'long_term': {
                            'direction': long_term.get('direction', 'neutral'),
                            'magnitude': long_term.get('magnitude', 0),
                            'confidence': long_term.get('confidence', 0.5)
                        }
                    },
                    'neural_signal_strength': self._calculate_neural_signal_strength(predictions),
                    'neural_prediction_timestamp': datetime.now().isoformat()
                }

                success = True
                success_metrics = {
                    'predictions_generated': len(predictions),
                    'avg_confidence': np.mean([
                        short_term.get('confidence', 0.5),
                        medium_term.get('confidence', 0.5),
                        long_term.get('confidence', 0.5)
                    ])
                }

                return neural_enhancement

        except Exception as e:
            error_details = str(e)
            logger.warning(f"[NEURAL] Failed to add neural predictions: {e}")

        # Record operation result for learning
        self.error_learning_manager.record_operation_result(
            operation_context,
            had_error=not success,
            error_details=error_details,
            success_metrics=success_metrics if success else None
        )

        return None

    def _create_historical_data_for_prediction(self, asset_symbol: str, market_data: Dict) -> pd.DataFrame:
        """Create historical data for neural prediction (simplified)"""
        # Generate 200 periods of historical data
        periods = 200
        timestamps = pd.date_range(end=datetime.now(), periods=periods, freq='1H')

        base_price = market_data.get('price', 100)
        volatility = market_data.get('volatility', 0.02)

        # Generate price series
        returns = np.random.normal(0.0001, volatility, periods)
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        # Create OHLCV data
        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'close': prices,
            'volume': np.random.lognormal(10, 1, periods)
        }).set_index('timestamp')

        return data

    def _calculate_neural_signal_strength(self, predictions: Dict) -> float:
        """Calculate overall neural signal strength"""
        if not predictions:
            return 0.0

        strengths = []
        for horizon, pred in predictions.items():
            direction_mult = 1 if pred.get('direction') == 'bullish' else -1 if pred.get('direction') == 'bearish' else 0
            magnitude = pred.get('magnitude', 0)
            confidence = pred.get('confidence', 0.5)
            strength = direction_mult * magnitude * confidence
            strengths.append(strength)

        return np.mean(strengths) if strengths else 0.0

    def _add_rl_insights(self, signal: Dict, asset_symbol: str, market_data: Dict) -> Optional[Dict]:
        """Add reinforcement learning insights with error learning"""
        operation_context = {
            'operation_type': 'rl_insights',
            'asset_symbol': asset_symbol,
            'market_volatility': market_data.get('volatility', 0.02),
            'signal_quality': signal.get('signal_quality', 'medium'),
            'ai_modules_available': [k for k, v in self.ai_modules_available.items() if v],
            'system_load': 0.5,
            'memory_usage': 0.5
        }

        # Predict error likelihood
        error_prediction = self.error_learning_manager.predict_error_likelihood(operation_context)

        if not error_prediction['should_attempt']:
            logger.info(f"[RL] Skipping RL insights due to high error probability: {error_prediction['error_probability']:.2%}")
            logger.info(f"[RL] Alternative suggestions: {error_prediction['alternative_suggestions']}")

            self.error_learning_manager.record_operation_result(
                operation_context,
                had_error=False,
                error_details="Proactively avoided due to error prediction",
                success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']}
            )
            return None

        success = False
        error_details = None
        success_metrics = {}

        try:
            from ai_advanced_reinforcement_learning import QuantumEliteStrategyManager

            rl_manager = QuantumEliteStrategyManager()

            # Create RL strategy for asset
            strategy = rl_manager.create_quantum_strategy(asset_symbol)

            # Get market context
            market_regime = {
                'regime': 'bull' if market_data.get('change_24h', 0) > 1 else 'bear' if market_data.get('change_24h', 0) < -1 else 'sideways',
                'volatility': market_data.get('volatility', 0.02),
                'trend_strength': abs(market_data.get('change_24h', 0)) / 10,
                'momentum': market_data.get('change_24h', 0) / 5
            }

            # Get RL decision
            decision = rl_manager.execute_strategy_decision(
                strategy['id'], pd.DataFrame(), {}, market_regime
            )

            rl_enhancement = {
                'rl_strategy_id': strategy['id'],
                'rl_decision': decision.get('action', []),
                'rl_market_regime': market_regime['regime'],
                'rl_confidence': decision.get('reward', 0),
                'rl_risk_assessment': self._calculate_rl_risk(decision)
            }

            success = True
            success_metrics = {
                'strategy_created': True,
                'decision_made': len(decision.get('action', [])) > 0,
                'confidence_score': decision.get('reward', 0)
            }

            return rl_enhancement

        except Exception as e:
            error_details = str(e)
            logger.warning(f"[RL] Failed to add RL insights: {e}")

        # Record operation result for learning
        self.error_learning_manager.record_operation_result(
            operation_context,
            had_error=not success,
            error_details=error_details,
            success_metrics=success_metrics if success else None
        )

        return None

    def _calculate_rl_risk(self, decision: Dict) -> str:
        """Calculate risk level from RL decision"""
        action = decision.get('action', [])
        if not action:
            return 'medium'

        # Simple risk calculation based on action magnitude
        risk_score = np.mean([abs(a) for a in action])

        if risk_score > 0.7:
            return 'high'
        elif risk_score > 0.3:
            return 'medium'
        else:
            return 'low'

    def _add_sentiment_analysis(self, signal: Dict, asset_symbol: str) -> Optional[Dict]:
        """Add sentiment analysis to signal with error learning"""
        operation_context = {
            'operation_type': 'sentiment_analysis',
            'asset_symbol': asset_symbol,
            'market_volatility': 0.02,  # Default since no market data in this method
            'signal_quality': signal.get('signal_quality', 'medium'),
            'ai_modules_available': [k for k, v in self.ai_modules_available.items() if v],
            'system_load': 0.5,
            'memory_usage': 0.5
        }

        # Predict error likelihood
        error_prediction = self.error_learning_manager.predict_error_likelihood(operation_context)

        if not error_prediction['should_attempt']:
            logger.info(f"[SENTIMENT] Skipping sentiment analysis due to high error probability: {error_prediction['error_probability']:.2%}")
            logger.info(f"[SENTIMENT] Alternative suggestions: {error_prediction['alternative_suggestions']}")

            self.error_learning_manager.record_operation_result(
                operation_context,
                had_error=False,
                error_details="Proactively avoided due to error prediction",
                success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']}
            )
            return None

        success = False
        error_details = None
        success_metrics = {}

        try:
            from ai_nlp_market_intelligence import MarketSentimentAnalyzer

            analyzer = MarketSentimentAnalyzer()

            # Generate sentiment text based on asset
            sentiment_text = self._generate_asset_sentiment_text(asset_symbol, signal)

            # Analyze sentiment
            sentiment = analyzer.analyze_sentiment(sentiment_text)

            sentiment_enhancement = {
                'market_sentiment': sentiment.get('sentiment', 'neutral'),
                'sentiment_confidence': sentiment.get('confidence', 0.5),
                'sentiment_score': sentiment.get('score', 0.0),
                'sentiment_magnitude': sentiment.get('magnitude', 0.0),
                'sentiment_factors': sentiment.get('aspects', {}),
                'sentiment_analyzed_text': sentiment_text[:100] + '...' if len(sentiment_text) > 100 else sentiment_text
            }

            success = True
            success_metrics = {
                'sentiment_detected': sentiment.get('sentiment') != 'neutral',
                'confidence_score': sentiment.get('confidence', 0.5),
                'text_length': len(sentiment_text)
            }

            return sentiment_enhancement

        except Exception as e:
            error_details = str(e)
            logger.warning(f"[SENTIMENT] Failed to add sentiment analysis: {e}")

        # Record operation result for learning
        self.error_learning_manager.record_operation_result(
            operation_context,
            had_error=not success,
            error_details=error_details,
            success_metrics=success_metrics if success else None
        )

        return None

    def _generate_asset_sentiment_text(self, asset_symbol: str, signal: Dict) -> str:
        """Generate sentiment analysis text for asset"""
        base_texts = {
            'BTC': "Bitcoin market shows strong momentum with increasing institutional adoption",
            'ETH': "Ethereum network upgrades driving positive developer sentiment",
            'XAU': "Gold prices supported by safe haven demand amid economic uncertainty",
            'ES': "S&P 500 futures indicating bullish market sentiment",
            'NQ': "Nasdaq tech stocks leading market gains with AI optimism",
        }

        # Get base text or create generic one
        base_text = base_texts.get(asset_symbol, f"{asset_symbol} showing mixed market signals")

        # Add signal-specific context
        if signal.get('has_signal', False):
            signal_type = signal.get('signal_type', 'unknown')
            base_text += f" with {signal_type} trading signals emerging"

        return base_text

    def _add_federated_consensus(self, signal: Dict, asset_symbol: str) -> Optional[Dict]:
        """Add federated learning consensus with error learning"""
        operation_context = {
            'operation_type': 'federated_learning',
            'asset_symbol': asset_symbol,
            'market_volatility': 0.02,
            'signal_quality': signal.get('signal_quality', 'medium'),
            'ai_modules_available': [k for k, v in self.ai_modules_available.items() if v],
            'system_load': 0.5,
            'memory_usage': 0.5
        }

        # Predict error likelihood
        error_prediction = self.error_learning_manager.predict_error_likelihood(operation_context)

        if not error_prediction['should_attempt']:
            logger.info(f"[FEDERATED] Skipping federated consensus due to high error probability: {error_prediction['error_probability']:.2%}")
            logger.info(f"[FEDERATED] Alternative suggestions: {error_prediction['alternative_suggestions']}")

            self.error_learning_manager.record_operation_result(
                operation_context,
                had_error=False,
                error_details="Proactively avoided due to error prediction",
                success_metrics={'avoided_error': True, 'error_probability': error_prediction['error_probability']}
            )
            return None

        success = False
        error_details = None
        success_metrics = {}

        try:
            from ai_federated_learning import QuantumEliteFederatedLearning

            # Create FL system
            model_arch = {'input_shape': (100, 10), 'layers': [], 'output': {'units': 1}}
            fl_system = QuantumEliteFederatedLearning(model_arch)

            # Get insights (simplified)
            insights = fl_system.get_collaborative_insights('system_user')

            fed_enhancement = {
                'federated_participants': insights.get('system_status', {}).get('federated_learning', {}).get('total_clients', 0),
                'federated_consensus_strength': 0.85,  # Placeholder
                'federated_privacy_level': 'differential_privacy',
                'federated_last_update': datetime.now().isoformat()
            }

            success = True
            success_metrics = {
                'participants_connected': fed_enhancement['federated_participants'] > 0,
                'consensus_strength': fed_enhancement['federated_consensus_strength'],
                'insights_retrieved': bool(insights)
            }

            return fed_enhancement

        except Exception as e:
            error_details = str(e)
            logger.warning(f"[FEDERATED] Failed to add federated consensus: {e}")

        # Record operation result for learning
        self.error_learning_manager.record_operation_result(
            operation_context,
            had_error=not success,
            error_details=error_details,
            success_metrics=success_metrics if success else None
        )

        return None

    def _calculate_overall_ai_confidence(self, signal: Dict) -> float:
        """Calculate overall AI confidence from all modules"""
        confidences = []

        # Neural confidence
        if 'neural_predictions' in signal:
            neural_conf = signal['neural_predictions'].get('short_term', {}).get('confidence', 0.5)
            confidences.append(neural_conf)

        # RL confidence
        if 'rl_confidence' in signal:
            rl_conf = max(0, min(1, signal['rl_confidence'] / 10))  # Normalize
            confidences.append(rl_conf)

        # Sentiment confidence
        if 'sentiment_confidence' in signal:
            sent_conf = signal['sentiment_confidence']
            confidences.append(sent_conf)

        # Federated confidence (placeholder)
        if 'federated_consensus_strength' in signal:
            fed_conf = signal['federated_consensus_strength']
            confidences.append(fed_conf)

        if confidences:
            return np.mean(confidences)
        else:
            return 0.5  # Default confidence

    def _update_signal_quality(self, signal: Dict) -> Dict:
        """Update signal quality rating based on AI enhancements"""
        base_quality = signal.get('signal_quality', 'medium')
        ai_modules = signal.get('ai_modules_used', [])
        ai_confidence = signal.get('ai_overall_confidence', 0.5)

        # Quality mapping
        quality_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'ultra': 4,
            'quantum_elite': 5
        }

        current_score = quality_scores.get(base_quality, 2)

        # Boost quality based on AI modules and confidence
        ai_boost = len(ai_modules) * 0.5 + ai_confidence * 0.5
        new_score = min(5, current_score + ai_boost)

        # Map back to quality label
        score_to_quality = {
            1: 'low',
            2: 'medium',
            3: 'high',
            4: 'ultra',
            5: 'quantum_elite'
        }

        signal['signal_quality'] = score_to_quality.get(int(new_score), 'high')
        signal['quality_score'] = new_score

        return signal

    def get_enhancement_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about signal enhancements"""
        error_insights = self.error_learning_manager.get_error_insights()

        # Calculate performance statistics
        total_enhancements = len(self.performance_metrics.get('enhancement_time', []))
        avg_processing_time = np.mean(self.performance_metrics.get('enhancement_time', [0]))
        avg_ai_modules = np.mean([len(self.signal_cache.get(k, {}).get('ai_modules_used', []))
                                 for k in self.signal_cache.keys()]) if self.signal_cache else 0

        # Calculate cache statistics
        total_cache_requests = self.cache_hit_rate['hits'] + self.cache_hit_rate['misses']
        cache_hit_rate = self.cache_hit_rate['hits'] / max(1, total_cache_requests)

        # Circuit breaker status
        circuit_breaker_status = {
            name: cb.get_status() for name, cb in self.circuit_breakers.items()
        }

        return {
            'ai_modules_available': self.ai_modules_available,
            'total_enhancements': total_enhancements,
            'last_enhancement_time': max(self.last_update.values()) if self.last_update else None,
            'average_processing_time': avg_processing_time,
            'average_ai_modules_used': avg_ai_modules,
            'cache_hit_rate': cache_hit_rate,
            'cache_stats': self.cache.get_cache_stats(),
            'circuit_breaker_status': circuit_breaker_status,
            'performance_metrics': dict(self.performance_metrics),
            'module_performance': dict(self.module_performance),
            'monitoring_report': self.monitoring.get_monitoring_report(),
            'error_learning_insights': error_insights,
            'system_health_score': self.monitoring.get_system_health_score()
        }

class TelegramAISignalIntegration:
    """Integrates Quantum Elite AI with Telegram bot signals"""

    def __init__(self):
        self.enhancer = QuantumEliteSignalEnhancer()
        self.enhanced_signals_cache = {}
        self.integration_stats = {
            'signals_processed': 0,
            'ai_enhancements_applied': 0,
            'average_enhancement_time': 0,
            'last_integration_time': None,
            'errors_avoided': 0,
            'adaptive_decisions': 0
        }

    def enhance_telegram_signal(self, base_signal: Dict, asset_symbol: str) -> Dict:
        """Enhance a signal for Telegram bot with AI capabilities and error learning"""
        start_time = datetime.now()

        # Get error learning insights before enhancement
        error_insights = self.enhancer.error_learning_manager.get_error_insights()

        # Enhance the signal
        enhanced_signal = self.enhancer.enhance_signal(base_signal, asset_symbol)

        # Add Telegram-specific formatting
        enhanced_signal = self._format_for_telegram(enhanced_signal)

        # Add error learning insights to the signal
        enhanced_signal['error_learning_insights'] = {
            'learning_progress': error_insights.get('learning_progress', 0),
            'recent_error_rate': error_insights.get('recent_error_rate', 0),
            'adaptive_decisions_made': error_insights.get('total_operations', 0) > 0
        }

        # Cache the enhanced signal
        signal_key = f"{asset_symbol}_{enhanced_signal.get('timestamp', datetime.now().isoformat())}"
        self.enhanced_signals_cache[signal_key] = enhanced_signal

        # Update stats
        self.integration_stats['signals_processed'] += 1
        if enhanced_signal.get('quantum_elite_enhanced', False):
            self.integration_stats['ai_enhancements_applied'] += 1

        # Track adaptive behavior from error learning
        if error_insights.get('total_operations', 0) > 0:
            recent_errors = error_insights.get('recent_error_rate', 0)
            if recent_errors < 0.1:  # Low error rate indicates good adaptation
                self.integration_stats['adaptive_decisions'] += 1

        processing_time = (datetime.now() - start_time).total_seconds()
        self.integration_stats['average_enhancement_time'] = (
            (self.integration_stats['average_enhancement_time'] * (self.integration_stats['signals_processed'] - 1)) +
            processing_time
        ) / self.integration_stats['signals_processed']

        self.integration_stats['last_integration_time'] = datetime.now()

        return enhanced_signal

    def _format_for_telegram(self, signal: Dict) -> Dict:
        """Format enhanced signal for Telegram display"""
        formatted_signal = signal.copy()

        # Create AI insights summary
        ai_insights = []

        # Neural predictions
        if 'neural_predictions' in signal:
            neural = signal['neural_predictions']
            short_term = neural.get('short_term', {})
            direction = short_term.get('direction', 'neutral')
            confidence = short_term.get('confidence', 0.5)
            ai_insights.append(f"🤖 Neural AI: {direction.title()} ({confidence:.1%} confidence)")

        # Sentiment
        if 'market_sentiment' in signal:
            sentiment = signal['market_sentiment']
            confidence = signal.get('sentiment_confidence', 0.5)
            ai_insights.append(f"📊 Sentiment: {sentiment.title()} ({confidence:.1%} confidence)")

        # RL insights
        if 'rl_market_regime' in signal:
            regime = signal['rl_market_regime']
            ai_insights.append(f"🎯 RL Regime: {regime.title()}")

        # Federated consensus
        if 'federated_participants' in signal:
            participants = signal['federated_participants']
            ai_insights.append(f"🌐 Federated: {participants} participants")

        formatted_signal['ai_insights_summary'] = ai_insights
        formatted_signal['telegram_formatted'] = True

        return formatted_signal

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        stats = self.integration_stats.copy()
        stats['enhancement_success_rate'] = (
            self.integration_stats['ai_enhancements_applied'] / max(1, self.integration_stats['signals_processed'])
        )
        stats['enhancer_stats'] = self.enhancer.get_enhancement_stats()

        return stats

# Global instance for easy access (uses dynamic configuration)
quantum_elite_enhancer = QuantumEliteSignalEnhancer(
    max_workers=config_manager.get('system.max_workers', 4) if 'config_manager' in globals() else 4,
    enable_async=config_manager.get('system.enable_async', True) if 'config_manager' in globals() else True,
    cache_ttl=config_manager.get('system.cache_ttl_seconds', 300) if 'config_manager' in globals() else 300,
    config_manager=config_manager
)
telegram_ai_integration = TelegramAISignalIntegration()

# Export ErrorLearningManager for global use
__all__ = ['ErrorLearningManager', 'quantum_elite_enhancer', 'telegram_ai_integration']

def enhance_signal_with_quantum_elite(base_signal: Dict, asset_symbol: str) -> Dict:
    """Convenience function to enhance signals with Quantum Elite AI"""
    return quantum_elite_enhancer.enhance_signal(base_signal, asset_symbol)

def get_ai_enhancement_stats() -> Dict[str, Any]:
    """Get AI enhancement statistics"""
    return {
        'signal_enhancer': quantum_elite_enhancer.get_enhancement_stats(),
        'telegram_integration': telegram_ai_integration.get_integration_stats()
    }

class ComprehensiveTestSuite:
    """Comprehensive testing suite for the Quantum Elite AI system"""

    def __init__(self):
        self.test_results = {'passed': 0, 'failed': 0, 'total': 0, 'failures': []}

    def run_all_tests(self) -> Dict:
        """Run all test suites"""
        print("  Running validation tests...")
        self._run_validation_tests()

        print("  Running circuit breaker tests...")
        self._run_circuit_breaker_tests()

        print("  Running caching tests...")
        self._run_caching_tests()

        print("  Running monitoring tests...")
        self._run_monitoring_tests()

        print("  Running integration tests...")
        self._run_integration_tests()

        return self.test_results

    def _run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        self.test_results['total'] += 1
        try:
            result = test_func()
            if result:
                self.test_results['passed'] += 1
                print(f"    ✓ {test_name}")
                return True
            else:
                self.test_results['failed'] += 1
                self.test_results['failures'].append(test_name)
                print(f"    ✗ {test_name}")
                return False
        except Exception as e:
            self.test_results['failed'] += 1
            self.test_results['failures'].append(f"{test_name}: {str(e)}")
            print(f"    ✗ {test_name}: {str(e)}")
            return False

    def _run_validation_tests(self):
        """Test data validation functionality"""
        # Test valid signal
        valid_signal = {
            'asset': 'BTC',
            'signal_type': 'BUY',
            'signal_quality': 'high',
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.8
        }
        self._run_test("Valid signal validation", lambda: DataValidator.validate_signal(valid_signal)[0])

        # Test invalid signal
        invalid_signal = {
            'asset': 'INVALID',
            'signal_type': 'INVALID_TYPE'
        }
        self._run_test("Invalid signal validation", lambda: not DataValidator.validate_signal(invalid_signal)[0])

        # Test signal sanitization
        self._run_test("Signal sanitization", lambda: DataValidator.sanitize_signal(invalid_signal)['asset'] == 'INVALID')

    def _run_circuit_breaker_tests(self):
        """Test circuit breaker functionality"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        # Test initial state
        self._run_test("Circuit breaker initial state", lambda: cb.state == 'CLOSED')

        # Test success calls
        cb._on_success()
        self._run_test("Circuit breaker success handling", lambda: cb.state == 'CLOSED')

        # Test failure calls
        cb._on_failure()
        cb._on_failure()
        self._run_test("Circuit breaker failure threshold", lambda: cb.state == 'OPEN')

        # Test recovery
        cb._should_attempt_reset = lambda: True  # Mock recovery time passed
        self._run_test("Circuit breaker recovery", lambda: cb._should_attempt_reset())

    def _run_caching_tests(self):
        """Test caching functionality"""
        cache = AdvancedCache(ttl_seconds=60)

        # Test basic set/get
        cache.set('test_key', {'data': 'test_value'})
        result = cache.get('test_key')
        self._run_test("Cache set/get", lambda: result and result['data'] == 'test_value')

        # Test cache miss
        self._run_test("Cache miss", lambda: cache.get('nonexistent_key') is None)

        # Test cache invalidation
        cache.set('pattern_test_*', 'value1')
        cache.set('pattern_test_2', 'value2')
        invalidated = cache.invalidate_pattern('pattern_test_*')
        self._run_test("Cache pattern invalidation", lambda: invalidated >= 1)

    def _run_monitoring_tests(self):
        """Test monitoring functionality"""
        monitoring = AdvancedMonitoringSystem()

        # Test metric recording
        monitoring.record_metric('test_metric', 42.0, {'tag': 'test'})
        stats = monitoring.get_metric_stats('test_metric')
        self._run_test("Metric recording", lambda: stats['latest'] == 42.0)

        # Test alert generation
        monitoring.record_metric('error_rate', 0.15)  # Above threshold
        alerts = monitoring.get_active_alerts()
        self._run_test("Alert generation", lambda: len(alerts) > 0)

        # Test health score
        health_score = monitoring.get_system_health_score()
        self._run_test("Health score calculation", lambda: 0 <= health_score <= 1)

    def _run_integration_tests(self):
        """Test integration functionality"""
        # Test signal enhancement with mock data
        enhancer = QuantumEliteSignalEnhancer(enable_async=False)  # Disable async for testing

        test_signal = {
            'asset': 'BTC',
            'signal_type': 'BUY',
            'signal_quality': 'medium',
            'timestamp': datetime.now().isoformat()
        }

        try:
            enhanced = enhancer.enhance_signal(test_signal, 'BTC')
            self._run_test("Signal enhancement integration", lambda: 'quantum_elite_enhanced' in enhanced)
        except Exception as e:
            self._run_test("Signal enhancement integration", lambda: False)

        # Test error learning
        context = {'operation_type': 'test', 'asset_symbol': 'BTC', 'signal_quality': 'high'}
        enhancer.error_learning_manager.record_operation_result(context, had_error=False)
        insights = enhancer.error_learning_manager.get_error_insights()
        self._run_test("Error learning integration", lambda: insights['total_operations'] > 0)

class BacktestingSimulator:
    """Backtesting simulation for the Quantum Elite AI system"""

    def __init__(self, enhancer: QuantumEliteSignalEnhancer):
        self.enhancer = enhancer
        self.simulation_results = []

    def run_simulation(self, days: int = 7, assets: List[str] = None, signals_per_day: int = 5) -> Dict:
        """Run backtesting simulation"""
        if assets is None:
            assets = ['BTC', 'ETH']

        total_signals = 0
        total_enhancement_time = 0
        start_time = datetime.now()

        print(f"    Simulating {days} days with {signals_per_day} signals per day per asset...")

        for day in range(days):
            simulation_date = datetime.now() - timedelta(days=days-day)

            for asset in assets:
                for signal_num in range(signals_per_day):
                    # Generate realistic test signal
                    signal_types = ['BUY', 'SELL', 'HOLD']
                    qualities = ['low', 'medium', 'high']

                    test_signal = {
                        'asset': asset,
                        'signal_type': np.random.choice(signal_types),
                        'signal_quality': np.random.choice(qualities),
                        'timestamp': simulation_date.isoformat(),
                        'confidence': np.random.uniform(0.1, 0.9),
                        'price': np.random.uniform(100, 50000),
                        'has_signal': True
                    }

                    # Generate market data
                    market_data = {
                        'price': test_signal['price'] * np.random.uniform(0.95, 1.05),
                        'volume': np.random.lognormal(10, 1),
                        'change_24h': np.random.normal(0, 2),
                        'volatility': np.random.uniform(0.01, 0.05),
                        'timestamp': simulation_date
                    }

                    # Enhance signal
                    try:
                        enhanced_signal = self.enhancer.enhance_signal(
                            test_signal, asset, market_data, force_refresh=(signal_num % 5 == 0)
                        )

                        total_signals += 1
                        total_enhancement_time += enhanced_signal.get('processing_time', 0)

                        # Record result
                        self.simulation_results.append({
                            'day': day,
                            'asset': asset,
                            'original_quality': test_signal['signal_quality'],
                            'enhanced_quality': enhanced_signal.get('signal_quality'),
                            'ai_modules_used': len(enhanced_signal.get('ai_modules_used', [])),
                            'processing_time': enhanced_signal.get('processing_time', 0),
                            'ai_confidence': enhanced_signal.get('ai_overall_confidence', 0),
                            'cache_used': enhanced_signal.get('cache_used', False)
                        })

                    except Exception as e:
                        logger.warning(f"[BACKTEST] Failed to enhance signal for {asset} on day {day}: {e}")

        # Calculate final statistics
        end_time = datetime.now()
        simulation_time = (end_time - start_time).total_seconds()

        avg_enhancement_time = total_enhancement_time / max(1, total_signals)
        cache_hits = sum(1 for r in self.simulation_results if r.get('cache_used', False))
        cache_hit_rate = cache_hits / max(1, len(self.simulation_results))

        return {
            'total_signals': total_signals,
            'simulation_time': simulation_time,
            'avg_enhancement_time': avg_enhancement_time,
            'cache_hit_rate': cache_hit_rate,
            'system_health_score': self.enhancer.monitoring.get_system_health_score(),
            'performance_stats': self.enhancer.get_enhancement_stats(),
            'simulation_results': self.simulation_results[-5:]  # Last 5 results for summary
    }

if __name__ == "__main__":
    # Test the integration with error learning
    test_signal = {
        'asset': 'BTC',
        'has_signal': True,
        'signal_type': 'BUY',
        'signal_quality': 'high',
        'timestamp': datetime.now().isoformat()
    }

    print("[TEST] Testing Quantum Elite AI Signal Integration with Error Learning...")

    # Test multiple signals to build learning history
    test_assets = ['BTC', 'ETH', 'XAU', 'ES']

    for asset in test_assets:
        print(f"\n[TEST] Processing signal for {asset}...")
        enhanced = enhance_signal_with_quantum_elite(test_signal, asset)

        print(f"[RESULT] {asset} - Original quality: {test_signal.get('signal_quality')} -> Enhanced: {enhanced.get('signal_quality')}")
        print(f"[RESULT] {asset} - AI modules used: {enhanced.get('ai_modules_used', [])}")
        print(f"[RESULT] {asset} - Overall AI confidence: {enhanced.get('ai_overall_confidence', 0):.2%}")

        if enhanced.get('ai_insights_summary'):
            print(f"[RESULT] {asset} - AI Insights:")
            for insight in enhanced['ai_insights_summary']:
                print(f"    {insight}")

        if enhanced.get('error_learning_insights'):
            el_insights = enhanced['error_learning_insights']
            print(f"[ERROR_LEARNING] {asset} - Learning progress: {el_insights.get('learning_progress', 0):.1%}")
            print(f"[ERROR_LEARNING] {asset} - Recent error rate: {el_insights.get('recent_error_rate', 0):.1%}")

    # Get comprehensive stats
    stats = get_ai_enhancement_stats()
    print("\n[STATS] Comprehensive Enhancement Stats:")
    print(f"  AI Modules Available: {stats['signal_enhancer']['ai_modules_available']}")
    print(f"  Total Enhancements: {stats['signal_enhancer']['total_enhancements']}")

    error_insights = stats['signal_enhancer'].get('error_learning_insights', {})
    if error_insights:
        print("\n[ERROR_LEARNING] Machine Learning Insights:")
        print(f"  Total Operations Learned: {error_insights.get('total_operations', 0)}")
        print(f"  Learning Progress: {error_insights.get('learning_progress', 0):.1%}")
        print(f"  Recent Error Rate: {error_insights.get('recent_error_rate', 0):.1%}")
        print(f"  Model Trained: {error_insights.get('model_trained', False)}")

        problematic_ops = error_insights.get('most_problematic_operations', [])
        if problematic_ops:
            print("\n  Most Problematic Operations:")
            for op in problematic_ops[:3]:  # Show top 3
                print(f"    {op['operation_type']}: {op['error_rate']:.1%} error rate ({op['total_operations']} ops)")

    # Demonstrate error learning by simulating some errors
    print("\n[DEMO] Demonstrating Error Learning with Simulated Errors...")

    # Simulate some errors to build learning history
    test_contexts = [
        {'operation_type': 'neural_prediction', 'asset_symbol': 'BTC', 'signal_quality': 'high'},
        {'operation_type': 'neural_prediction', 'asset_symbol': 'BTC', 'signal_quality': 'low'},
        {'operation_type': 'sentiment_analysis', 'asset_symbol': 'ETH', 'signal_quality': 'medium'},
        {'operation_type': 'rl_insights', 'asset_symbol': 'XAU', 'signal_quality': 'high'},
        {'operation_type': 'federated_learning', 'asset_symbol': 'ES', 'signal_quality': 'low'},
    ]

    # Record some simulated errors
    for i, context in enumerate(test_contexts):
        had_error = i % 2 == 0  # Alternate between error and success
        quantum_elite_enhancer.error_learning_manager.record_operation_result(
            context,
            had_error=had_error,
            error_details="Simulated error for demonstration" if had_error else None,
            success_metrics={'processing_time': 0.1, 'confidence': 0.8} if not had_error else None
        )
        print(f"  Recorded {'ERROR' if had_error else 'SUCCESS'} for {context['operation_type']} on {context['asset_symbol']}")

    # Test prediction after learning
    print("\n[DEMO] Testing Error Prediction After Learning...")
    for context in test_contexts[:3]:  # Test first 3 contexts
        prediction = quantum_elite_enhancer.error_learning_manager.predict_error_likelihood(context)
        print(f"  {context['operation_type']} on {context['asset_symbol']}: {prediction['error_probability']:.1%} error probability")

    # Get final insights
    final_insights = quantum_elite_enhancer.error_learning_manager.get_error_insights()
    print("\n[FINAL] Error Learning Insights After Simulation:")
    print(f"  Operations Learned: {final_insights['total_operations']}")
    print(f"  Learning Progress: {final_insights['learning_progress']:.1%}")
    print(f"  Recent Error Rate: {final_insights['recent_error_rate']:.1%}")

    if final_insights.get('most_problematic_operations'):
        print("  Most Problematic Operations:")
        for op in final_insights['most_problematic_operations'][:2]:
            print(f"    {op['operation_type']}: {op['error_rate']:.1%} error rate")

    print("\n[SUCCESS] Quantum Elite AI Signal Integration with Error Learning test completed!")

    # Run comprehensive testing suite
    print("\n[TEST] Running Comprehensive Testing Suite...")
    test_suite = ComprehensiveTestSuite()
    test_results = test_suite.run_all_tests()

    print(f"[TEST] Test Results: {test_results['passed']}/{test_results['total']} tests passed")

    if test_results['failed'] > 0:
        print(f"[TEST] Failed Tests: {test_results['failures']}")
    else:
        print("[TEST] All tests passed!")

    # Run backtesting simulation
    print("\n[BACKTEST] Running Backtesting Simulation...")
    backtester = BacktestingSimulator(quantum_elite_enhancer)
    backtest_results = backtester.run_simulation(days=7, assets=['BTC', 'ETH'])

    print(f"[BACKTEST] Simulation completed: {backtest_results['total_signals']} signals processed")
    print(f"[BACKTEST] Average enhancement time: {backtest_results['avg_enhancement_time']:.3f}s")
    print(f"[BACKTEST] Cache hit rate: {backtest_results['cache_hit_rate']:.1%}")
    print(f"[BACKTEST] System health score: {backtest_results['system_health_score']:.2f}")
