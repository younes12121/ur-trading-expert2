"""
Performance Dashboard
Real-time performance monitoring and visualization
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
import sys

try:
    from flask import Flask, render_template_string, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available. Dashboard will run in console mode only.")

class PerformanceDashboard:
    """Real-time performance monitoring dashboard"""
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.metrics = {
            'execution_times': deque(maxlen=max_history),
            'cache_hits': deque(maxlen=max_history),
            'cache_misses': deque(maxlen=max_history),
            'api_calls': deque(maxlen=max_history),
            'memory_usage': deque(maxlen=max_history),
            'cpu_usage': deque(maxlen=max_history),
            'error_rates': deque(maxlen=max_history),
            'throughput': deque(maxlen=max_history)
        }
        self.timestamps = deque(maxlen=max_history)
        self.running = False
        self.monitor_thread = None
        
    def record_metric(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Record a performance metric"""
        if metric_name in self.metrics:
            if timestamp is None:
                timestamp = datetime.now()
            self.metrics[metric_name].append(value)
            self.timestamps.append(timestamp)
    
    def get_metric_stats(self, metric_name: str, window_minutes: int = 60) -> Dict:
        """Get statistics for a metric over a time window"""
        if metric_name not in self.metrics:
            return {}
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        values = []
        
        for i, ts in enumerate(self.timestamps):
            if ts >= cutoff_time:
                if i < len(self.metrics[metric_name]):
                    values.append(self.metrics[metric_name][i])
        
        if not values:
            return {'count': 0}
        
        import numpy as np
        return {
            'count': len(values),
            'mean': float(np.mean(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'std': float(np.std(values)),
            'latest': float(values[-1]) if values else 0
        }
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        hits = list(self.metrics['cache_hits'])
        misses = list(self.metrics['cache_misses'])
        
        total = len(hits) + len(misses)
        if total == 0:
            return {'hit_rate': 0, 'total_requests': 0}
        
        hit_rate = len(hits) / total if total > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'total_requests': total,
            'hits': len(hits),
            'misses': len(misses)
        }
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary"""
        return {
            'execution_time': self.get_metric_stats('execution_times', 60),
            'cache': self.get_cache_stats(),
            'api_calls': self.get_metric_stats('api_calls', 60),
            'memory': self.get_metric_stats('memory_usage', 60),
            'cpu': self.get_metric_stats('cpu_usage', 60),
            'errors': self.get_metric_stats('error_rates', 60),
            'throughput': self.get_metric_stats('throughput', 60)
        }
    
    def start_monitoring(self, interval: float = 1.0):
        """Start background monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _monitor_loop(self, interval: float):
        """Background monitoring loop"""
        import psutil
        process = psutil.Process()
        
        while self.running:
            try:
                # Monitor system resources
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                cpu_percent = process.cpu_percent(interval=0.1)
                
                self.record_metric('memory_usage', memory_mb)
                self.record_metric('cpu_usage', cpu_percent)
                
                time.sleep(interval)
            except Exception:
                break
    
    def export_data(self, filename: Optional[str] = None) -> str:
        """Export metrics data to JSON"""
        if filename is None:
            filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'timestamps': [ts.isoformat() for ts in self.timestamps],
            'metrics': {
                name: list(values) for name, values in self.metrics.items()
            },
            'summary': self.get_performance_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename

def create_web_dashboard(dashboard: PerformanceDashboard):
    """Create Flask web dashboard"""
    if not FLASK_AVAILABLE:
        print("Flask not available. Install with: pip install flask")
        return None
    
    app = Flask(__name__)
    
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performance Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .metric-card { border: 1px solid #ddd; padding: 15px; margin: 10px; display: inline-block; width: 200px; }
            .metric-value { font-size: 24px; font-weight: bold; }
            .metric-label { color: #666; }
        </style>
    </head>
    <body>
        <h1>Performance Dashboard</h1>
        <div id="metrics"></div>
        <canvas id="chart" width="800" height="400"></canvas>
        <script>
            function updateMetrics() {
                fetch('/api/metrics')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('metrics').innerHTML = 
                            '<div class="metric-card"><div class="metric-label">Execution Time</div><div class="metric-value">' + 
                            data.execution_time.mean.toFixed(3) + 's</div></div>' +
                            '<div class="metric-card"><div class="metric-label">Cache Hit Rate</div><div class="metric-value">' + 
                            (data.cache.hit_rate * 100).toFixed(1) + '%</div></div>' +
                            '<div class="metric-card"><div class="metric-label">Memory Usage</div><div class="metric-value">' + 
                            data.memory.latest.toFixed(1) + 'MB</div></div>' +
                            '<div class="metric-card"><div class="metric-label">CPU Usage</div><div class="metric-value">' + 
                            data.cpu.latest.toFixed(1) + '%</div></div>';
                    });
            }
            setInterval(updateMetrics, 1000);
            updateMetrics();
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(dashboard_html)
    
    @app.route('/api/metrics')
    def api_metrics():
        return jsonify(dashboard.get_performance_summary())
    
    return app

def run_console_dashboard(dashboard: PerformanceDashboard):
    """Run console-based dashboard"""
    print("="*60)
    print("PERFORMANCE DASHBOARD (Console Mode)")
    print("="*60)
    print("Press Ctrl+C to stop\n")
    
    dashboard.start_monitoring()
    
    try:
        while True:
            summary = dashboard.get_performance_summary()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Performance Metrics:")
            print(f"  Execution Time: {summary['execution_time'].get('mean', 0):.3f}s (avg)")
            print(f"  Cache Hit Rate: {summary['cache'].get('hit_rate', 0)*100:.1f}%")
            print(f"  Memory Usage: {summary['memory'].get('latest', 0):.1f}MB")
            print(f"  CPU Usage: {summary['cpu'].get('latest', 0):.1f}%")
            print(f"  API Calls: {summary['api_calls'].get('count', 0)} (last hour)")
            print(f"  Error Rate: {summary['errors'].get('mean', 0)*100:.2f}%")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        dashboard.stop_monitoring()

def main():
    """Main dashboard runner"""
    dashboard = PerformanceDashboard()
    
    if FLASK_AVAILABLE and len(sys.argv) > 1 and sys.argv[1] == '--web':
        # Run web dashboard
        app = create_web_dashboard(dashboard)
        if app:
            dashboard.start_monitoring()
            print("Starting web dashboard on http://localhost:5000")
            app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        # Run console dashboard
        run_console_dashboard(dashboard)

if __name__ == "__main__":
    main()
