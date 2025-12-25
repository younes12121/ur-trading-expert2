"""
Concurrent Processing Framework
Multi-threaded operations for data fetching, signal generation, and backtesting
"""

import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Dict, List, Callable, Any, Optional
from queue import Queue, PriorityQueue
import psutil
import os
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class TaskPriority(Enum):
    """Task priority levels"""
    HIGH = 1
    NORMAL = 2
    LOW = 3

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """Represents a concurrent task"""
    task_id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3

class ConcurrentProcessor:
    """Multi-threaded processing framework with resource management"""

    def __init__(self, max_workers: Optional[int] = None, max_memory_percent: float = 80.0,
                 max_cpu_percent: float = 80.0):
        self.max_workers = max_workers or min(32, os.cpu_count() * 2)
        self.max_memory_percent = max_memory_percent
        self.max_cpu_percent = max_cpu_percent

        # Thread pool management
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="ConcurrentProcessor")
        self.active_tasks: Dict[str, Future] = {}
        self.completed_tasks: Dict[str, Task] = {}

        # Resource monitoring
        self.process = psutil.Process()
        self.resource_lock = threading.Lock()

        # Task queues
        self.task_queue: PriorityQueue = PriorityQueue()
        self.task_lock = threading.Lock()

        # Monitoring
        self.monitoring_active = False
        self.monitor_thread = None

        # Statistics
        self.stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }

        self.logger = logging.getLogger('concurrent_processor')

    def submit_task(self, task_id: str, func: Callable, *args,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   max_retries: int = 3, **kwargs) -> str:
        """Submit a task for execution"""

        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries
        )

        with self.task_lock:
            self.task_queue.put((priority.value, task))
            self.stats['tasks_submitted'] += 1

        self.logger.info(f"Task {task_id} submitted with priority {priority.name}")
        return task_id

    def _execute_task(self, task: Task) -> Task:
        """Execute a single task with error handling and retries"""
        task.started_at = datetime.now()
        task.status = TaskStatus.RUNNING

        try:
            # Check resource limits before execution
            if not self._check_resource_limits():
                raise ResourceWarning("Resource limits exceeded")

            task.result = task.func(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()

            execution_time = (task.completed_at - task.started_at).total_seconds()
            with self.task_lock:
                self.stats['tasks_completed'] += 1
                self.stats['total_execution_time'] += execution_time

            self.logger.info(f"Task {task.task_id} completed successfully in {execution_time:.2f}s")

        except Exception as e:
            task.error = e
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()

            self.logger.error(f"Task {task.task_id} failed: {e}")

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self.logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count}/{task.max_retries})")

                # Put back in queue with higher priority for retries
                retry_priority = TaskPriority.HIGH if task.retry_count > 1 else task.priority
                with self.task_lock:
                    self.task_queue.put((retry_priority.value, task))
                return task
            else:
                with self.task_lock:
                    self.stats['tasks_failed'] += 1

        return task

    def _check_resource_limits(self) -> bool:
        """Check if system resources are within acceptable limits"""
        try:
            memory_percent = self.process.memory_percent()
            cpu_percent = self.process.cpu_percent(interval=0.1)

            if memory_percent > self.max_memory_percent:
                self.logger.warning(".1f")
                return False

            if cpu_percent > self.max_cpu_percent:
                self.logger.warning(".1f")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Resource check failed: {e}")
            return True  # Allow execution if monitoring fails

    def _process_queue(self):
        """Process tasks from the queue"""
        while True:
            try:
                # Get next task
                with self.task_lock:
                    if self.task_queue.empty():
                        break
                    _, task = self.task_queue.get_nowait()

                # Execute task
                result_task = self._execute_task(task)

                # Store result
                with self.task_lock:
                    self.completed_tasks[task.task_id] = result_task

                # Mark queue task as done
                self.task_queue.task_done()

            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
                break

    def _monitor_resources(self):
        """Background resource monitoring"""
        while self.monitoring_active:
            try:
                # Log resource usage periodically
                memory_percent = self.process.memory_percent()
                cpu_percent = self.process.cpu_percent(interval=1.0)

                self.logger.debug(".1f")

                # Check for resource warnings
                if memory_percent > self.max_memory_percent * 0.9:  # 90% of limit
                    self.logger.warning(".1f")
                if cpu_percent > self.max_cpu_percent * 0.9:
                    self.logger.warning(".1f")

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
                break

    def start_processing(self, enable_monitoring: bool = True):
        """Start the concurrent processing"""
        if enable_monitoring and not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_resources,
                daemon=True,
                name="ResourceMonitor"
            )
            self.monitor_thread.start()
            self.logger.info("Resource monitoring started")

        # Start queue processing
        processing_thread = threading.Thread(
            target=self._process_queue,
            daemon=True,
            name="QueueProcessor"
        )
        processing_thread.start()

        self.logger.info(f"Concurrent processor started with {self.max_workers} workers")

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for all tasks to complete"""
        start_time = time.time()

        while True:
            with self.task_lock:
                if self.task_queue.empty() and not self.active_tasks:
                    break

            if timeout and (time.time() - start_time) > timeout:
                self.logger.warning(f"Timeout waiting for completion after {timeout}s")
                return False

            time.sleep(0.1)

        # Update statistics
        with self.task_lock:
            if self.stats['tasks_completed'] > 0:
                self.stats['average_execution_time'] = (
                    self.stats['total_execution_time'] / self.stats['tasks_completed']
                )

        self.logger.info("All tasks completed")
        return True

    def get_task_result(self, task_id: str) -> Optional[Task]:
        """Get the result of a completed task"""
        with self.task_lock:
            return self.completed_tasks.get(task_id)

    def get_stats(self) -> Dict:
        """Get processing statistics"""
        with self.task_lock:
            return self.stats.copy()

    def get_active_tasks(self) -> List[str]:
        """Get list of currently active task IDs"""
        with self.task_lock:
            return list(self.active_tasks.keys())

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        # Note: This is a simplified implementation
        # In a real system, you'd need to handle running tasks differently
        with self.task_lock:
            # Find task in queue and remove it
            temp_queue = PriorityQueue()
            cancelled = False

            while not self.task_queue.empty():
                try:
                    priority, task = self.task_queue.get_nowait()
                    if task.task_id != task_id:
                        temp_queue.put((priority, task))
                    else:
                        task.status = TaskStatus.CANCELLED
                        self.completed_tasks[task_id] = task
                        cancelled = True
                    self.task_queue.task_done()
                except:
                    break

            # Restore queue
            while not temp_queue.empty():
                self.task_queue.put(temp_queue.get())
                temp_queue.task_done()

            return cancelled

    def shutdown(self, wait: bool = True):
        """Shutdown the processor"""
        self.logger.info("Shutting down concurrent processor...")

        # Stop monitoring
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        # Shutdown executor
        self.executor.shutdown(wait=wait)

        # Cancel remaining tasks
        cancelled_count = 0
        with self.task_lock:
            while not self.task_queue.empty():
                try:
                    _, task = self.task_queue.get_nowait()
                    task.status = TaskStatus.CANCELLED
                    self.completed_tasks[task.task_id] = task
                    cancelled_count += 1
                    self.task_queue.task_done()
                except:
                    break

        self.logger.info(f"Concurrent processor shutdown complete. {cancelled_count} tasks cancelled.")

# Global processor instance
_processor_instance = None

def get_processor() -> ConcurrentProcessor:
    """Get global processor instance"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = ConcurrentProcessor()
    return _processor_instance

# Convenience functions for common operations

def submit_data_fetch_task(symbol: str, timeframe: str, days: int) -> str:
    """Submit a data fetching task"""
    from data_fetcher import BinanceDataFetcher
    import config

    def fetch_data():
        fetcher = BinanceDataFetcher(performance_mode=config.PERFORMANCE_MODE)
        return fetcher.get_historical_data(symbol, timeframe, days)

    task_id = f"fetch_{symbol}_{timeframe}_{days}d"
    processor = get_processor()
    return processor.submit_task(task_id, fetch_data, priority=TaskPriority.HIGH)

def submit_signal_generation_task(symbol: str) -> str:
    """Submit a signal generation task"""
    def generate_signal():
        if symbol == "BTCUSDT":
            from elite_signal_generator import EliteAPlusSignalGenerator
            import config
            generator = EliteAPlusSignalGenerator(performance_mode=config.PERFORMANCE_MODE)
            return generator.generate_signal()
        # Add other symbols as needed
        return None

    task_id = f"signal_{symbol}"
    processor = get_processor()
    return processor.submit_task(task_id, generate_signal, priority=TaskPriority.NORMAL)

def submit_backtest_task(data, strategy_func, **backtest_params) -> str:
    """Submit a backtest task"""
    from backtest_engine import BacktestEngine

    def run_backtest():
        engine = BacktestEngine(**backtest_params)
        return engine.run_backtest(data, strategy_func, verbose=False, performance_mode=True)

    task_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    processor = get_processor()
    return processor.submit_task(task_id, run_backtest, priority=TaskPriority.NORMAL)

def main():
    """Test the concurrent processor"""
    print("="*60)
    print("CONCURRENT PROCESSOR TEST")
    print("="*60)

    # Create processor
    processor = ConcurrentProcessor(max_workers=4)

    # Submit test tasks
    print("\nSubmitting test tasks...")

    def test_task(task_id, duration):
        print(f"Starting task {task_id}")
        time.sleep(duration)
        print(f"Completed task {task_id}")
        return f"Result from {task_id}"

    # Submit multiple tasks
    task_ids = []
    for i in range(5):
        task_id = processor.submit_task(
            f"test_task_{i}",
            test_task,
            f"test_task_{i}",
            2.0,  # 2 second duration
            priority=TaskPriority.NORMAL if i % 2 == 0 else TaskPriority.HIGH
        )
        task_ids.append(task_id)

    # Start processing
    processor.start_processing()

    # Wait for completion
    print("\nWaiting for tasks to complete...")
    processor.wait_for_completion(timeout=30)

    # Show results
    print("\nResults:")
    stats = processor.get_stats()
    print(f"Tasks submitted: {stats['tasks_submitted']}")
    print(f"Tasks completed: {stats['tasks_completed']}")
    print(f"Tasks failed: {stats['tasks_failed']}")
    print(".2f")
    print(".2f")

    for task_id in task_ids:
        task = processor.get_task_result(task_id)
        if task:
            status = "✓" if task.status == TaskStatus.COMPLETED else "✗"
            print(f"  {status} {task_id}: {task.status.value}")

    processor.shutdown()
    print("\nTest completed!")

if __name__ == "__main__":
    main()

