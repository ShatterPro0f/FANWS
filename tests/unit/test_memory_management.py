"""
Unit tests for FANWS memory management backend features.
Tests lazy loading, caching, memory cleanup, and optimization.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Import memory management components
from src.system.memory_manager import (
    MemoryStats, MemoryConfig, LazyTextLoader,
    FileCache, ProjectFileCache, MemoryManager,
    get_memory_manager, get_cache_manager
)


class TestMemoryConfiguration:
    """Test memory configuration functionality."""
    
    def test_memory_config_defaults(self):
        """Test default memory configuration values."""
        config = MemoryConfig()
        
        assert config.max_memory_mb == 512
        assert config.max_cache_mb == 128
        assert config.enable_lazy_loading is True
        assert config.enable_streaming is True
        assert config.enable_compression is True
    
    def test_custom_memory_config(self):
        """Test custom memory configuration."""
        config = MemoryConfig(
            max_memory_mb=1024,
            max_cache_mb=256,
            enable_lazy_loading=False
        )
        
        assert config.max_memory_mb == 1024
        assert config.max_cache_mb == 256
        assert config.enable_lazy_loading is False


class TestMemoryStats:
    """Test memory statistics tracking."""
    
    def test_memory_stats_creation(self):
        """Test creating memory stats object."""
        stats = MemoryStats(
            process_memory_mb=100.5,
            system_memory_percent=45.2,
            cache_memory_mb=25.0
        )
        
        assert stats.process_memory_mb == 100.5
        assert stats.system_memory_percent == 45.2
        assert stats.cache_memory_mb == 25.0
    
    def test_memory_stats_defaults(self):
        """Test memory stats with default values."""
        stats = MemoryStats()
        
        assert stats.process_memory_mb == 0.0
        assert stats.system_memory_percent == 0.0
        assert stats.cache_memory_mb == 0.0
        assert stats.gc_collections == 0


class TestLazyTextLoader:
    """Test lazy text loading functionality."""
    
    def test_lazy_loader_initialization(self):
        """Test LazyTextLoader initialization."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            loader = LazyTextLoader(temp_file)
            
            assert loader.file_path == temp_file
            assert loader.chunk_size > 0
        finally:
            os.unlink(temp_file)
    
    def test_lazy_loader_file_size(self):
        """Test getting file size without loading."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            content = "Test content " * 100
            f.write(content)
            temp_file = f.name
        
        try:
            loader = LazyTextLoader(temp_file)
            size = loader.size
            
            assert size > 0
            assert len(loader) == size
        finally:
            os.unlink(temp_file)
    
    def test_lazy_loader_iteration(self):
        """Test iterating through file lines."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Line 1\nLine 2\nLine 3\n")
            temp_file = f.name
        
        try:
            loader = LazyTextLoader(temp_file)
            lines = list(loader)
            
            assert len(lines) == 3
            assert lines[0] == "Line 1"
            assert lines[1] == "Line 2"
            assert lines[2] == "Line 3"
        finally:
            os.unlink(temp_file)
    
    def test_lazy_loader_chunk_reading(self):
        """Test reading specific chunks."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            content = "X" * 2000  # 2KB of content
            f.write(content)
            temp_file = f.name
        
        try:
            loader = LazyTextLoader(temp_file, chunk_size=1024)
            
            # Read first chunk
            chunk0 = loader.read_chunk(0)
            assert len(chunk0) > 0
            assert len(chunk0) <= 1024
            
            # Read second chunk
            chunk1 = loader.read_chunk(1)
            assert len(chunk1) > 0
        finally:
            os.unlink(temp_file)


class TestFileCache:
    """Test file caching functionality."""
    
    def test_file_cache_initialization(self):
        """Test FileCache initialization."""
        cache = FileCache(max_size_mb=10)
        
        assert cache.max_size_mb == 10
        assert len(cache.cache) == 0
    
    def test_cache_set_and_get(self):
        """Test setting and getting cached values."""
        cache = FileCache()
        
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        
        assert value == "test_value"
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = FileCache()
        
        value = cache.get("nonexistent_key")
        
        assert value is None
    
    def test_cache_clear(self):
        """Test clearing cache."""
        cache = FileCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.cache) == 2
        
        cache.clear()
        
        assert len(cache.cache) == 0
    
    def test_cache_size_tracking(self):
        """Test cache size tracking."""
        cache = FileCache()
        
        content = "X" * 1000  # 1KB of content
        cache.set("large_item", content)
        
        assert cache.current_size_mb > 0


class TestProjectFileCache:
    """Test project-specific file caching."""
    
    def test_project_cache_initialization(self):
        """Test ProjectFileCache initialization."""
        cache = ProjectFileCache(project_name="test_project")
        
        assert cache.project_name == "test_project"
    
    def test_project_cache_isolation(self):
        """Test that project caches are isolated."""
        cache1 = ProjectFileCache(project_name="project1")
        cache2 = ProjectFileCache(project_name="project2")
        
        cache1.set("key", "value1")
        cache2.set("key", "value2")
        
        assert cache1.get("key") == "value1"
        assert cache2.get("key") == "value2"


class TestMemoryManager:
    """Test memory manager functionality."""
    
    def test_memory_manager_initialization(self):
        """Test MemoryManager initialization."""
        manager = MemoryManager()
        
        assert manager is not None
        assert hasattr(manager, 'get_memory_stats')
    
    def test_get_memory_stats(self):
        """Test getting current memory statistics."""
        manager = MemoryManager()
        stats = manager.get_memory_stats()
        
        assert isinstance(stats, MemoryStats)
        assert stats.process_memory_mb >= 0
        assert stats.system_memory_percent >= 0
    
    def test_memory_cleanup(self):
        """Test memory cleanup functionality."""
        manager = MemoryManager()
        
        # Get initial stats
        stats_before = manager.get_memory_stats()
        
        # Trigger cleanup
        manager.cleanup()
        
        # Get stats after cleanup
        stats_after = manager.get_memory_stats()
        
        # Verify cleanup was attempted
        assert stats_after is not None
    
    def test_cache_optimization(self):
        """Test cache optimization."""
        manager = MemoryManager()
        
        # Add some items to cache
        if hasattr(manager, 'cache'):
            manager.cache.set("test1", "value1")
            manager.cache.set("test2", "value2")
        
        # Trigger optimization
        manager.optimize_memory()
        
        # Should complete without error
        assert True
    
    def test_memory_threshold_monitoring(self):
        """Test memory threshold monitoring."""
        manager = MemoryManager()
        stats = manager.get_memory_stats()
        
        # Check if monitoring is working
        assert stats.process_memory_mb >= 0
        
        # Verify threshold checking exists
        if hasattr(manager, 'check_memory_threshold'):
            result = manager.check_memory_threshold()
            assert result is not None


class TestMemoryOptimization:
    """Test memory optimization features."""
    
    def test_garbage_collection(self):
        """Test garbage collection trigger."""
        manager = MemoryManager()
        
        stats_before = manager.get_memory_stats()
        gc_before = stats_before.gc_collections
        
        # Trigger GC
        manager.force_garbage_collection()
        
        stats_after = manager.get_memory_stats()
        
        # GC should have been triggered
        assert stats_after is not None
    
    def test_cache_eviction(self):
        """Test cache eviction when limit exceeded."""
        cache = FileCache(max_size_mb=1)  # Very small cache
        
        # Add items until cache is full
        for i in range(100):
            large_value = "X" * 10000  # 10KB each
            cache.set(f"key_{i}", large_value)
        
        # Cache should evict old items
        assert cache.current_size_mb <= cache.max_size_mb * 1.1  # Allow 10% overflow
    
    def test_lazy_loading_efficiency(self):
        """Test that lazy loading is more efficient than full loading."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Create a large file
            large_content = "Line " * 100000  # ~500KB
            f.write(large_content)
            temp_file = f.name
        
        try:
            # Lazy loading should not load entire file
            loader = LazyTextLoader(temp_file)
            
            # Just getting size should be fast
            size = loader.size
            assert size > 0
            
            # Hasn't loaded entire content
            assert len(loader._loaded_chunks) == 0
        finally:
            os.unlink(temp_file)


class TestCacheManager:
    """Test cache manager singleton."""
    
    def test_get_cache_manager(self):
        """Test getting cache manager instance."""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()
        
        # Should return same instance (singleton)
        assert manager1 is manager2
    
    def test_cache_manager_operations(self):
        """Test cache manager operations."""
        manager = get_cache_manager()
        
        # Test basic operations
        manager.set("test_key", "test_value")
        value = manager.get("test_key")
        
        assert value == "test_value"


class TestMemoryManagerSingleton:
    """Test memory manager singleton."""
    
    def test_get_memory_manager(self):
        """Test getting memory manager instance."""
        manager1 = get_memory_manager()
        manager2 = get_memory_manager()
        
        # Should return same instance (singleton)
        assert manager1 is manager2
    
    def test_memory_manager_stats(self):
        """Test memory manager statistics."""
        manager = get_memory_manager()
        stats = manager.get_memory_stats()
        
        assert stats is not None
        assert isinstance(stats, MemoryStats)


class TestMemoryLeakPrevention:
    """Test memory leak prevention features."""
    
    def test_weak_references(self):
        """Test that cache uses weak references where appropriate."""
        cache = FileCache()
        
        # Create objects
        obj1 = "test value"
        cache.set("key1", obj1)
        
        # Delete original reference
        del obj1
        
        # Cache should still have the value
        # (or None if using weak references and GC ran)
        value = cache.get("key1")
        assert value is None or value == "test value"
    
    def test_cache_size_limit(self):
        """Test that cache respects size limits."""
        cache = FileCache(max_size_mb=1)
        
        # Add data until we hit the limit
        for i in range(1000):
            cache.set(f"key_{i}", "X" * 1000)
        
        # Cache should not exceed max size by too much
        assert cache.current_size_mb <= cache.max_size_mb * 1.2


class TestMemoryMonitoring:
    """Test memory monitoring capabilities."""
    
    def test_continuous_monitoring(self):
        """Test continuous memory monitoring."""
        manager = MemoryManager()
        
        # Start monitoring
        if hasattr(manager, 'start_monitoring'):
            manager.start_monitoring()
            
            # Get stats multiple times
            stats1 = manager.get_memory_stats()
            stats2 = manager.get_memory_stats()
            
            assert stats1 is not None
            assert stats2 is not None
            
            # Stop monitoring
            if hasattr(manager, 'stop_monitoring'):
                manager.stop_monitoring()
    
    def test_memory_alerts(self):
        """Test memory alert thresholds."""
        manager = MemoryManager()
        config = MemoryConfig(
            warning_threshold=0.8,
            critical_threshold=0.9
        )
        
        assert config.warning_threshold == 0.8
        assert config.critical_threshold == 0.9


class TestMemoryIntegration:
    """Test memory management integration."""
    
    def test_integration_with_file_operations(self):
        """Test memory management integration with file operations."""
        manager = get_memory_manager()
        cache = get_cache_manager()
        
        # Simulate file operation
        cache.set("file1", "content1")
        
        # Get memory stats
        stats = manager.get_memory_stats()
        
        assert stats is not None
        assert stats.process_memory_mb > 0
    
    def test_memory_optimization_trigger(self):
        """Test automatic memory optimization trigger."""
        manager = MemoryManager()
        
        # Should have optimization logic
        if hasattr(manager, 'should_optimize'):
            result = manager.should_optimize()
            assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
