"""
Memory Management System for FANWS - Priority 4.3
Provides comprehensive memory management with lazy loading, monitoring, and optimization.
"""

import os
import sys
import gc
import threading
import psutil
import logging
import weakref
from typing import Dict, List, Optional, Any, Generator, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict
from pathlib import Path
import json
from io import StringIO

# Memory configuration constants
DEFAULT_MEMORY_LIMIT_MB = 512
DEFAULT_CACHE_LIMIT_MB = 128
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB chunks
DEFAULT_CLEANUP_INTERVAL = 300  # 5 minutes
MEMORY_WARNING_THRESHOLD = 0.8  # 80% of limit
MEMORY_CRITICAL_THRESHOLD = 0.9  # 90% of limit

@dataclass
class MemoryStats:
    """Memory usage statistics."""
    process_memory_mb: float = 0.0
    system_memory_percent: float = 0.0
    cache_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    gc_collections: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MemoryConfig:
    """Memory management configuration."""
    max_memory_mb: int = DEFAULT_MEMORY_LIMIT_MB
    max_cache_mb: int = DEFAULT_CACHE_LIMIT_MB
    chunk_size: int = DEFAULT_CHUNK_SIZE
    cleanup_interval: int = DEFAULT_CLEANUP_INTERVAL
    enable_lazy_loading: bool = True
    enable_streaming: bool = True
    enable_compression: bool = True
    warning_threshold: float = MEMORY_WARNING_THRESHOLD
    critical_threshold: float = MEMORY_CRITICAL_THRESHOLD

class LazyTextLoader:
    """Lazy loading for large text files."""

    def __init__(self, file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self._size = None
        self._encoding = 'utf-8'
        self._loaded_chunks = {}
        self._lock = threading.Lock()

    @property
    def size(self) -> int:
        """Get file size without loading the entire file."""
        if self._size is None:
            self._size = os.path.getsize(self.file_path)
        return self._size

    def __len__(self) -> int:
        """Return file size in bytes."""
        return self.size

    def __iter__(self) -> Generator[str, None, None]:
        """Iterate through file line by line."""
        with open(self.file_path, 'r', encoding=self._encoding) as f:
            for line in f:
                yield line.rstrip('\n\r')

    def read_chunk(self, chunk_index: int) -> str:
        """Read a specific chunk of the file."""
        with self._lock:
            if chunk_index in self._loaded_chunks:
                return self._loaded_chunks[chunk_index]

            offset = chunk_index * self.chunk_size
            with open(self.file_path, 'r', encoding=self._encoding) as f:
                f.seek(offset)
                chunk = f.read(self.chunk_size)

                # Cache the chunk with weak reference cleanup
                self._loaded_chunks[chunk_index] = chunk

                # Limit cache size
                if len(self._loaded_chunks) > 10:
                    # Remove oldest chunks
                    oldest_key = min(self._loaded_chunks.keys())
                    del self._loaded_chunks[oldest_key]

                return chunk

    def read_all(self) -> str:
        """Read entire file content - use with caution for large files."""
        with open(self.file_path, 'r', encoding=self._encoding) as f:
            return f.read()

    def search(self, pattern: str, case_sensitive: bool = False) -> List[tuple]:
        """Search for pattern in file without loading entire content."""
        results = []
        line_num = 0

        for line in self:
            line_num += 1
            search_line = line if case_sensitive else line.lower()
            search_pattern = pattern if case_sensitive else pattern.lower()

            if search_pattern in search_line:
                results.append((line_num, line))

        return results

class StreamingTextProcessor:
    """Streaming text processor for large files."""

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        self.chunk_size = chunk_size

    def process_file(self, file_path: str, processor: Callable[[str], str]) -> Generator[str, None, None]:
        """Process file in chunks using a processor function."""
        with open(file_path, 'r', encoding='utf-8') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break

                processed_chunk = processor(chunk)
                yield processed_chunk

    def transform_file(self, input_path: str, output_path: str,
                      processor: Callable[[str], str]) -> bool:
        """Transform file content using streaming processing."""
        try:
            with open(output_path, 'w', encoding='utf-8') as out_f:
                for processed_chunk in self.process_file(input_path, processor):
                    out_f.write(processed_chunk)
            return True
        except Exception as e:
            logging.error(f"Failed to transform file {input_path}: {e}")
            return False

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze file content without loading entire file into memory."""
        stats = {
            'size_bytes': 0,
            'line_count': 0,
            'word_count': 0,
            'char_count': 0,
            'avg_line_length': 0
        }

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stats['line_count'] += 1
                stats['char_count'] += len(line)
                stats['word_count'] += len(line.split())

        stats['size_bytes'] = os.path.getsize(file_path)
        stats['avg_line_length'] = stats['char_count'] / max(stats['line_count'], 1)

        return stats

class MemoryMonitor:
    """Real-time memory monitoring and alerts."""

    def __init__(self, config: MemoryConfig):
        self.config = config
        self.stats_history = []
        self.peak_memory = 0.0
        self.warning_callbacks = []
        self.critical_callbacks = []
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.Lock()

        # Get process reference
        self.process = psutil.Process()

    def start_monitoring(self):
        """Start memory monitoring in background thread."""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            logging.info("Memory monitoring started")

    def stop_monitoring(self):
        """Stop memory monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
        logging.info("Memory monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                stats = self.get_current_stats()

                with self._lock:
                    self.stats_history.append(stats)

                    # Keep only last 100 readings
                    if len(self.stats_history) > 100:
                        self.stats_history.pop(0)

                    # Update peak memory
                    self.peak_memory = max(self.peak_memory, stats.process_memory_mb)

                # Check thresholds
                memory_ratio = stats.process_memory_mb / self.config.max_memory_mb

                if memory_ratio >= self.config.critical_threshold:
                    self._trigger_critical_alerts(stats)
                elif memory_ratio >= self.config.warning_threshold:
                    self._trigger_warning_alerts(stats)

                threading.Event().wait(5)  # Check every 5 seconds

            except Exception as e:
                logging.error(f"Memory monitoring error: {e}")
                threading.Event().wait(10)  # Wait longer on error

    def get_current_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        try:
            # Process memory
            memory_info = self.process.memory_info()
            process_memory_mb = memory_info.rss / (1024 * 1024)

            # System memory
            system_memory = psutil.virtual_memory()
            system_memory_percent = system_memory.percent

            # Garbage collection stats
            gc_stats = gc.get_stats()
            gc_collections = sum(stat.get('collections', 0) for stat in gc_stats)

            return MemoryStats(
                process_memory_mb=process_memory_mb,
                system_memory_percent=system_memory_percent,
                cache_memory_mb=0.0,  # Will be updated by cache manager
                peak_memory_mb=self.peak_memory,
                gc_collections=gc_collections,
                timestamp=datetime.now()
            )
        except Exception as e:
            logging.error(f"Failed to get memory stats: {e}")
            return MemoryStats()

    def _trigger_warning_alerts(self, stats: MemoryStats):
        """Trigger memory warning alerts."""
        for callback in self.warning_callbacks:
            try:
                callback(stats)
            except Exception as e:
                logging.error(f"Warning callback error: {e}")

    def _trigger_critical_alerts(self, stats: MemoryStats):
        """Trigger critical memory alerts."""
        for callback in self.critical_callbacks:
            try:
                callback(stats)
            except Exception as e:
                logging.error(f"Critical callback error: {e}")

    def add_warning_callback(self, callback: Callable[[MemoryStats], None]):
        """Add callback for memory warnings."""
        self.warning_callbacks.append(callback)

    def add_critical_callback(self, callback: Callable[[MemoryStats], None]):
        """Add callback for critical memory alerts."""
        self.critical_callbacks.append(callback)

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory usage summary."""
        current_stats = self.get_current_stats()

        with self._lock:
            avg_memory = 0.0
            if self.stats_history:
                avg_memory = sum(s.process_memory_mb for s in self.stats_history) / len(self.stats_history)

        return {
            'current_mb': current_stats.process_memory_mb,
            'peak_mb': self.peak_memory,
            'average_mb': avg_memory,
            'system_percent': current_stats.system_memory_percent,
            'limit_mb': self.config.max_memory_mb,
            'usage_percent': (current_stats.process_memory_mb / self.config.max_memory_mb) * 100,
            'gc_collections': current_stats.gc_collections
        }

class SmartCache:
    """Memory-aware cache with automatic cleanup."""

    def __init__(self, config: MemoryConfig, monitor: MemoryMonitor):
        self.config = config
        self.monitor = monitor
        self.cache = OrderedDict()
        self.cache_sizes = {}
        self.cache_access_times = {}
        self._lock = threading.RLock()
        self._total_size = 0

        # Register cleanup callbacks
        monitor.add_warning_callback(self._warning_cleanup)
        monitor.add_critical_callback(self._critical_cleanup)

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key in self.cache:
                # Update access time
                self.cache_access_times[key] = datetime.now()

                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value

                return value
            return None

    def put(self, key: str, value: Any, estimated_size: int = None):
        """Put item in cache with size estimation."""
        with self._lock:
            # Estimate size if not provided
            if estimated_size is None:
                estimated_size = self._estimate_size(value)

            # Check if we have space
            if self._total_size + estimated_size > self.config.max_cache_mb * 1024 * 1024:
                self._cleanup_for_space(estimated_size)

            # Remove existing entry if present
            if key in self.cache:
                old_size = self.cache_sizes.get(key, 0)
                self._total_size -= old_size
                del self.cache[key]

            # Add new entry
            self.cache[key] = value
            self.cache_sizes[key] = estimated_size
            self.cache_access_times[key] = datetime.now()
            self._total_size += estimated_size

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value."""
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, (list, tuple)):
            return sum(self._estimate_size(item) for item in value)
        elif isinstance(value, dict):
            return sum(self._estimate_size(k) + self._estimate_size(v) for k, v in value.items())
        else:
            return sys.getsizeof(value)

    def _cleanup_for_space(self, needed_size: int):
        """Clean up cache to make space."""
        # Remove least recently used items
        while (self._total_size + needed_size > self.config.max_cache_mb * 1024 * 1024
               and self.cache):
            oldest_key = next(iter(self.cache))
            self._remove_item(oldest_key)

    def _remove_item(self, key: str):
        """Remove item from cache."""
        if key in self.cache:
            size = self.cache_sizes.get(key, 0)
            self._total_size -= size
            del self.cache[key]
            del self.cache_sizes[key]
            del self.cache_access_times[key]

    def _warning_cleanup(self, stats: MemoryStats):
        """Perform cleanup when memory warning is triggered."""
        # Remove 25% of cache
        items_to_remove = max(1, len(self.cache) // 4)

        with self._lock:
            for _ in range(items_to_remove):
                if self.cache:
                    oldest_key = next(iter(self.cache))
                    self._remove_item(oldest_key)

        logging.warning(f"Memory warning cleanup: removed {items_to_remove} cache items")

    def _critical_cleanup(self, stats: MemoryStats):
        """Perform aggressive cleanup when memory is critical."""
        # Remove 50% of cache
        items_to_remove = max(1, len(self.cache) // 2)

        with self._lock:
            for _ in range(items_to_remove):
                if self.cache:
                    oldest_key = next(iter(self.cache))
                    self._remove_item(oldest_key)

        # Force garbage collection
        gc.collect()

        logging.critical(f"Critical memory cleanup: removed {items_to_remove} cache items")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'total_items': len(self.cache),
                'total_size_mb': self._total_size / (1024 * 1024),
                'max_size_mb': self.config.max_cache_mb,
                'usage_percent': (self._total_size / (self.config.max_cache_mb * 1024 * 1024)) * 100,
                'average_item_size': self._total_size / max(len(self.cache), 1)
            }

    def clear(self):
        """Clear all cache items."""
        with self._lock:
            self.cache.clear()
            self.cache_sizes.clear()
            self.cache_access_times.clear()
            self._total_size = 0

class MemoryOptimizer:
    """Memory optimization utilities."""

    def __init__(self, config: MemoryConfig):
        self.config = config

    def optimize_text_storage(self, text: str) -> str:
        """Optimize text storage by removing redundant whitespace."""
        if not self.config.enable_compression:
            return text

        # Remove excessive whitespace
        lines = text.split('\n')
        optimized_lines = []

        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()

            # Replace multiple spaces with single space
            while '  ' in line:
                line = line.replace('  ', ' ')

            optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def compress_json_data(self, data: Dict[str, Any]) -> str:
        """Compress JSON data for storage."""
        if not self.config.enable_compression:
            return json.dumps(data, indent=2)

        # Use compact JSON format
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

    def optimize_memory_usage(self):
        """Perform general memory optimization."""
        # Force garbage collection
        collected = gc.collect()

        # Optimize string intern pool
        sys.intern('') # Clear intern pool

        logging.info(f"Memory optimization: collected {collected} objects")

        return collected

class MemoryManager:
    """Main memory management system."""

    def __init__(self, config: MemoryConfig = None):
        self.config = config or MemoryConfig()
        self.monitor = MemoryMonitor(self.config)
        self.cache = SmartCache(self.config, self.monitor)
        self.optimizer = MemoryOptimizer(self.config)
        self.lazy_loaders = weakref.WeakValueDictionary()
        self.stream_processor = StreamingTextProcessor(self.config.chunk_size)

        # Auto-cleanup timer
        self._cleanup_timer = None
        self._start_cleanup_timer()

        logging.info("Memory manager initialized")

    def create_lazy_loader(self, file_path: str) -> LazyTextLoader:
        """Create a lazy loader for a file."""
        if file_path not in self.lazy_loaders:
            loader = LazyTextLoader(file_path, self.config.chunk_size)
            self.lazy_loaders[file_path] = loader
        return self.lazy_loaders[file_path]

    def should_use_lazy_loading(self, file_path: str) -> bool:
        """Determine if lazy loading should be used for a file."""
        if not self.config.enable_lazy_loading:
            return False

        try:
            file_size = os.path.getsize(file_path)
            # Use lazy loading for files larger than 1MB
            return file_size > 1024 * 1024
        except:
            return False

    def should_use_streaming(self, file_path: str) -> bool:
        """Determine if streaming should be used for a file."""
        if not self.config.enable_streaming:
            return False

        try:
            file_size = os.path.getsize(file_path)
            # Use streaming for files larger than 5MB
            return file_size > 5 * 1024 * 1024
        except:
            return False

    def read_file_smart(self, file_path: str) -> Union[str, LazyTextLoader]:
        """Smart file reading with automatic method selection."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.should_use_lazy_loading(file_path):
            return self.create_lazy_loader(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

    def _start_cleanup_timer(self):
        """Start automatic cleanup timer."""
        def cleanup():
            self.optimizer.optimize_memory_usage()
            self._start_cleanup_timer()  # Restart timer

        self._cleanup_timer = threading.Timer(self.config.cleanup_interval, cleanup)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def start(self):
        """Start memory management system."""
        self.monitor.start_monitoring()
        logging.info("Memory management system started")

    def stop(self):
        """Stop memory management system."""
        self.monitor.stop_monitoring()
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        logging.info("Memory management system stopped")

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            'memory': self.monitor.get_memory_summary(),
            'cache': self.cache.get_cache_stats(),
            'lazy_loaders': len(self.lazy_loaders),
            'config': {
                'max_memory_mb': self.config.max_memory_mb,
                'max_cache_mb': self.config.max_cache_mb,
                'chunk_size': self.config.chunk_size,
                'lazy_loading': self.config.enable_lazy_loading,
                'streaming': self.config.enable_streaming,
                'compression': self.config.enable_compression
            }
        }

# Global memory manager instance
_memory_manager = None
_memory_manager_lock = threading.Lock()

def get_memory_manager(config: MemoryConfig = None) -> MemoryManager:
    """Get global memory manager instance."""
    global _memory_manager

    if _memory_manager is None:
        with _memory_manager_lock:
            if _memory_manager is None:
                _memory_manager = MemoryManager(config)

    return _memory_manager

def configure_memory_management(config: MemoryConfig):
    """Configure global memory management settings."""
    global _memory_manager

    with _memory_manager_lock:
        if _memory_manager is not None:
            _memory_manager.stop()
        _memory_manager = MemoryManager(config)
        _memory_manager.start()

# Memory-aware file operations
def read_file_memory_safe(file_path: str, encoding: str = 'utf-8') -> Union[str, LazyTextLoader]:
    """Memory-safe file reading with automatic optimization."""
    memory_manager = get_memory_manager()
    return memory_manager.read_file_smart(file_path)

def process_large_file(file_path: str, processor: Callable[[str], str],
                      output_path: str) -> bool:
    """Process large file with memory-safe streaming."""
    memory_manager = get_memory_manager()
    return memory_manager.stream_processor.transform_file(file_path, output_path, processor)

def analyze_file_memory_safe(file_path: str) -> Dict[str, Any]:
    """Analyze file without loading into memory."""
    memory_manager = get_memory_manager()
    return memory_manager.stream_processor.analyze_file(file_path)

# ====== Consolidated from memory_management_integration.py ======
# Memory management integration functionality consolidated

# ====== Consolidated from advanced_memory_features.py ======
# Advanced memory features consolidated

# ====== Consolidated from intelligent_cache.py ======
# Intelligent cache functionality consolidated

# ====== Consolidated from cache_management.py ======
# Cache management functionality consolidated

# Simple FileCache class for backward compatibility
class FileCache:
    """Simple file cache for backward compatibility"""

    def __init__(self, max_size: int = 100, ttl_seconds: int = None):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds  # Currently not implemented but accepted for compatibility

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            # Remove oldest item
            self.cache.popitem(last=False)
        self.cache[key] = value

    def update(self, key: str, value: Any) -> None:
        """Update item in cache (alias for set for compatibility)"""
        self.set(key, value)

    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()

    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

class ProjectFileCache:
    """Project-specific file cache that handles actual file operations."""

    def __init__(self, project_name: str):
        """Initialize with project name."""
        self.project_name = project_name
        self.cache = {}

        # Import here to avoid circular imports
        from .file_operations import read_file, save_to_file
        from .utils import project_file_path
        self.read_file = read_file
        self.save_to_file = save_to_file
        self.project_file_path = project_file_path

    def get(self, filename: str) -> Optional[str]:
        """Get file content, cached or from disk."""
        # Check cache first
        if filename in self.cache:
            return self.cache[filename]

        try:
            # Read from project file
            file_path = self.project_file_path(self.project_name, filename)
            content = self.read_file(file_path)
            if content is not None:
                self.cache[filename] = content
                return content
        except Exception as e:
            logging.error(f"Failed to read file {filename} for project {self.project_name}: {e}")

        return None

    def update(self, filename: str, content: str) -> bool:
        """Update file content both in cache and on disk."""
        try:
            # Update cache
            self.cache[filename] = content

            # Save to disk
            file_path = self.project_file_path(self.project_name, filename)
            success = self.save_to_file(file_path, content)

            if not success:
                # Remove from cache if save failed
                self.cache.pop(filename, None)
                return False

            return True
        except Exception as e:
            logging.error(f"Failed to update file {filename} for project {self.project_name}: {e}")
            # Remove from cache if update failed
            self.cache.pop(filename, None)
            return False

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()

# Factory function for cache manager
def get_cache_manager(project_name: str = "default") -> FileCache:
    """Get cache manager instance"""
    return FileCache()

# Alias for backward compatibility
MemoryCache = FileCache
