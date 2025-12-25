# 🔧 Error Learning System API Reference

## Core API Functions

### `predict_error(component, operation_context)`

Predicts the likelihood of an error occurring for a specific operation.

#### Parameters
- **component** (`str`): Component name
  - `'telegram_bot'`: User interface operations
  - `'execution_manager'`: Trade execution operations
  - `'risk_manager'`: Risk assessment operations
  - `'data_fetcher'`: Market data operations
  - `'backtest_engine'`: Strategy testing operations
  - `'signal_generator'`: Signal generation operations

- **operation_context** (`dict`): Dictionary containing operation details and system state
  - `operation_type` (`str`): Type of operation being performed
  - `system_load` (`float`, optional): Current system load (0.0-1.0)
  - `memory_usage` (`float`, optional): Memory usage (0.0-1.0)
  - `time_of_day` (`float`, optional): Hour of day (0.0-24.0)
  - Component-specific fields (see examples below)

#### Returns
```python
{
    'error_probability': float,  # 0.0-1.0: Likelihood of error
    'confidence': float,         # 0.0-1.0: Prediction confidence
    'should_attempt': bool,      # Whether to proceed with operation
    'alternative_suggestions': list,  # Alternative approaches
    'risk_level': str           # 'low', 'medium', 'high', 'critical'
}
```

#### Example Usage
```python
from global_error_learning import predict_error

# Predict data fetching error
prediction = predict_error('data_fetcher', {
    'operation_type': 'get_market_data',
    'symbol': 'BTCUSDT',
    'timeframe': '1h',
    'system_load': 0.7,
    'memory_usage': 0.6
})

if prediction['should_attempt']:
    # Proceed with operation
    data = fetch_market_data()
else:
    print(f"High error risk ({prediction['error_probability']:.1%})")
    # Use cached data or alternative approach
```

---

### `record_error(component, operation_context, had_error, **kwargs)`

Records the result of an operation for machine learning.

#### Parameters
- **component** (`str`): Component name (same as predict_error)
- **operation_context** (`dict`): Operation context (same as predict_error)
- **had_error** (`bool`): Whether the operation failed
- **error_details** (`str`, optional): Description of the error
- **success_metrics** (`dict`, optional): Success measurements
- **execution_time** (`float`, optional): Operation duration in seconds

#### Returns
`None`

#### Example Usage
```python
from global_error_learning import record_error

# Record successful operation
record_error('data_fetcher', {
    'operation_type': 'get_market_data',
    'symbol': 'BTCUSDT'
}, had_error=False, execution_time=0.234)

# Record failed operation
record_error('execution_manager', {
    'operation_type': 'place_order',
    'symbol': 'BTCUSDT',
    'order_type': 'market'
}, had_error=True, error_details="API rate limit exceeded")
```

---

### `get_error_insights(component=None)`

Retrieves comprehensive error analytics and insights.

#### Parameters
- **component** (`str`, optional): Specific component or `None` for system-wide insights

#### Returns
```python
{
    'total_operations': int,           # Total operations recorded
    'error_patterns': dict,            # Component-specific error patterns
    'performance_metrics': dict,       # System performance data
    'model_trained': bool,             # Whether ML model is trained
    'training_data_size': int,         # Size of training dataset
    'learning_progress': float,        # Learning progress (0.0-1.0)
    'recent_error_rate': float,        # Recent error rate
    'most_problematic_components': list, # Top error-prone components
    'system_health_score': float       # Overall system health (0-100)
}
```

#### Example Usage
```python
from global_error_learning import get_error_insights

# Get system-wide insights
insights = get_error_insights()
print(f"System Health: {insights['system_health_score']:.1f}/100")
print(f"Error Rate: {insights['recent_error_rate']:.2%}")

# Get component-specific insights
data_fetcher_insights = get_error_insights('data_fetcher')
print(f"Data Fetcher Error Rate: {data_fetcher_insights['recent_error_rate']:.2%}")
```

---

## Advanced Features API

### `detect_anomalies(metrics)`

Detects anomalies in system metrics using machine learning.

#### Parameters
- **metrics** (`dict`): Current system metrics
  - `recent_error_rate`: Recent error frequency
  - `system_health_score`: Overall system health
  - `avg_prediction_time`: Average prediction time
  - `memory_usage_mb`: Memory usage
  - `cpu_usage_percent`: CPU usage
  - `learning_progress`: Learning progress
  - `active_alerts`: Number of active alerts
  - `total_operations`: Total operations
  - `cache_hit_rate`: Cache performance

#### Returns
```python
[
    {
        'type': 'anomaly_detected',
        'anomaly_type': str,      # Type of anomaly detected
        'severity': str,          # 'critical', 'high', 'medium', 'low'
        'confidence': float,      # Detection confidence
        'features': dict,         # Anomaly features
        'timestamp': str,         # Detection timestamp
        'recommendations': list   # Action recommendations
    }
]
```

#### Example Usage
```python
from advanced_error_features import detect_anomalies

current_metrics = {
    'recent_error_rate': 0.15,
    'system_health_score': 75,
    'memory_usage_mb': 450,
    'cpu_usage_percent': 85
}

anomalies = detect_anomalies(current_metrics)
for anomaly in anomalies:
    print(f"Anomaly: {anomaly['anomaly_type']} (Severity: {anomaly['severity']})")
```

---

### `assess_component_health(component, metrics)`

Assesses the health status of a specific component.

#### Parameters
- **component** (`str`): Component name
- **metrics** (`dict`): Component-specific metrics
  - `error_rate`: Component error rate
  - `response_time`: Average response time
  - `success_rate`: Operation success rate
  - Component-specific metrics

#### Returns
```python
{
    'component': str,
    'health_score': float,           # 0.0-1.0: Health score
    'health_status': str,            # 'good', 'fair', 'warning', 'critical'
    'predicted_failure_hours': float,# Hours until likely failure (or None)
    'maintenance_needed': bool,      # Whether maintenance is needed
    'urgent_maintenance': bool,      # Whether urgent maintenance needed
    'recommendations': list,         # Maintenance recommendations
    'timestamp': str
}
```

#### Example Usage
```python
from advanced_error_features import assess_component_health

health = assess_component_health('data_fetcher', {
    'error_rate': 0.08,
    'response_time': 0.12,
    'success_rate': 0.92,
    'cache_hit_rate': 0.85
})

print(f"Health Status: {health['health_status']} ({health['health_score']:.1%})")
if health['predicted_failure_hours']:
    print(f"Predicted failure in: {health['predicted_failure_hours']:.1f} hours")
```

---

### `get_dashboard_report(report_type)`

Generates comprehensive system reports.

#### Parameters
- **report_type** (`str`): Type of report
  - `'summary'`: Brief system overview
  - `'full'`: Comprehensive analysis
  - `'technical'`: Detailed technical metrics

#### Returns
`str`: Formatted report text

#### Example Usage
```python
from error_dashboard import get_dashboard_report

# Generate full system report
report = get_dashboard_report('full')
print(report)

# Save to file
with open('error_report.txt', 'w') as f:
    f.write(report)
```

---

## Monitoring & Alerting API

### `start_monitoring()`

Starts the production monitoring system.

#### Parameters
None

#### Returns
None

#### Example Usage
```python
from production_monitoring import start_monitoring

# Start monitoring with configured alert channels
start_monitoring()
print("Production monitoring started")
```

---

### `configure_alert_channel(channel, config)`

Configures alert communication channels.

#### Parameters
- **channel** (`str`): Channel type (`'email'`, `'slack'`, `'telegram'`)
- **config** (`dict`): Channel configuration

#### Email Configuration
```python
configure_alert_channel('email', {
    'enabled': True,
    'sender_email': 'alerts@yourbot.com',
    'recipient_emails': ['admin@yourbot.com'],
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_password': 'your_password'
})
```

#### Slack Configuration
```python
configure_alert_channel('slack', {
    'enabled': True,
    'webhook_url': 'https://hooks.slack.com/services/...',
    'channel': '#alerts'
})
```

#### Telegram Configuration
```python
configure_alert_channel('telegram', {
    'enabled': True,
    'bot_token': 'your_bot_token',
    'chat_ids': ['123456789', '987654321']
})
```

---

### `get_monitoring_status()`

Gets current monitoring system status.

#### Parameters
None

#### Returns
```python
{
    'monitoring_active': bool,
    'health_check_interval': int,
    'alert_check_interval': int,
    'communication_channels': dict,
    'recent_alerts': int,
    'system_health': dict,
    'active_alerts': list
}
```

#### Example Usage
```python
from production_monitoring import get_monitoring_status

status = get_monitoring_status()
print(f"Monitoring Active: {status['monitoring_active']}")
print(f"System Health: {status['system_health']['system_health_score']:.1f}/100")
print(f"Active Alerts: {len(status['active_alerts'])}")
```

---

## Performance Optimization API

### `force_optimization()`

Forces immediate system optimization cycle.

#### Parameters
None

#### Returns
```python
{
    'optimization_active': bool,
    'current_metrics': dict,
    'targets': dict,
    'recent_optimizations': list,
    'performance_trends': dict
}
```

#### Example Usage
```python
from performance_optimizer import force_optimization

result = force_optimization()
print(f"Optimization completed - improvements: {len(result['recent_optimizations'])}")
```

---

### `get_optimization_status()`

Gets current optimization system status.

#### Parameters
None

#### Returns
Same as `force_optimization()`

#### Example Usage
```python
from performance_optimizer import get_optimization_status

status = get_optimization_status()
print(f"CPU Usage: {status['current_metrics']['cpu_usage_percent']:.1f}%")
print(f"Memory Usage: {status['current_metrics']['memory_usage_mb']:.1f}MB")
```

---

## Component-Specific APIs

### Telegram Bot Integration

```python
# Before command execution
operation_context = {
    'command_type': 'signal_request',
    'user_tier': 'premium',
    'api_calls_today': 45,
    'system_load': 0.6,
    'memory_usage': 0.5
}

prediction = predict_error('telegram_bot', operation_context)
if prediction['should_attempt']:
    # Execute command
    result = execute_signal_command()
    record_error('telegram_bot', operation_context, had_error=(result is None))
else:
    # Send user-friendly error message
    send_error_message("System busy, please try again in a moment")
```

### Execution Manager Integration

```python
# Before trade execution
operation_context = {
    'operation_type': 'place_market_order',
    'asset_symbol': 'BTC',
    'position_size': 0.1,
    'market_volatility': 0.025,
    'spread_width': 0.0005,
    'liquidity_score': 0.85
}

prediction = predict_error('execution_manager', operation_context)
if prediction['should_attempt']:
    # Execute trade
    order_result = place_market_order(order_details)
    record_error('execution_manager', operation_context, had_error=(order_result is None))
else:
    # Use alternative execution method
    logger.info(f"Switching to limit order due to high error risk: {prediction['error_probability']:.1%}")
```

### Risk Manager Integration

```python
# Before risk calculation
operation_context = {
    'operation_type': 'calculate_position_size',
    'balance': 10000,
    'confidence_level': 0.85,
    'market_regime': 'normal',
    'volatility': 0.02,
    'correlation_risk': 0.15,
    'drawdown_pct': 2.5
}

prediction = predict_error('risk_manager', operation_context)
if prediction['should_attempt']:
    # Calculate position size
    position_size = calculate_position_size(risk_params)
    record_error('risk_manager', operation_context, had_error=(position_size is None))
else:
    # Use conservative defaults
    position_size = balance * 0.005  # 0.5% risk
    logger.warning(f"Using conservative position sizing due to error risk: {prediction['error_probability']:.1%}")
```

### Data Fetcher Integration

```python
# Before data fetching
operation_context = {
    'operation_type': 'get_klines',
    'symbol': 'BTCUSDT',
    'timeframe': '1h',
    'api_endpoint': 'binance_api',
    'rate_limit_status': 0.2,  # 20% of limit used
    'network_latency': 85,     # 85ms average latency
    'cache_hit_rate': 0.75
}

prediction = predict_error('data_fetcher', operation_context)
if prediction['should_attempt']:
    # Fetch data
    klines_data = get_klines(symbol, timeframe)
    record_error('data_fetcher', operation_context, had_error=(klines_data is None))
else:
    # Use cached data or alternative source
    klines_data = get_cached_data(symbol, timeframe)
    logger.info(f"Using cached data due to API error risk: {prediction['error_probability']:.1%}")
```

---

## Error Codes and Handling

### Common Error Codes

- **ERR_PREDICTION_FAILED**: ML prediction failed
- **ERR_MODEL_NOT_TRAINED**: Model not yet trained
- **ERR_INVALID_COMPONENT**: Unknown component name
- **ERR_MISSING_CONTEXT**: Required context data missing
- **ERR_MONITORING_FAILED**: Monitoring system error

### Error Handling Best Practices

```python
try:
    prediction = predict_error(component, context)
except Exception as e:
    # Fallback to conservative behavior
    logger.error(f"Prediction failed: {e}")
    prediction = {
        'error_probability': 0.5,  # Conservative default
        'should_attempt': True,    # Allow operation but log
        'risk_level': 'medium'
    }

try:
    record_error(component, context, had_error=operation_failed)
except Exception as e:
    # Don't let error recording break the main operation
    logger.warning(f"Error recording failed: {e}")
```

---

## Performance Benchmarks

### Expected Performance

| Operation | Target Response Time | Target Accuracy |
|-----------|---------------------|-----------------|
| Error Prediction | <50ms | >80% |
| Error Recording | <10ms | N/A |
| Anomaly Detection | <100ms | >85% |
| Health Assessment | <50ms | >90% |
| Report Generation | <5 seconds | N/A |

### System Requirements

- **Memory**: 256MB minimum, 1GB recommended
- **CPU**: 1 core minimum, 2+ cores recommended
- **Storage**: 100MB for models, 500MB for logs
- **Network**: Required for external monitoring/alerting

---

## Configuration Reference

### Environment Variables

```bash
# Error Learning Configuration
ERROR_LEARNING_ENABLED=true
ERROR_LEARNING_MODEL_PATH=/path/to/models
ERROR_LEARNING_MAX_HISTORY=2000

# Monitoring Configuration
MONITORING_ENABLED=true
MONITORING_CONFIG_PATH=/path/to/config.json

# Performance Optimization
OPTIMIZATION_ENABLED=true
OPTIMIZATION_INTERVAL_HOURS=6

# Alert Configuration
ALERT_EMAIL_ENABLED=true
ALERT_SLACK_ENABLED=false
ALERT_TELEGRAM_ENABLED=true
```

### Configuration File Structure

See `monitoring_config.json` and `ERROR_LEARNING_SYSTEM_GUIDE.md` for complete configuration options.

---

## Troubleshooting

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed error learning logging
from global_error_learning import global_error_manager
global_error_manager.debug_mode = True
```

### Health Checks

```python
# Quick system health check
insights = get_error_insights()
if insights['system_health_score'] < 50:
    print("WARNING: System health critical")
    # Take corrective action

# Component-specific health
for component in ['telegram_bot', 'execution_manager', 'risk_manager']:
    comp_insights = get_error_insights(component)
    if comp_insights['recent_error_rate'] > 0.2:
        print(f"WARNING: {component} error rate high")
```

---

## Version History

- **v1.0.0**: Initial release with core error prediction
- **v1.1.0**: Added anomaly detection and predictive maintenance
- **v1.2.0**: Production monitoring and alerting system
- **v1.3.0**: Performance optimization and automated reporting
- **v2.0.0**: Advanced features and enterprise scalability

---

*For additional support and advanced usage examples, see the comprehensive user guide.*
