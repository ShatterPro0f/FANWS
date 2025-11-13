"""
API manager module for FANWS application.
Handles external API interactions, rate limiting, response processing, and caching.
"""

import requests
import json
import time
import logging
import threading
import sqlite3
import hashlib
import os
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta

# Retry logic with tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Compression support
try:
    import lz4.frame
    LZ4_AVAILABLE = True
    logging.info("✓ LZ4 compression available")
except ImportError:
    LZ4_AVAILABLE = False
    logging.warning("⚠ LZ4 not available - using no compression")

from PyQt5.QtCore import QThread, pyqtSignal, QObject
from ..database.database_manager import DatabaseManager
from ..core.error_handling_system import ErrorHandler, APIError
# from ..core.error_handling_system import MemoryCache  # MemoryCache not available


# Simple in-memory cache wrapper to provide get/set/clear and stats
class MemoryCache:
    def __init__(self):
        self._cache = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        val = self._cache.get(key)
        if val is not None:
            self.hits += 1
        else:
            self.misses += 1
        return val

    def set(self, key: str, value):
        self._cache[key] = value

    def clear(self):
        self._cache.clear()

class RateLimiter:
    """Rate limiter for API requests."""

    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        """Initialize rate limiter."""
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = threading.RLock()

    def can_make_request(self) -> bool:
        """Check if a request can be made."""
        with self._lock:
            now = time.time()
            # Remove old requests
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

            return len(self.requests) < self.max_requests

    def record_request(self):
        """Record a request."""
        with self._lock:
            self.requests.append(time.time())

    def get_wait_time(self) -> float:
        """Get time to wait before next request."""
        with self._lock:
            if not self.requests:
                return 0.0

            oldest_request = min(self.requests)
            wait_time = (oldest_request + self.time_window) - time.time()
            return max(0.0, wait_time)


class SQLiteCache:
    """SQLite-based cache with LZ4 compression for API responses"""

    def __init__(self, cache_dir: str = "cache", max_age_days: int = 7):
        """Initialize SQLite cache"""
        self.cache_dir = cache_dir
        self.max_age_days = max_age_days
        self.db_path = os.path.join(cache_dir, "api_cache.db")
        self._lock = threading.RLock()

        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize the cache database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    timestamp REAL,
                    compressed INTEGER
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON api_cache(timestamp)
            """)

    def _compress_data(self, data: str) -> tuple[bytes, bool]:
        """Compress data if LZ4 is available"""
        if LZ4_AVAILABLE:
            try:
                compressed = lz4.frame.compress(data.encode('utf-8'))
                return compressed, True
            except Exception as e:
                logging.warning(f"LZ4 compression failed: {e}")

        return data.encode('utf-8'), False

    def _decompress_data(self, data: bytes, compressed: bool) -> str:
        """Decompress data if needed"""
        if compressed and LZ4_AVAILABLE:
            try:
                return lz4.frame.decompress(data).decode('utf-8')
            except Exception as e:
                logging.warning(f"LZ4 decompression failed: {e}")
                return data.decode('utf-8')

        return data.decode('utf-8')

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT data, timestamp, compressed FROM api_cache WHERE key = ?",
                        (key,)
                    )
                    result = cursor.fetchone()

                    if result is None:
                        return None

                    data_blob, timestamp, compressed = result

                    # Check if data is expired
                    age_days = (time.time() - timestamp) / (24 * 3600)
                    if age_days > self.max_age_days:
                        self.delete(key)
                        return None

                    # Decompress and parse data
                    data_str = self._decompress_data(data_blob, bool(compressed))
                    return json.loads(data_str)

            except Exception as e:
                logging.error(f"Cache get error: {e}")
                return None

    def set(self, key: str, data: Dict[str, Any]):
        """Set cached data"""
        with self._lock:
            try:
                data_str = json.dumps(data)
                data_blob, compressed = self._compress_data(data_str)

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO api_cache (key, data, timestamp, compressed) VALUES (?, ?, ?, ?)",
                        (key, data_blob, time.time(), int(compressed))
                    )

            except Exception as e:
                logging.error(f"Cache set error: {e}")

    def delete(self, key: str):
        """Delete cached data"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM api_cache WHERE key = ?", (key,))
            except Exception as e:
                logging.error(f"Cache delete error: {e}")

    def clear_expired(self):
        """Clear expired cache entries"""
        with self._lock:
            try:
                cutoff_time = time.time() - (self.max_age_days * 24 * 3600)
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM api_cache WHERE timestamp < ?",
                        (cutoff_time,)
                    )
                    deleted_count = cursor.rowcount
                    logging.info(f"Cleared {deleted_count} expired cache entries")
            except Exception as e:
                logging.error(f"Cache cleanup error: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM api_cache")
                    total_entries = cursor.fetchone()[0]

                    cursor = conn.execute(
                        "SELECT SUM(LENGTH(data)) FROM api_cache"
                    )
                    total_size = cursor.fetchone()[0] or 0

                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM api_cache WHERE compressed = 1"
                    )
                    compressed_entries = cursor.fetchone()[0]

                    return {
                        'total_entries': total_entries,
                        'total_size_bytes': total_size,
                        'compressed_entries': compressed_entries,
                        'cache_file': self.db_path
                    }
            except Exception as e:
                logging.error(f"Cache stats error: {e}")
                return {}


class APIWorkerThread(QThread):
    """QThread worker for API requests"""

    # Signals
    request_completed = pyqtSignal(str, dict)  # request_id, response
    request_failed = pyqtSignal(str, str)      # request_id, error_message
    progress_updated = pyqtSignal(str, str)    # request_id, status

    def __init__(self, parent=None):
        super().__init__(parent)
        self.request_queue = []
        self.current_request = None
        self._lock = threading.RLock()
        self._stop_requested = False

    def add_request(self, request_id: str, api_name: str, endpoint: str,
                   method: str = 'POST', data: Optional[Dict] = None,
                   headers: Optional[Dict] = None, use_cache: bool = True,
                   cache_key: Optional[str] = None):
        """Add API request to queue"""
        with self._lock:
            request = {
                'id': request_id,
                'api_name': api_name,
                'endpoint': endpoint,
                'method': method,
                'data': data,
                'headers': headers,
                'use_cache': use_cache,
                'cache_key': cache_key
            }
            self.request_queue.append(request)

        if not self.isRunning():
            self.start()

    def run(self):
        """Process API requests from queue"""
        while not self._stop_requested:
            with self._lock:
                if not self.request_queue:
                    break
                self.current_request = self.request_queue.pop(0)

            if self.current_request:
                self._process_request(self.current_request)

            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    def _process_request(self, request):
        """Process a single API request"""
        try:
            request_id = request['id']
            self.progress_updated.emit(request_id, "Processing request...")

            # Get API manager and make request
            api_manager = get_api_manager()
            response = api_manager._make_sync_request(
                request['api_name'],
                request['endpoint'],
                request['method'],
                request['data'],
                request['headers'],
                request['use_cache'],
                request['cache_key']
            )

            self.request_completed.emit(request_id, response)

        except Exception as e:
            self.request_failed.emit(request['id'], str(e))

    def stop_processing(self):
        """Stop processing requests"""
        self._stop_requested = True

class APIManager(QObject):
    """Manager for external API interactions with threading and caching support."""

    # Signals for async operations
    request_completed = pyqtSignal(str, dict)
    request_failed = pyqtSignal(str, str)

    def __init__(self):
        """Initialize API manager."""
        super().__init__()

        self.db_manager = DatabaseManager()
        self.memory_cache = MemoryCache()  # In-memory cache wrapper
        self.sqlite_cache = SQLiteCache()  # New SQLite cache with compression
        self.rate_limiters = {}
        self.api_keys = {}
        self.api_endpoints = {}
        self._lock = threading.RLock()

        # Thread worker for async requests
        self.worker_thread = APIWorkerThread()
        self.worker_thread.request_completed.connect(self.request_completed)
        self.worker_thread.request_failed.connect(self.request_failed)

        # Request tracking
        self._pending_requests = {}
        self._request_counter = 0

        # Initialize default configurations
        self._setup_default_apis()

        logging.info("APIManager initialized with threading and SQLite caching")

    def _generate_cache_key(self, api_name: str, endpoint: str, data: Optional[Dict] = None,
                           project_context: Optional[Dict] = None) -> str:
        """Generate cache key for request with project context"""
        key_data = {
            'api': api_name,
            'endpoint': endpoint,
            'data': data or {},
            'project_context': project_context or {}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_project_context(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Get current project context for enhanced prompts"""
        context = {}

        if not project_name:
            # Try to get current project from various sources
            try:
                # This would be set by the main application
                project_name = getattr(self, '_current_project', None)
            except:
                project_name = None

        if project_name:
            context['project_name'] = project_name

            # Try to load project metadata
            try:
                import os
                project_dir = os.path.join("projects", project_name)

                # Load project configuration if it exists
                config_file = os.path.join(project_dir, "project_config.json")
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        project_config = json.load(f)
                        context.update({
                            'genre': project_config.get('genre', ''),
                            'style': project_config.get('style', ''),
                            'target_audience': project_config.get('target_audience', ''),
                            'word_count_goal': project_config.get('word_count_goal', 0),
                            'themes': project_config.get('themes', []),
                            'characters': project_config.get('characters', []),
                            'setting': project_config.get('setting', ''),
                        })

                # Load current chapter/section context
                current_chapter_file = os.path.join(project_dir, "current_chapter.txt")
                if os.path.exists(current_chapter_file):
                    with open(current_chapter_file, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                        # Get last 500 characters for context
                        context['recent_content'] = current_content[-500:] if len(current_content) > 500 else current_content

                # Load story outline if available
                outline_file = os.path.join(project_dir, "outline.txt")
                if os.path.exists(outline_file):
                    with open(outline_file, 'r', encoding='utf-8') as f:
                        outline = f.read()
                        context['outline'] = outline[:1000]  # First 1000 chars of outline

            except Exception as e:
                logging.warning(f"Could not load project context: {e}")

        return context

    def _enhance_prompt_with_context(self, prompt: str, project_context: Dict[str, Any]) -> str:
        """Enhance prompt with project context"""
        if not project_context:
            return prompt

        context_parts = []

        if 'project_name' in project_context:
            context_parts.append(f"Project: {project_context['project_name']}")

        if 'genre' in project_context and project_context['genre']:
            context_parts.append(f"Genre: {project_context['genre']}")

        if 'style' in project_context and project_context['style']:
            context_parts.append(f"Writing Style: {project_context['style']}")

        if 'target_audience' in project_context and project_context['target_audience']:
            context_parts.append(f"Target Audience: {project_context['target_audience']}")

        if 'themes' in project_context and project_context['themes']:
            themes_str = ", ".join(project_context['themes'])
            context_parts.append(f"Key Themes: {themes_str}")

        if 'setting' in project_context and project_context['setting']:
            context_parts.append(f"Setting: {project_context['setting']}")

        if 'characters' in project_context and project_context['characters']:
            chars = [char.get('name', str(char)) if isinstance(char, dict) else str(char)
                    for char in project_context['characters'][:5]]  # Limit to 5 characters
            context_parts.append(f"Main Characters: {', '.join(chars)}")

        if 'recent_content' in project_context and project_context['recent_content'].strip():
            context_parts.append(f"Recent Content: ...{project_context['recent_content']}")

        if 'outline' in project_context and project_context['outline'].strip():
            context_parts.append(f"Story Outline: {project_context['outline']}")

        if context_parts:
            context_str = "\n".join(f"[{part}]" for part in context_parts)
            enhanced_prompt = f"{context_str}\n\nUser Request: {prompt}"
            return enhanced_prompt

        return prompt

    def make_request_async(self, api_name: str, endpoint: str, method: str = 'POST',
                          data: Optional[Dict] = None, headers: Optional[Dict] = None,
                          use_cache: bool = True, callback: Optional[Callable] = None) -> str:
        """Make async API request using QThread worker"""

        # Generate request ID
        with self._lock:
            self._request_counter += 1
            request_id = f"req_{self._request_counter}_{int(time.time())}"

        # Generate cache key
        cache_key = self._generate_cache_key(api_name, endpoint, data) if use_cache else None

        # Check cache first
        if use_cache and cache_key:
            # Check memory cache first
            cached_response = self.memory_cache.get(cache_key)
            if cached_response:
                logging.debug(f"Memory cache hit for {api_name} request")
                if callback:
                    callback(cached_response)
                self.request_completed.emit(request_id, cached_response)
                return request_id

            # Check SQLite cache
            cached_response = self.sqlite_cache.get(cache_key)
            if cached_response:
                logging.debug(f"SQLite cache hit for {api_name} request")
                # Store in memory cache for faster access
                self.memory_cache.set(cache_key, cached_response)
                if callback:
                    callback(cached_response)
                self.request_completed.emit(request_id, cached_response)
                return request_id

        # Store callback if provided
        if callback:
            self._pending_requests[request_id] = callback

        # Add to worker thread queue
        self.worker_thread.add_request(
            request_id, api_name, endpoint, method, data, headers, use_cache, cache_key
        )

        return request_id

    def _make_sync_request(self, api_name: str, endpoint: str, method: str = 'POST',
                          data: Optional[Dict] = None, headers: Optional[Dict] = None,
                          use_cache: bool = True, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Make synchronous API request (used by worker thread)"""

        # Check if API is configured
        if api_name not in self.api_endpoints:
            raise APIError(f"API '{api_name}' not configured")

        # Check rate limiting
        rate_limiter = self.rate_limiters.get(api_name)
        if rate_limiter and not rate_limiter.can_make_request():
            wait_time = rate_limiter.get_wait_time()
            raise APIError(f"Rate limit exceeded for {api_name}. Wait {wait_time:.2f} seconds.")

        # Prepare request
        api_config = self.api_endpoints[api_name]
        base_url = api_config['base_url']

        # Build full URL
        if endpoint.startswith('/'):
            url = base_url + endpoint
        else:
            url = f"{base_url}/{endpoint}"

        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'FANWS/1.0'
        }

        if headers:
            request_headers.update(headers)

        # Add API key if available
        api_key = self.get_api_key(api_name)
        if api_key:
            if api_name == 'openai':
                request_headers['Authorization'] = f'Bearer {api_key}'
            elif api_name == 'anthropic':
                request_headers['x-api-key'] = api_key
            elif api_name == 'google':
                request_headers['Authorization'] = f'Bearer {api_key}'

        try:
            # Make request
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=request_headers,
                                       json=data, timeout=30)
            else:
                raise APIError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Record successful request for rate limiting
            if rate_limiter:
                rate_limiter.record_request()

            # Parse response
            response_data = response.json()

            # Cache response
            if use_cache and cache_key:
                # Store in both caches
                self.memory_cache.set(cache_key, response_data)
                self.sqlite_cache.set(cache_key, response_data)

            return response_data

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed for {api_name}: {str(e)}")
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response from {api_name}: {str(e)}")

    def on_request_completed(self, request_id: str, response: Dict[str, Any]):
        """Handle completed async request"""
        callback = self._pending_requests.pop(request_id, None)
        if callback:
            callback(response)

    def on_request_failed(self, request_id: str, error_message: str):
        """Handle failed async request"""
        callback = self._pending_requests.pop(request_id, None)
        if callback:
            callback(None)  # Or pass error info
        logging.error(f"Request {request_id} failed: {error_message}")

    def clear_cache(self):
        """Clear all caches"""
        self.memory_cache.clear()
        # Clear SQLite cache by deleting all entries
        with sqlite3.connect(self.sqlite_cache.db_path) as conn:
            conn.execute("DELETE FROM api_cache")
        logging.info("All caches cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        memory_stats = {
            'memory_cache_size': len(self.memory_cache._cache),
            'memory_cache_hits': getattr(self.memory_cache, 'hits', 0),
            'memory_cache_misses': getattr(self.memory_cache, 'misses', 0)
        }

        sqlite_stats = self.sqlite_cache.get_cache_stats()

        return {**memory_stats, **sqlite_stats}

    def cleanup(self):
        """Cleanup resources"""
        if self.worker_thread.isRunning():
            self.worker_thread.stop_processing()
            self.worker_thread.wait(5000)  # Wait up to 5 seconds
        self.sqlite_cache.clear_expired()

    def _setup_default_apis(self):
        """Setup default API configurations."""
        # Placeholder configurations for common APIs
        self.api_endpoints = {
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'endpoints': {
                    'chat': '/chat/completions',
                    'completions': '/completions',
                    'embeddings': '/embeddings'
                },
                'rate_limit': {'requests': 3000, 'window': 60}  # 3000 requests per minute
            },
            'anthropic': {
                'base_url': 'https://api.anthropic.com/v1',
                'endpoints': {
                    'messages': '/messages'
                },
                'rate_limit': {'requests': 1000, 'window': 60}
            },
            'google': {
                'base_url': 'https://generativelanguage.googleapis.com/v1',
                'endpoints': {
                    'generate': '/models/text-bison-001:generateText'
                },
                'rate_limit': {'requests': 60, 'window': 60}
            },
            'huggingface': {
                'base_url': 'https://api-inference.huggingface.co',
                'endpoints': {
                    'inference': '/models'
                },
                'rate_limit': {'requests': 1000, 'window': 3600}
            }
        }

        # Initialize rate limiters
        for api_name, config in self.api_endpoints.items():
            rate_config = config.get('rate_limit', {'requests': 100, 'window': 3600})
            self.rate_limiters[api_name] = RateLimiter(
                max_requests=rate_config['requests'],
                time_window=rate_config['window']
            )

    def set_api_key(self, api_name: str, api_key: str):
        """Set API key for a service."""
        with self._lock:
            self.api_keys[api_name] = api_key
            logging.info(f"API key set for {api_name}")

    def get_api_key(self, api_name: str) -> Optional[str]:
        """Get API key for a service."""
        return self.api_keys.get(api_name)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout)),
        reraise=True
    )
    def _make_http_request(self, method: str, url: str, headers: Dict[str, str],
                          data: Optional[Dict] = None, timeout: int = 30) -> requests.Response:
        """Make HTTP request with retry logic."""
        logging.debug(f"Making {method} request to {url} (with retry logic)")

        if method.upper() == 'GET':
            return requests.get(url, headers=headers, params=data, timeout=timeout)
        elif method.upper() == 'POST':
            return requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == 'PUT':
            return requests.put(url, headers=headers, json=data, timeout=timeout)
        else:
            raise APIError(f"Unsupported HTTP method: {method}")

    def make_request(self, api_name: str, endpoint: str, method: str = 'POST',
                    data: Optional[Dict] = None, headers: Optional[Dict] = None,
                    use_cache: bool = True, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Make API request with rate limiting, caching, and retry logic."""

        # Check if API is configured
        if api_name not in self.api_endpoints:
            raise APIError(f"API '{api_name}' not configured")

        # Check rate limiting
        rate_limiter = self.rate_limiters.get(api_name)
        if rate_limiter and not rate_limiter.can_make_request():
            wait_time = rate_limiter.get_wait_time()
            raise APIError(f"Rate limit exceeded for {api_name}. Wait {wait_time:.2f} seconds.")

        # Check cache (use SQLite cache instead of response_cache)
        if use_cache and cache_key:
            cached_response = self.sqlite_cache.get(cache_key)
            if cached_response:
                logging.debug(f"SQLite cache hit for {api_name} request")
                return cached_response

        # Prepare request
        api_config = self.api_endpoints[api_name]
        base_url = api_config['base_url']

        # Build full URL
        if endpoint.startswith('/'):
            url = base_url + endpoint
        else:
            url = f"{base_url}/{endpoint}"

        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'FANWS/1.0'
        }

        if headers:
            request_headers.update(headers)

        # Add authentication if available
        api_key = self.get_api_key(api_name)
        if api_key:
            if api_name == 'openai':
                request_headers['Authorization'] = f'Bearer {api_key}'
            elif api_name == 'anthropic':
                request_headers['x-api-key'] = api_key
            elif api_name == 'google':
                request_headers['Authorization'] = f'Bearer {api_key}'
            elif api_name == 'huggingface':
                request_headers['Authorization'] = f'Bearer {api_key}'

        try:
            # Record request for rate limiting
            if rate_limiter:
                rate_limiter.record_request()

            # Make request with retry logic
            start_time = time.time()

            response = self._make_http_request(method, url, request_headers, data)

            request_time = time.time() - start_time

            # Handle response
            if response.status_code == 200:
                result = response.json()

                # Cache successful response in SQLite
                if use_cache and cache_key:
                    self.sqlite_cache.set(cache_key, result)
                    logging.debug(f"Cached response for {api_name} request in SQLite")

                # Log API usage
                self._log_api_usage(api_name, endpoint, True, request_time, response.status_code)

                return result
            else:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                self._log_api_usage(api_name, endpoint, False, request_time, response.status_code)
                raise APIError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            self._log_api_usage(api_name, endpoint, False, 0, 0)
            raise APIError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during API request: {str(e)}"
            logging.error(error_msg)
            self._log_api_usage(api_name, endpoint, False, 0, 0)
            raise APIError(error_msg)

    def _log_api_usage(self, api_name: str, endpoint: str, success: bool,
                      response_time: float, status_code: int):
        """Log API usage to database."""
        try:
            self.db_manager.log_api_usage(
                api_name=api_name,
                endpoint=endpoint,
                success=success,
                response_time=response_time,
                status_code=status_code
            )
        except Exception as e:
            logging.error(f"Failed to log API usage: {str(e)}")

    def generate_text(self, prompt: str, api_name: str = 'openai',
                     model: str = 'gpt-3.5-turbo', max_tokens: int = 500,
                     temperature: float = 0.7, use_cache: bool = True,
                     project_name: Optional[str] = None,
                     use_project_context: bool = True) -> str:
        """Generate text using AI API with optional project context enhancement."""

        # Get project context if enabled
        project_context = {}
        if use_project_context:
            project_context = self._get_project_context(project_name)

        # Enhance prompt with project context
        enhanced_prompt = prompt
        if project_context:
            enhanced_prompt = self._enhance_prompt_with_context(prompt, project_context)
            logging.debug(f"Enhanced prompt with project context: {len(project_context)} context items")

        # Create cache key including project context
        cache_key = None
        if use_cache:
            cache_key = self._generate_cache_key(
                api_name,
                f"generate_text_{model}",
                {
                    'prompt': enhanced_prompt,
                    'max_tokens': max_tokens,
                    'temperature': temperature
                },
                project_context
            )

        try:
            if api_name == 'openai':
                return self._generate_openai_text(enhanced_prompt, model, max_tokens, temperature, cache_key)
            elif api_name == 'anthropic':
                return self._generate_anthropic_text(enhanced_prompt, model, max_tokens, temperature, cache_key)
            elif api_name == 'google':
                return self._generate_google_text(enhanced_prompt, model, max_tokens, temperature, cache_key)
            else:
                raise APIError(f"Text generation not supported for {api_name}")

        except Exception as e:
            logging.error(f"Text generation failed: {str(e)}")
            raise APIError(f"Text generation failed: {str(e)}")

    def set_current_project(self, project_name: str):
        """Set the current project for context enhancement"""
        self._current_project = project_name
        logging.info(f"Set current project to: {project_name}")

    def clear_project_context(self):
        """Clear the current project context"""
        self._current_project = None
        logging.info("Cleared project context")

    def _generate_openai_text(self, prompt: str, model: str, max_tokens: int,
                            temperature: float, cache_key: str) -> str:
        """Generate text using OpenAI API."""
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens,
            'temperature': temperature
        }

        response = self.make_request('openai', '/chat/completions', 'POST', data, cache_key=cache_key)

        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            raise APIError("No response from OpenAI API")

    def _generate_anthropic_text(self, prompt: str, model: str, max_tokens: int,
                               temperature: float, cache_key: str) -> str:
        """Generate text using Anthropic API."""
        data = {
            'model': model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [{'role': 'user', 'content': prompt}]
        }

        response = self.make_request('anthropic', '/messages', 'POST', data, cache_key=cache_key)

        if 'content' in response and len(response['content']) > 0:
            return response['content'][0]['text']
        else:
            raise APIError("No response from Anthropic API")

    def _generate_google_text(self, prompt: str, model: str, max_tokens: int,
                            temperature: float, cache_key: str) -> str:
        """Generate text using Google API."""
        data = {
            'prompt': {'text': prompt},
            'temperature': temperature,
            'candidate_count': 1,
            'max_output_tokens': max_tokens
        }

        response = self.make_request('google', '/models/text-bison-001:generateText', 'POST', data, cache_key=cache_key)

        if 'candidates' in response and len(response['candidates']) > 0:
            return response['candidates'][0]['output']
        else:
            raise APIError("No response from Google API")

    def get_api_usage_stats(self, api_name: Optional[str] = None,
                           days: int = 30) -> Dict[str, Any]:
        """Get API usage statistics."""
        try:
            return self.db_manager.get_api_usage_stats(api_name, days)
        except Exception as e:
            logging.error(f"Failed to get API usage stats: {str(e)}")
            return {}

    def clear_cache(self, api_name: Optional[str] = None):
        """Clear response cache."""
        if api_name:
            # Clear specific API cache (would need more sophisticated cache key management)
            logging.info(f"Clearing cache for {api_name}")
            # For now, clear all cache since we don't have specific API filtering
            self.sqlite_cache.clear()
        else:
            self.sqlite_cache.clear()
            logging.info("Cleared all API response cache")

    def test_api_connection(self, api_name: str) -> bool:
        """Test API connection."""
        try:
            if api_name == 'openai':
                # Test with a simple request
                response = self.make_request('openai', '/models', 'GET', use_cache=False)
                return 'data' in response
            elif api_name == 'anthropic':
                # Anthropic doesn't have a simple test endpoint, so we'll try a minimal request
                test_data = {
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 10,
                    'messages': [{'role': 'user', 'content': 'Hello'}]
                }
                response = self.make_request('anthropic', '/messages', 'POST', test_data, use_cache=False)
                return 'content' in response
            else:
                logging.warning(f"Test connection not implemented for {api_name}")
                return False

        except Exception as e:
            logging.error(f"API connection test failed for {api_name}: {str(e)}")
            return False

    def get_available_models(self, api_name: str) -> List[str]:
        """Get available models for an API."""
        try:
            if api_name == 'openai':
                response = self.make_request('openai', '/models', 'GET', use_cache=True, cache_key=f"models_{api_name}")
                if 'data' in response:
                    return [model['id'] for model in response['data']]
            elif api_name == 'anthropic':
                # Anthropic doesn't have a models endpoint, return known models
                return ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
            elif api_name == 'google':
                return ['text-bison-001', 'text-bison-002', 'gemini-pro']

            return []

        except Exception as e:
            logging.error(f"Failed to get models for {api_name}: {str(e)}")
            return []

    def estimate_cost(self, api_name: str, model: str, prompt_tokens: int,
                     completion_tokens: int = 0) -> float:
        """Estimate cost for API request."""
        # Simplified cost estimation (would need real pricing data)
        pricing = {
            'openai': {
                'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},  # per 1K tokens
                'gpt-4': {'input': 0.03, 'output': 0.06},
                'gpt-4-turbo': {'input': 0.01, 'output': 0.03}
            },
            'anthropic': {
                'claude-3-opus': {'input': 0.015, 'output': 0.075},
                'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
                'claude-3-haiku': {'input': 0.00025, 'output': 0.00125}
            }
        }

        if api_name in pricing and model in pricing[api_name]:
            model_pricing = pricing[api_name][model]
            input_cost = (prompt_tokens / 1000) * model_pricing['input']
            output_cost = (completion_tokens / 1000) * model_pricing['output']
            return input_cost + output_cost

        return 0.0

    # Legacy compatibility methods
    def make_request(self, api_name: str, endpoint: str, method: str = 'POST',
                    data: Optional[Dict] = None, headers: Optional[Dict] = None,
                    use_cache: bool = True, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Legacy synchronous make_request method for backward compatibility"""
        cache_key = cache_key or self._generate_cache_key(api_name, endpoint, data)

        # Check cache first
        if use_cache and cache_key:
            cached_response = self.memory_cache.get(cache_key)
            if cached_response:
                return cached_response
            cached_response = self.sqlite_cache.get(cache_key)
            if cached_response:
                self.memory_cache.set(cache_key, cached_response)
                return cached_response

        # Make synchronous request (pass keyword args for easier testing/mocking)
        result = self._make_sync_request(
            api_name=api_name,
            endpoint=endpoint,
            method=method,
            data=data,
            headers=headers,
            use_cache=use_cache,
            cache_key=cache_key
        )

        # Ensure caching happens even if tests patch _make_sync_request
        try:
            if use_cache and cache_key and result is not None:
                try:
                    self.memory_cache.set(cache_key, result)
                except Exception:
                    pass
                try:
                    self.sqlite_cache.set(cache_key, result)
                except Exception:
                    pass
        except Exception:
            pass

        return result

    def generate_text_openai(self, prompt: str, max_tokens: int, api_key: str) -> str:
        """Legacy OpenAI text generation method"""
        self.set_api_key('openai', api_key)

        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens
        }

        try:
            response = self.make_request('openai', '/chat/completions', 'POST', data)
            if 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content']
            return "API_LIMIT_REACHED"
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return "API_LIMIT_REACHED"

    def generate_text_openai_async(self, prompt: str, max_tokens: int, api_key: str) -> str:
        """Legacy async OpenAI text generation method"""
        # For now, return the synchronous version
        # In a full implementation, this would use the async worker
        return self.generate_text_openai(prompt, max_tokens, api_key)

# Global API manager instance
_api_manager = None

def get_api_manager() -> APIManager:
    """Get global API manager instance."""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager()
    return _api_manager
