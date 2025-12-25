#!/usr/bin/env python3
"""
Simple test of the Professional Error Learning System
"""

from global_error_learning import predict_error, record_error, get_error_insights
from error_dashboard import get_dashboard_report

print("Testing Professional Error Learning System...")

# Test prediction
pred = predict_error('test_component', {'operation_type': 'test', 'system_load': 0.5})
print(f"Error Prediction: {pred['error_probability']:.1%} risk")

# Record some operations
record_error('test_component', {'operation_type': 'test'}, had_error=False, execution_time=0.1)
record_error('test_component', {'operation_type': 'test'}, had_error=True, execution_time=0.1)

# Get insights
insights = get_error_insights()
print(f"Learned {insights['total_operations']} operations")
print(f"Learning Progress: {insights['learning_progress']:.1%}")

# Test dashboard
report = get_dashboard_report('summary')
print("Dashboard report generated successfully")

print("Error Learning System Ready for Production!")
