"""
AI Staging Monitoring Dashboard
Real-time monitoring of AI system performance in staging
"""

import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import psutil
import os
from pathlib import Path

class StagingMonitor:
    def __init__(self):
        self.staging_dir = Path("staging")
        self.metrics_history = []
        self.start_time = datetime.now()

    def get_system_metrics(self):
        """Get current system metrics"""
        return {
            "timestamp": datetime.now(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }

    def get_ai_metrics(self):
        """Get AI system metrics (placeholder for real metrics)"""
        return {
            "predictions_per_minute": 120 + np.random.normal(0, 10),
            "average_response_time": 0.45 + np.random.normal(0, 0.05),
            "error_rate": max(0, 0.02 + np.random.normal(0, 0.01)),
            "model_accuracy": 0.95 + np.random.normal(0, 0.02),
            "active_users": 15 + np.random.randint(-3, 3),
            "federated_clients": 8 + np.random.randint(-2, 2)
        }

    def create_dashboard(self):
        """Create Dash monitoring dashboard"""
        app = dash.Dash(__name__, title="AI Staging Monitor")

        app.layout = html.Div([
            html.H1("AI Staging Monitor", style={'textAlign': 'center'}),

            # System Metrics
            html.Div([
                html.H2("System Performance"),
                html.Div(id='system-metrics', children=self._create_system_metrics_display())
            ], style={'margin': '20px'}),

            # AI Metrics
            html.Div([
                html.H2("AI System Metrics"),
                html.Div(id='ai-metrics', children=self._create_ai_metrics_display())
            ], style={'margin': '20px'}),

            # Performance Charts
            html.Div([
                html.H2("Performance Trends"),
                dcc.Graph(id='performance-chart'),
                dcc.Interval(id='interval-component', interval=5000, n_intervals=0)  # Update every 5 seconds
            ], style={'margin': '20px'}),

            # Status Indicators
            html.Div([
                html.H2("System Status"),
                html.Div(id='status-indicators', children=self._create_status_indicators())
            ], style={'margin': '20px'})
        ])

        @app.callback(
            [Output('system-metrics', 'children'),
             Output('ai-metrics', 'children'),
             Output('performance-chart', 'figure'),
             Output('status-indicators', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_dashboard(n):
            system_metrics = self.get_system_metrics()
            ai_metrics = self.get_ai_metrics()

            # Store metrics history
            self.metrics_history.append({
                'timestamp': system_metrics['timestamp'],
                **system_metrics,
                **ai_metrics
            })

            # Keep only last 100 points
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]

            return (
                self._create_system_metrics_display(system_metrics),
                self._create_ai_metrics_display(ai_metrics),
                self._create_performance_chart(),
                self._create_status_indicators(ai_metrics)
            )

        return app

    def _create_system_metrics_display(self, metrics=None):
        """Create system metrics display"""
        if metrics is None:
            metrics = self.get_system_metrics()

        return html.Div([
            html.Div([
                html.H4("CPU Usage"),
                html.P(".1f")
            ], className="metric-card"),
            html.Div([
                html.H4("Memory Usage"),
                html.P(".1f")
            ], className="metric-card"),
            html.Div([
                html.H4("Disk Usage"),
                html.P(".1f")
            ], className="metric-card"),
            html.Div([
                html.H4("Uptime"),
                html.P(".1f")
            ], className="metric-card")
        ], style={'display': 'flex', 'justifyContent': 'space-around'})

    def _create_ai_metrics_display(self, metrics=None):
        """Create AI metrics display"""
        if metrics is None:
            metrics = self.get_ai_metrics()

        return html.Div([
            html.Div([
                html.H4("Predictions/min"),
                html.P(".1f")
            ], className="metric-card"),
            html.Div([
                html.H4("Response Time"),
                html.P(".3f")
            ], className="metric-card"),
            html.Div([
                html.H4("Model Accuracy"),
                html.P(".1%")
            ], className="metric-card"),
            html.Div([
                html.H4("Active Users"),
                html.P(str(int(metrics['active_users'])))
            ], className="metric-card")
        ], style={'display': 'flex', 'justifyContent': 'space-around'})

    def _create_performance_chart(self):
        """Create performance trend chart"""
        if not self.metrics_history:
            return go.Figure()

        df = pd.DataFrame(self.metrics_history[-50:])  # Last 50 points

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['predictions_per_minute'],
            mode='lines+markers',
            name='Predictions/min',
            line=dict(color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['average_response_time'] * 100,  # Convert to milliseconds
            mode='lines+markers',
            name='Response Time (ms)',
            line=dict(color='green'),
            yaxis='y2'
        ))

        fig.update_layout(
            title="AI Performance Trends",
            xaxis_title="Time",
            yaxis_title="Predictions/min",
            yaxis2=dict(title="Response Time (ms)", overlaying='y', side='right'),
            showlegend=True
        )

        return fig

    def _create_status_indicators(self, ai_metrics=None):
        """Create status indicators"""
        if ai_metrics is None:
            ai_metrics = self.get_ai_metrics()

        indicators = []

        # Performance indicators
        status_checks = {
            "Model Accuracy": ai_metrics['model_accuracy'] > 0.9,
            "Response Time": ai_metrics['average_response_time'] < 1.0,
            "Error Rate": ai_metrics['error_rate'] < 0.05,
            "System Load": True  # Placeholder
        }

        for check_name, status in status_checks.items():
            color = "green" if status else "red"
            symbol = "[OK]" if status else "[ERROR]"
            indicators.append(
                html.Div([
                    html.Span(f"{symbol} {check_name}", style={'color': color})
                ], style={'margin': '10px'})
            )

        return html.Div(indicators, style={'display': 'flex', 'flexWrap': 'wrap'})

if __name__ == "__main__":
    import numpy as np

    monitor = StagingMonitor()
    app = monitor.create_dashboard()

    # Add custom CSS
    app.css.append_css({
        'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
    })

    print("[INFO] Starting AI Staging Monitor Dashboard...")
    print("[INFO] Open your browser to: http://127.0.0.1:8050")
    app.run_server(debug=True, host='0.0.0.0', port=8050)
