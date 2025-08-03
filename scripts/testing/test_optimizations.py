#!/usr/bin/env python3
"""
Test script for FANWS performance optimizations
"""

import sys
import os
import time
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_lazy_loading():
    """Test lazy loading of NLTK and scikit-learn"""
    print("=" * 50)
    print("Testing Lazy Loading")
    print("=" * 50)

    # Test NLTK lazy loading
    print("\n1. Testing NLTK lazy loading...")
    from module_compatibility import get_nltk, NLTK_AVAILABLE

    # First call should load NLTK
    start_time = time.time()
    nltk = get_nltk()
    load_time = time.time() - start_time
    print(f"   NLTK loaded in {load_time:.4f} seconds")
    print(f"   NLTK available: {NLTK_AVAILABLE}")

    # Test tokenization
    text = "Hello world. This is a test sentence."
    tokens = nltk.tokenize.word_tokenize(text)
    sentences = nltk.tokenize.sent_tokenize(text)
    print(f"   Word tokens: {tokens}")
    print(f"   Sentences: {sentences}")

    # Test scikit-learn lazy loading
    print("\n2. Testing scikit-learn lazy loading...")
    from module_compatibility import get_sklearn, SKLEARN_AVAILABLE

    start_time = time.time()
    sklearn = get_sklearn()
    load_time = time.time() - start_time
    print(f"   Scikit-learn loaded in {load_time:.4f} seconds")
    print(f"   Scikit-learn available: {SKLEARN_AVAILABLE}")

    # Test basic functionality
    vectorizer = sklearn.feature_extraction.text.TfidfVectorizer()
    docs = ["Hello world", "Machine learning is fun"]
    features = vectorizer.fit_transform(docs)
    print(f"   TF-IDF features shape: {features}")

def test_memory_monitoring():
    """Test memory monitoring functionality"""
    print("\n" + "=" * 50)
    print("Testing Memory Monitoring")
    print("=" * 50)

    try:
        import psutil

        # Get current memory usage
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory_mb = process.memory_info().rss / 1024 / 1024

        print(f"\n   System Memory Usage: {memory.percent:.1f}%")
        print(f"   Available Memory: {memory.available / 1024 / 1024:.1f} MB")
        print(f"   Process Memory Usage: {process_memory_mb:.1f} MB")

        # Test memory warning threshold
        threshold = 80
        if memory.percent > threshold:
            print(f"   ⚠ WARNING: Memory usage ({memory.percent:.1f}%) exceeds threshold ({threshold}%)")
        else:
            print(f"   ✓ Memory usage is within acceptable limits")

    except ImportError:
        print("\n   ⚠ psutil not available - memory monitoring disabled")

def test_api_caching():
    """Test API caching functionality"""
    print("\n" + "=" * 50)
    print("Testing API Caching")
    print("=" * 50)

    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from api_manager import SQLiteCache

        # Test SQLite cache
        print("\n1. Testing SQLite cache...")
        cache = SQLiteCache(cache_dir="test_cache")

        # Test cache operations
        test_data = {"message": "Hello, World!", "timestamp": time.time()}
        cache_key = "test_key_123"

        # Set data
        start_time = time.time()
        cache.set(cache_key, test_data)
        set_time = time.time() - start_time
        print(f"   Cache set time: {set_time:.4f} seconds")

        # Get data
        start_time = time.time()
        retrieved_data = cache.get(cache_key)
        get_time = time.time() - start_time
        print(f"   Cache get time: {get_time:.4f} seconds")
        print(f"   Data retrieved successfully: {retrieved_data == test_data}")

        # Get cache stats
        stats = cache.get_cache_stats()
        print(f"   Cache stats: {stats}")

        # Test compression
        large_data = {"content": "x" * 1000, "data": list(range(100))}
        cache.set("large_key", large_data)
        retrieved_large = cache.get("large_key")
        print(f"   Large data compression test: {retrieved_large == large_data}")

    except Exception as e:
        print(f"\n   ⚠ API caching test failed: {e}")

def test_threading():
    """Test QThread API worker"""
    print("\n" + "=" * 50)
    print("Testing QThread API Worker")
    print("=" * 50)

    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        from api_manager import APIWorkerThread

        # Create Qt application (required for QThread)
        app = QApplication.instance() or QApplication(sys.argv)

        print("\n   Creating API worker thread...")
        worker = APIWorkerThread()

        # Test signals
        request_completed = False

        def on_completed(request_id, response):
            nonlocal request_completed
            print(f"   Request {request_id} completed: {len(str(response))} bytes")
            request_completed = True
            app.quit()

        def on_failed(request_id, error):
            print(f"   Request {request_id} failed: {error}")
            app.quit()

        worker.request_completed.connect(on_completed)
        worker.request_failed.connect(on_failed)

        # Add a test request (this will fail since we don't have real API keys)
        print("   Adding test request...")
        worker.add_request(
            "test_req_1",
            "openai",
            "/models",
            "GET"
        )

        # Set a timeout
        QTimer.singleShot(3000, app.quit)  # 3 second timeout

        print("   Processing requests...")
        app.exec_()

        print(f"   Thread test completed")

    except Exception as e:
        print(f"\n   ⚠ Threading test failed: {e}")

def main():
    """Run all optimization tests"""
    print("FANWS Performance Optimization Tests")
    print("=" * 60)

    test_lazy_loading()
    test_memory_monitoring()
    test_api_caching()
    test_threading()

    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main()
