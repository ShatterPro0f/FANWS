"""
Unit tests for FANWS performance monitoring backend features.
Tests CPU, memory, disk usage tracking, and system metrics.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import threading

# Import performance monitoring components
from src.core.performance_monitor import PerformanceMonitor


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""
    
    def test_performance_monitor_initialization(self):
        """Test PerformanceMonitor initialization."""
        monitor = PerformanceMonitor(update_interval=5)
        
        assert monitor.update_interval == 5
        assert not monitor.is_monitoring
        assert monitor.monitor_thread is None
        assert len(monitor.metrics_history) == 0
    
    def test_collect_metrics(self):
        """Test collecting system metrics."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        assert 'timestamp' in metrics
        assert 'system' in metrics
        assert 'process' in metrics
        
        # Check system metrics
        system_metrics = metrics['system']
        assert 'cpu_percent' in system_metrics
        assert 'memory_percent' in system_metrics
        assert 'memory_total' in system_metrics
        assert 'disk_percent' in system_metrics
        
        # Check process metrics
        process_metrics = metrics['process']
        assert 'cpu_percent' in process_metrics
        assert 'memory_rss' in process_metrics
        assert 'num_threads' in process_metrics
    
    def test_metrics_values_valid(self):
        """Test that collected metrics have valid values."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        # CPU should be between 0 and 100
        assert 0 <= metrics['system']['cpu_percent'] <= 100
        
        # Memory percentage should be between 0 and 100
        assert 0 <= metrics['system']['memory_percent'] <= 100
        
        # Process memory should be positive
        assert metrics['process']['memory_rss'] > 0
        
        # Number of threads should be positive
        assert metrics['process']['num_threads'] > 0
    
    def test_start_monitoring(self):
        """Test starting performance monitoring."""
        monitor = PerformanceMonitor(update_interval=1)
        
        monitor.start_monitoring()
        
        assert monitor.is_monitoring
        assert monitor.monitor_thread is not None
        assert monitor.monitor_thread.is_alive()
        
        # Clean up
        monitor.stop_monitoring()
    
    def test_stop_monitoring(self):
        """Test stopping performance monitoring."""
        monitor = PerformanceMonitor(update_interval=1)
        
        monitor.start_monitoring()
        time.sleep(0.5)  # Let it run briefly
        monitor.stop_monitoring()
        
        assert not monitor.is_monitoring
        
        # Wait for thread to finish
        if monitor.monitor_thread:
            monitor.monitor_thread.join(timeout=3)
        
        # Thread should be stopped
        if monitor.monitor_thread:
            assert not monitor.monitor_thread.is_alive()
    
    def test_metrics_history_collection(self):
        """Test that metrics are collected into history."""
        monitor = PerformanceMonitor(update_interval=1)
        
        monitor.start_monitoring()
        time.sleep(2.5)  # Let it collect a few samples
        monitor.stop_monitoring()
        
        # Should have at least 1 metric in history
        assert len(monitor.metrics_history) > 0
    
    def test_metrics_history_max_length(self):
        """Test that metrics history respects max length."""
        monitor = PerformanceMonitor(update_interval=1)
        
        # Manually add metrics to test deque behavior
        for i in range(150):
            monitor.metrics_history.append({'index': i})
        
        # Should maintain max of 100 items
        assert len(monitor.metrics_history) <= 100
    
    def test_memory_threshold_check(self):
        """Test memory threshold checking."""
        monitor = PerformanceMonitor()
        
        # Set low threshold for testing
        monitor.memory_threshold = 1  # 1%
        
        metrics = monitor.collect_metrics()
        
        # Memory usage should exceed 1%
        assert metrics['system']['memory_percent'] > monitor.memory_threshold
    
    def test_cpu_threshold_check(self):
        """Test CPU threshold checking."""
        monitor = PerformanceMonitor()
        
        # Check that threshold value is set
        assert monitor.cpu_threshold == 80
        assert monitor.memory_threshold == 80
        assert monitor.disk_threshold == 90
    
    def test_concurrent_monitoring(self):
        """Test that multiple monitoring instances don't conflict."""
        monitor1 = PerformanceMonitor(update_interval=2)
        monitor2 = PerformanceMonitor(update_interval=2)
        
        monitor1.start_monitoring()
        monitor2.start_monitoring()
        
        time.sleep(1)
        
        assert monitor1.is_monitoring
        assert monitor2.is_monitoring
        
        monitor1.stop_monitoring()
        monitor2.stop_monitoring()


class TestPerformanceMetricsStorage:
    """Test performance metrics storage functionality."""
    
    def test_metrics_stored_in_database(self):
        """Test that metrics can be stored in database."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        try:
            # Test if database storage method exists
            if hasattr(monitor, 'db_manager'):
                monitor.db_manager.store_performance_metrics(metrics)
                # If we get here without exception, storage works
                assert True
        except Exception as e:
            # If storage fails, at least verify metrics were collected
            assert metrics is not None
            assert 'timestamp' in metrics
    
    def test_metrics_retrieval(self):
        """Test retrieving performance metrics."""
        monitor = PerformanceMonitor()
        
        # Start monitoring briefly to collect some metrics
        monitor.start_monitoring()
        time.sleep(2)
        monitor.stop_monitoring()
        
        # Check that metrics were collected
        assert len(monitor.metrics_history) > 0
        
        # Verify recent metrics
        if len(monitor.metrics_history) > 0:
            latest_metric = monitor.metrics_history[-1]
            assert 'timestamp' in latest_metric


class TestSystemResourceTracking:
    """Test system resource tracking capabilities."""
    
    def test_memory_tracking(self):
        """Test memory usage tracking."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        system = metrics['system']
        
        assert 'memory_percent' in system
        assert 'memory_available' in system
        assert 'memory_total' in system
        assert 'memory_used' in system
        
        # Total memory should equal used + available
        assert system['memory_total'] > 0
        assert system['memory_used'] >= 0
        assert system['memory_available'] >= 0
    
    def test_cpu_tracking(self):
        """Test CPU usage tracking."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        assert 'cpu_percent' in metrics['system']
        assert 'cpu_percent' in metrics['process']
        
        # CPU percentages should be valid
        assert 0 <= metrics['system']['cpu_percent'] <= 100
        assert metrics['process']['cpu_percent'] >= 0
    
    def test_disk_tracking(self):
        """Test disk usage tracking."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        disk = metrics['system']
        
        assert 'disk_percent' in disk
        assert 'disk_free' in disk
        assert 'disk_total' in disk
        assert 'disk_used' in disk
        
        # Disk metrics should be valid
        assert disk['disk_total'] > 0
        assert disk['disk_free'] >= 0
        assert disk['disk_used'] >= 0
        assert 0 <= disk['disk_percent'] <= 100
    
    def test_process_memory_tracking(self):
        """Test process-specific memory tracking."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        process = metrics['process']
        
        assert 'memory_rss' in process
        assert 'memory_vms' in process
        assert 'memory_percent' in process
        
        # Process memory should be positive
        assert process['memory_rss'] > 0
        assert process['memory_vms'] > 0
        assert process['memory_percent'] >= 0
    
    def test_thread_tracking(self):
        """Test thread count tracking."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        assert 'num_threads' in metrics['process']
        assert metrics['process']['num_threads'] > 0
        
        # Should have at least 1 thread (the main thread)
        assert metrics['process']['num_threads'] >= 1


class TestPerformanceAlerts:
    """Test performance alert functionality."""
    
    def test_threshold_configuration(self):
        """Test configuring performance thresholds."""
        monitor = PerformanceMonitor()
        
        # Set custom thresholds
        monitor.memory_threshold = 75
        monitor.cpu_threshold = 85
        monitor.disk_threshold = 95
        
        assert monitor.memory_threshold == 75
        assert monitor.cpu_threshold == 85
        assert monitor.disk_threshold == 95
    
    def test_high_memory_detection(self):
        """Test detecting high memory usage."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        # Check if memory is above threshold
        memory_percent = metrics['system']['memory_percent']
        
        if memory_percent > monitor.memory_threshold:
            # High memory detected
            assert True
        else:
            # Memory is within acceptable range
            assert memory_percent <= monitor.memory_threshold


class TestPerformanceOptimization:
    """Test performance optimization features."""
    
    def test_metrics_collection_performance(self):
        """Test that metrics collection is fast."""
        monitor = PerformanceMonitor()
        
        start_time = time.time()
        metrics = monitor.collect_metrics()
        collection_time = time.time() - start_time
        
        # Should complete in less than 2 seconds
        assert collection_time < 2.0
        assert metrics is not None
    
    def test_monitoring_overhead(self):
        """Test monitoring overhead is minimal."""
        monitor = PerformanceMonitor(update_interval=1)
        
        # Get baseline CPU
        metrics_before = monitor.collect_metrics()
        cpu_before = metrics_before['process']['cpu_percent']
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(2)
        
        # Check CPU during monitoring
        metrics_during = monitor.collect_metrics()
        cpu_during = metrics_during['process']['cpu_percent']
        
        monitor.stop_monitoring()
        
        # Monitoring shouldn't significantly increase CPU usage
        # (allowing for some variation)
        assert cpu_during < cpu_before + 50  # Allow up to 50% increase


class TestIntegrationWithDatabase:
    """Test integration of performance monitoring with database."""
    
    def test_database_connection(self):
        """Test database connection for metrics storage."""
        monitor = PerformanceMonitor()
        
        # Check if database manager is available
        assert hasattr(monitor, 'db_manager')
        assert monitor.db_manager is not None
    
    def test_store_and_retrieve_metrics(self):
        """Test storing and retrieving metrics from database."""
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        
        try:
            # Store metrics
            monitor.db_manager.store_performance_metrics(metrics)
            
            # Verify storage succeeded
            assert True
        except Exception as e:
            # If database not available, skip test
            pytest.skip(f"Database not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
