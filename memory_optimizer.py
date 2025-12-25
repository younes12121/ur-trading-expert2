"""
Memory Optimizer
Memory usage monitoring, optimization, and leak detection
"""

import gc
import psutil
import threading
import time
import logging
import weakref
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import tracemalloc
import sys

class MemoryOptimizer:
    """Memory management and optimization system"""

    def __init__(self, memory_threshold_mb: float = 500.0,
                 gc_threshold_mb: float = 200.0,
                 monitoring_interval: float = 30.0):
        self.memory_threshold_mb = memory_threshold_mb
        self.gc_threshold_mb = gc_threshold_mb
        self.monitoring_interval = monitoring_interval

        # Process monitoring
        self.process = psutil.Process()
        self.logger = logging.getLogger('memory_optimizer')

        # Memory tracking
        self.memory_history = deque(maxlen=100)
        self.memory_peaks = []
        self.gc_stats = {
            'collections': 0,
            'objects_collected': 0,
            'last_gc_time': None
        }

        # Object tracking
        self.object_refs = weakref.WeakSet()
        self.object_counts = defaultdict(int)

        # Memory tracing
        self.tracing_active = False
        self.trace_snapshots = []

        # Monitoring thread
        self.monitoring_active = False
        self.monitor_thread = None

        # Callbacks
        self.memory_callbacks: List[Callable] = []
        self.leak_callbacks: List[Callable] = []

    def start_monitoring(self):
        """Start background memory monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="MemoryMonitor"
        )
        self.monitor_thread.start()
        self.logger.info("Memory monitoring started")

    def stop_monitoring(self):
        """Stop background memory monitoring"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        self.logger.info("Memory monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_memory_usage()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                break

    def _check_memory_usage(self):
        """Check current memory usage and trigger actions if needed"""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # Record memory usage
            timestamp = datetime.now()
            self.memory_history.append((timestamp, memory_mb))

            # Track memory peaks
            if not self.memory_peaks or memory_mb > max(p[1] for p in self.memory_peaks):
                self.memory_peaks.append((timestamp, memory_mb))

                # Keep only last 10 peaks
                if len(self.memory_peaks) > 10:
                    self.memory_peaks = sorted(self.memory_peaks, key=lambda x: x[1], reverse=True)[:10]

            # Check thresholds
            if memory_mb > self.memory_threshold_mb:
                self.logger.warning(".2f")
                self._trigger_memory_callbacks(memory_mb)

            if memory_mb > self.gc_threshold_mb:
                self._perform_garbage_collection()

            # Check for memory leaks
            self._check_memory_leaks()

        except Exception as e:
            self.logger.error(f"Memory check failed: {e}")

    def _perform_garbage_collection(self):
        """Perform garbage collection"""
        try:
            start_time = time.time()

            # Force garbage collection
            collected = gc.collect()

            gc_time = time.time() - start_time

            # Update stats
            self.gc_stats['collections'] += 1
            self.gc_stats['objects_collected'] += collected
            self.gc_stats['last_gc_time'] = datetime.now()

            self.logger.info(f"Garbage collection completed: {collected} objects collected in {gc_time:.3f}s")

        except Exception as e:
            self.logger.error(f"Garbage collection failed: {e}")

    def _check_memory_leaks(self):
        """Check for potential memory leaks"""
        try:
            # Simple leak detection based on trend
            if len(self.memory_history) >= 10:
                recent_memory = [m for _, m in list(self.memory_history)[-10:]]
                trend = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)

                # If memory is consistently increasing
                if trend > 5.0:  # More than 5MB increase over last 10 checks
                    self.logger.warning(".2f")
                    self._trigger_leak_callbacks(trend)

        except Exception as e:
            self.logger.error(f"Memory leak check failed: {e}")

    def _trigger_memory_callbacks(self, memory_mb: float):
        """Trigger memory threshold callbacks"""
        for callback in self.memory_callbacks:
            try:
                callback(memory_mb)
            except Exception as e:
                self.logger.error(f"Memory callback failed: {e}")

    def _trigger_leak_callbacks(self, trend: float):
        """Trigger memory leak callbacks"""
        for callback in self.leak_callbacks:
            try:
                callback(trend)
            except Exception as e:
                self.logger.error(f"Leak callback failed: {e}")

    def add_memory_callback(self, callback: Callable):
        """Add callback for memory threshold events"""
        self.memory_callbacks.append(callback)

    def add_leak_callback(self, callback: Callable):
        """Add callback for memory leak events"""
        self.leak_callbacks.append(callback)

    def get_memory_stats(self) -> Dict:
        """Get current memory statistics"""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            return {
                'current_memory_mb': memory_mb,
                'peak_memory_mb': max((p[1] for p in self.memory_peaks), default=0),
                'memory_threshold_mb': self.memory_threshold_mb,
                'gc_threshold_mb': self.gc_threshold_mb,
                'gc_collections': self.gc_stats['collections'],
                'objects_collected': self.gc_stats['objects_collected'],
                'last_gc_time': self.gc_stats['last_gc_time'],
                'history_points': len(self.memory_history),
                'monitoring_active': self.monitoring_active
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {}

    def optimize_data_structures(self, data: Any) -> Any:
        """Optimize data structures for memory efficiency"""
        try:
            if isinstance(data, list):
                # Convert lists to tuples where appropriate
                if all(isinstance(item, (int, float, str)) for item in data):
                    return tuple(data)

            elif isinstance(data, dict):
                # Use more memory-efficient dict operations
                return {k: self.optimize_data_structures(v) for k, v in data.items()}

            elif hasattr(data, '__dict__'):
                # For objects, optimize their attributes
                for attr in dir(data):
                    if not attr.startswith('_'):
                        try:
                            current_value = getattr(data, attr)
                            optimized_value = self.optimize_data_structures(current_value)
                            if optimized_value is not current_value:
                                setattr(data, attr, optimized_value)
                        except:
                            pass

            return data

        except Exception as e:
            self.logger.error(f"Data structure optimization failed: {e}")
            return data

    def start_memory_tracing(self):
        """Start memory tracing for detailed analysis"""
        if not self.tracing_active:
            tracemalloc.start()
            self.tracing_active = True
            self.logger.info("Memory tracing started")

    def stop_memory_tracing(self):
        """Stop memory tracing"""
        if self.tracing_active:
            tracemalloc.stop()
            self.tracing_active = False
            self.logger.info("Memory tracing stopped")

    def take_memory_snapshot(self) -> Optional[Any]:
        """Take a memory snapshot for analysis"""
        if not self.tracing_active:
            self.start_memory_tracing()

        try:
            snapshot = tracemalloc.take_snapshot()
            self.trace_snapshots.append((datetime.now(), snapshot))

            # Keep only last 5 snapshots
            if len(self.trace_snapshots) > 5:
                self.trace_snapshots = self.trace_snapshots[-5:]

            return snapshot
        except Exception as e:
            self.logger.error(f"Memory snapshot failed: {e}")
            return None

    def analyze_memory_usage(self) -> Dict:
        """Analyze memory usage patterns"""
        if not self.trace_snapshots:
            return {}

        try:
            # Get the most recent snapshot
            _, snapshot = self.trace_snapshots[-1]

            # Get top memory consumers
            top_stats = snapshot.statistics('lineno')

            analysis = {
                'total_memory_blocks': len(snapshot.traces),
                'top_consumers': []
            }

            for stat in top_stats[:10]:  # Top 10
                analysis['top_consumers'].append({
                    'size': stat.size,
                    'count': stat.count,
                    'average': stat.size / stat.count if stat.count > 0 else 0,
                    'traceback': stat.traceback.format()[:200]  # First 200 chars
                })

            return analysis

        except Exception as e:
            self.logger.error(f"Memory analysis failed: {e}")
            return {}

    def force_cleanup(self):
        """Force aggressive cleanup"""
        try:
            # Clear various caches
            gc.collect(2)  # Full collection

            # Clear any module-level caches if they exist
            import sys
            for module in sys.modules.values():
                if hasattr(module, '_cache'):
                    try:
                        module._cache.clear()
                    except:
                        pass

            self.logger.info("Aggressive cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

    def get_memory_report(self) -> str:
        """Generate a comprehensive memory report"""
        stats = self.get_memory_stats()
        analysis = self.analyze_memory_usage()

        report = []
        report.append("=" * 60)
        report.append("MEMORY OPTIMIZER REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        report.append("CURRENT STATUS:")
        report.append(".2f")
        report.append(".2f")
        report.append(".2f")
        report.append(".2f")
        report.append("")

        if stats.get('gc_collections', 0) > 0:
            report.append("GARBAGE COLLECTION:")
            report.append(f"  Collections: {stats['gc_collections']}")
            report.append(f"  Objects collected: {stats['objects_collected']}")
            if stats.get('last_gc_time'):
                report.append(f"  Last GC: {stats['last_gc_time'].strftime('%H:%M:%S')}")
            report.append("")

        if analysis:
            report.append("MEMORY ANALYSIS:")
            report.append(f"  Total memory blocks: {analysis.get('total_memory_blocks', 0)}")
            report.append("  Top consumers:")
            for i, consumer in enumerate(analysis.get('top_consumers', [])[:5], 1):
                report.append(f"    {i}. {consumer['size']/1024:.1f}KB ({consumer['count']} objects)")
            report.append("")

        if self.memory_peaks:
            report.append("MEMORY PEAKS:")
            for i, (timestamp, peak_mb) in enumerate(sorted(self.memory_peaks, key=lambda x: x[1], reverse=True)[:5], 1):
                report.append(f"  {i}. {timestamp.strftime('%H:%M:%S')}: {peak_mb:.1f}MB")
            report.append("")

        return "\n".join(report)

# Global optimizer instance
_optimizer_instance = None

def get_optimizer() -> MemoryOptimizer:
    """Get global memory optimizer instance"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = MemoryOptimizer()
    return _optimizer_instance

# Convenience functions

def monitor_memory_usage():
    """Start monitoring memory usage"""
    optimizer = get_optimizer()
    optimizer.start_monitoring()

def check_memory_health() -> bool:
    """Check if memory usage is within acceptable limits"""
    optimizer = get_optimizer()
    stats = optimizer.get_memory_stats()
    current_memory = stats.get('current_memory_mb', 0)
    threshold = stats.get('memory_threshold_mb', 500.0)

    return current_memory <= threshold

def optimize_memory():
    """Perform memory optimization"""
    optimizer = get_optimizer()
    optimizer.force_cleanup()
    optimizer._perform_garbage_collection()

def get_memory_report() -> str:
    """Get memory usage report"""
    optimizer = get_optimizer()
    return optimizer.get_memory_report()

def add_memory_alert_callback(callback: Callable):
    """Add callback for memory alerts"""
    optimizer = get_optimizer()
    optimizer.add_memory_callback(callback)

def add_leak_alert_callback(callback: Callable):
    """Add callback for memory leak alerts"""
    optimizer = get_optimizer()
    optimizer.add_leak_callback(callback)

def main():
    """Test the memory optimizer"""
    print("="*60)
    print("MEMORY OPTIMIZER TEST")
    print("="*60)

    optimizer = MemoryOptimizer(memory_threshold_mb=100.0, gc_threshold_mb=50.0)

    # Add test callbacks
    def memory_callback(memory_mb):
        print(".2f")

    def leak_callback(trend):
        print(".2f")

    optimizer.add_memory_callback(memory_callback)
    optimizer.add_leak_callback(leak_callback)

    # Start monitoring
    optimizer.start_monitoring()

    # Create some memory usage
    print("\nCreating memory usage...")
    test_data = []
    for i in range(10):
        test_data.append([j for j in range(10000)])  # Create lists
        time.sleep(0.1)

    # Take snapshot
    print("Taking memory snapshot...")
    optimizer.take_memory_snapshot()

    # Wait for monitoring
    print("Monitoring for 10 seconds...")
    time.sleep(10)

    # Generate report
    report = optimizer.get_memory_report()
    print("\n" + report)

    # Cleanup
    optimizer.force_cleanup()
    optimizer.stop_monitoring()

    print("\nTest completed!")

if __name__ == "__main__":
    main()

