"""
API manager module for FANWS application.
Handles external API interactions, rate limiting, and response processing.
"""

import requests
import json
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from .database_manager import DatabaseManager
from .error_handling_system import ErrorHandler, APIError
from .memory_manager import MemoryCache

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

class APIManager:
    """Manager for external API interactions."""

    def __init__(self):
        """Initialize API manager."""
        self.db_manager = DatabaseManager()
        self.response_cache = MemoryCache(max_size=200, ttl_seconds=1800)  # 30 minutes
        self.rate_limiters = {}
        self.api_keys = {}
        self.api_endpoints = {}
        self._lock = threading.RLock()

        # Initialize default configurations
        self._setup_default_apis()

        logging.info("APIManager initialized")

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

    def make_request(self, api_name: str, endpoint: str, method: str = 'POST',
                    data: Optional[Dict] = None, headers: Optional[Dict] = None,
                    use_cache: bool = True, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Make API request with rate limiting and caching."""

        # Check if API is configured
        if api_name not in self.api_endpoints:
            raise APIError(f"API '{api_name}' not configured")

        # Check rate limiting
        rate_limiter = self.rate_limiters.get(api_name)
        if rate_limiter and not rate_limiter.can_make_request():
            wait_time = rate_limiter.get_wait_time()
            raise APIError(f"Rate limit exceeded for {api_name}. Wait {wait_time:.2f} seconds.")

        # Check cache
        if use_cache and cache_key:
            cached_response = self.response_cache.get(cache_key)
            if cached_response:
                logging.debug(f"Cache hit for {api_name} request")
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

            # Make request
            start_time = time.time()

            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, params=data, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=request_headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=request_headers, json=data, timeout=30)
            else:
                raise APIError(f"Unsupported HTTP method: {method}")

            request_time = time.time() - start_time

            # Handle response
            if response.status_code == 200:
                result = response.json()

                # Cache successful response
                if use_cache and cache_key:
                    self.response_cache.put(cache_key, result)

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
                     temperature: float = 0.7, use_cache: bool = True) -> str:
        """Generate text using AI API."""

        # Create cache key
        cache_key = None
        if use_cache:
            cache_key = f"generate_{api_name}_{model}_{hash(prompt)}_{max_tokens}_{temperature}"

        try:
            if api_name == 'openai':
                return self._generate_openai_text(prompt, model, max_tokens, temperature, cache_key)
            elif api_name == 'anthropic':
                return self._generate_anthropic_text(prompt, model, max_tokens, temperature, cache_key)
            elif api_name == 'google':
                return self._generate_google_text(prompt, model, max_tokens, temperature, cache_key)
            else:
                raise APIError(f"Text generation not supported for {api_name}")

        except Exception as e:
            logging.error(f"Text generation failed: {str(e)}")
            raise APIError(f"Text generation failed: {str(e)}")

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
        else:
            self.response_cache.clear()
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

# Global API manager instance
_api_manager = None

def get_api_manager() -> APIManager:
    """Get global API manager instance."""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager()
    return _api_manager
