"""
Performance monitoring module for FANWS application.
Tracks system performance, memory usage, and application metrics.
"""

import psutil
import time
import threading
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
from .database_manager import DatabaseManager

class PerformanceMonitor:
    """Monitor system and application performance."""

    def __init__(self, update_interval: int = 60):
        """Initialize performance monitor."""
        self.update_interval = update_interval
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_history = deque(maxlen=100)  # Keep last 100 measurements
        self.db_manager = DatabaseManager()
        self._lock = threading.RLock()

        # Performance thresholds
        self.memory_threshold = 80  # percentage
        self.cpu_threshold = 80  # percentage
        self.disk_threshold = 90  # percentage

        logging.info("PerformanceMonitor initialized")

    def start_monitoring(self):
        """Start performance monitoring."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logging.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logging.info("Performance monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                metrics = self.collect_metrics()
                self._store_metrics(metrics)
                self._check_thresholds(metrics)

                time.sleep(self.update_interval)

            except Exception as e:
                logging.error(f"Error in performance monitoring: {str(e)}")
                time.sleep(self.update_interval)

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics."""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Process metrics (current process)
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()

            # Network metrics
            network = psutil.net_io_counters()

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available': memory.available,
                    'memory_total': memory.total,
                    'memory_used': memory.used,
                    'disk_percent': (disk.used / disk.total) * 100,
                    'disk_free': disk.free,
                    'disk_total': disk.total,
                    'disk_used': disk.used
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }

            return metrics

        except Exception as e:
            logging.error(f"Error collecting metrics: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'system': {},
                'process': {},
                'network': {}
            }

    def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in memory and database."""
        with self._lock:
            self.metrics_history.append(metrics)

            # Store in database (sample every 10 measurements to avoid too much data)
            if len(self.metrics_history) % 10 == 0:
                try:
                    self.db_manager.store_performance_metrics(metrics)
                except Exception as e:
                    logging.error(f"Failed to store metrics in database: {str(e)}")

    def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check if metrics exceed thresholds and log warnings."""
        try:
            system_metrics = metrics.get('system', {})

            # Check CPU threshold
            cpu_percent = system_metrics.get('cpu_percent', 0)
            if cpu_percent > self.cpu_threshold:
                logging.warning(f"High CPU usage: {cpu_percent:.1f}%")

            # Check memory threshold
            memory_percent = system_metrics.get('memory_percent', 0)
            if memory_percent > self.memory_threshold:
                logging.warning(f"High memory usage: {memory_percent:.1f}%")

            # Check disk threshold
            disk_percent = system_metrics.get('disk_percent', 0)
            if disk_percent > self.disk_threshold:
                logging.warning(f"High disk usage: {disk_percent:.1f}%")

        except Exception as e:
            logging.error(f"Error checking thresholds: {str(e)}")

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.collect_metrics()

    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics history for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        with self._lock:
            filtered_metrics = []
            for metrics in self.metrics_history:
                try:
                    timestamp = datetime.fromisoformat(metrics['timestamp'])
                    if timestamp >= cutoff_time:
                        filtered_metrics.append(metrics)
                except Exception:
                    continue

            return filtered_metrics

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        try:
            current_metrics = self.get_current_metrics()
            recent_metrics = self.get_metrics_history(minutes=30)

            if not recent_metrics:
                return {
                    'current': current_metrics,
                    'averages': {},
                    'peaks': {},
                    'status': 'no_history'
                }

            # Calculate averages
            cpu_values = [m.get('system', {}).get('cpu_percent', 0) for m in recent_metrics]
            memory_values = [m.get('system', {}).get('memory_percent', 0) for m in recent_metrics]
            disk_values = [m.get('system', {}).get('disk_percent', 0) for m in recent_metrics]

            averages = {
                'cpu_percent': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'memory_percent': sum(memory_values) / len(memory_values) if memory_values else 0,
                'disk_percent': sum(disk_values) / len(disk_values) if disk_values else 0
            }

            # Calculate peaks
            peaks = {
                'cpu_percent': max(cpu_values) if cpu_values else 0,
                'memory_percent': max(memory_values) if memory_values else 0,
                'disk_percent': max(disk_values) if disk_values else 0
            }

            # Determine status
            status = 'good'
            if (averages['cpu_percent'] > self.cpu_threshold or
                averages['memory_percent'] > self.memory_threshold or
                averages['disk_percent'] > self.disk_threshold):
                status = 'warning'

            return {
                'current': current_metrics,
                'averages': averages,
                'peaks': peaks,
                'status': status,
                'history_count': len(recent_metrics)
            }

        except Exception as e:
            logging.error(f"Error getting performance summary: {str(e)}")
            return {
                'current': {},
                'averages': {},
                'peaks': {},
                'status': 'error',
                'error': str(e)
            }

    def get_resource_usage_trend(self, resource: str, hours: int = 24) -> Dict[str, Any]:
        """Get resource usage trend over time."""
        try:
            # Get metrics from database
            metrics = self.db_manager.get_performance_metrics(hours * 60)  # Convert to minutes

            if not metrics:
                return {
                    'resource': resource,
                    'trend': 'stable',
                    'data_points': 0,
                    'current_value': 0,
                    'min_value': 0,
                    'max_value': 0,
                    'average_value': 0
                }

            # Extract values for the specified resource
            values = []
            timestamps = []

            for metric in metrics:
                if resource in ['cpu_percent', 'memory_percent', 'disk_percent']:
                    value = metric.get('system', {}).get(resource, 0)
                elif resource.startswith('process_'):
                    key = resource.replace('process_', '')
                    value = metric.get('process', {}).get(key, 0)
                else:
                    continue

                values.append(value)
                timestamps.append(metric['timestamp'])

            if not values:
                return {
                    'resource': resource,
                    'trend': 'no_data',
                    'data_points': 0,
                    'current_value': 0,
                    'min_value': 0,
                    'max_value': 0,
                    'average_value': 0
                }

            # Calculate statistics
            current_value = values[-1] if values else 0
            min_value = min(values)
            max_value = max(values)
            average_value = sum(values) / len(values)

            # Determine trend
            if len(values) >= 2:
                recent_avg = sum(values[-min(5, len(values)):]) / min(5, len(values))
                older_avg = sum(values[:min(5, len(values))]) / min(5, len(values))

                if recent_avg > older_avg * 1.1:
                    trend = 'increasing'
                elif recent_avg < older_avg * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'

            return {
                'resource': resource,
                'trend': trend,
                'data_points': len(values),
                'current_value': current_value,
                'min_value': min_value,
                'max_value': max_value,
                'average_value': average_value,
                'timestamps': timestamps[-20:],  # Return last 20 timestamps
                'values': values[-20:]  # Return last 20 values
            }

        except Exception as e:
            logging.error(f"Error getting resource usage trend: {str(e)}")
            return {
                'resource': resource,
                'trend': 'error',
                'error': str(e)
            }

    def optimize_performance(self) -> Dict[str, Any]:
        """Suggest performance optimizations."""
        try:
            current_metrics = self.get_current_metrics()
            suggestions = []

            system_metrics = current_metrics.get('system', {})
            process_metrics = current_metrics.get('process', {})

            # Check memory usage
            memory_percent = system_metrics.get('memory_percent', 0)
            if memory_percent > 80:
                suggestions.append({
                    'type': 'memory',
                    'severity': 'high',
                    'message': f'High memory usage ({memory_percent:.1f}%). Consider closing unused applications.',
                    'action': 'Close unused applications or restart the system'
                })

            # Check CPU usage
            cpu_percent = system_metrics.get('cpu_percent', 0)
            if cpu_percent > 80:
                suggestions.append({
                    'type': 'cpu',
                    'severity': 'high',
                    'message': f'High CPU usage ({cpu_percent:.1f}%). System may be slow.',
                    'action': 'Check for background processes or reduce workload'
                })

            # Check disk usage
            disk_percent = system_metrics.get('disk_percent', 0)
            if disk_percent > 90:
                suggestions.append({
                    'type': 'disk',
                    'severity': 'critical',
                    'message': f'Very high disk usage ({disk_percent:.1f}%). Free up space.',
                    'action': 'Delete unnecessary files or move files to external storage'
                })

            # Check process metrics
            process_memory_percent = process_metrics.get('memory_percent', 0)
            if process_memory_percent > 10:  # If FANWS is using more than 10% of system memory
                suggestions.append({
                    'type': 'application',
                    'severity': 'medium',
                    'message': f'FANWS is using {process_memory_percent:.1f}% of system memory.',
                    'action': 'Consider saving work and restarting the application'
                })

            return {
                'suggestions': suggestions,
                'current_metrics': current_metrics,
                'optimization_needed': len(suggestions) > 0
            }

        except Exception as e:
            logging.error(f"Error optimizing performance: {str(e)}")
            return {
                'suggestions': [],
                'error': str(e),
                'optimization_needed': False
            }

    def set_thresholds(self, memory_threshold: int = None,
                      cpu_threshold: int = None, disk_threshold: int = None):
        """Set performance thresholds."""
        if memory_threshold is not None:
            self.memory_threshold = memory_threshold

        if cpu_threshold is not None:
            self.cpu_threshold = cpu_threshold

        if disk_threshold is not None:
            self.disk_threshold = disk_threshold

        logging.info(f"Performance thresholds updated: CPU={self.cpu_threshold}%, Memory={self.memory_threshold}%, Disk={self.disk_threshold}%")

    def log_event(self, event_type: str, event_data: Dict[str, Any] = None):
        """Log a performance-related event with current metrics."""
        try:
            current_metrics = self.collect_metrics()
            event_log = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'event_data': event_data or {},
                'metrics_at_event': current_metrics
            }

            logging.info(f"Performance event logged: {event_type}")
            logging.debug(f"Event details: {event_log}")

            # Store the event in metrics history with a special marker
            event_log['is_event'] = True
            self._store_metrics(event_log)

        except Exception as e:
            logging.error(f"Failed to log performance event '{event_type}': {str(e)}")

    def clear_history(self):
        """Clear metrics history."""
        with self._lock:
            self.metrics_history.clear()
        logging.info("Performance metrics history cleared")

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def start_performance_monitoring():
    """Start performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_monitoring()

def stop_performance_monitoring():
    """Stop performance monitoring."""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()

def get_current_performance() -> Dict[str, Any]:
    """Get current performance metrics."""
    monitor = get_performance_monitor()
    return monitor.get_current_metrics()

def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary."""
    monitor = get_performance_monitor()
    return monitor.get_performance_summary()
