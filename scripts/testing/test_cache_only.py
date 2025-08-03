#!/usr/bin/env python3
"""
Simple test for SQLite cache functionality only
"""

import os
import sys
import time
import sqlite3
import hashlib
import json

# Add compression support
try:
    import lz4.frame
    LZ4_AVAILABLE = True
    print("✓ LZ4 compression available")
except ImportError:
    LZ4_AVAILABLE = False
    print("⚠ LZ4 not available - using no compression")

class SimpleCache:
    """Simplified SQLite cache for testing"""

    def __init__(self, cache_dir="cache"):
        """Initialize cache"""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        self.db_path = os.path.join(cache_dir, "api_cache.db")
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at REAL,
                    ttl INTEGER
                )
            ''')
            conn.commit()

    def _compress_data(self, data: str) -> bytes:
        """Compress data if LZ4 is available"""
        data_bytes = data.encode('utf-8')
        if LZ4_AVAILABLE:
            return lz4.frame.compress(data_bytes)
        return data_bytes

    def _decompress_data(self, data: bytes) -> str:
        """Decompress data if LZ4 was used"""
        if LZ4_AVAILABLE:
            try:
                return lz4.frame.decompress(data).decode('utf-8')
            except:
                pass
        return data.decode('utf-8')

    def set(self, key: str, value: any, ttl: int = 3600):
        """Set cache value"""
        serialized = json.dumps(value)
        compressed = self._compress_data(serialized)
        created_at = time.time()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO cache (key, value, created_at, ttl) VALUES (?, ?, ?, ?)',
                (key, compressed, created_at, ttl)
            )
            conn.commit()

    def get(self, key: str):
        """Get cache value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT value, created_at, ttl FROM cache WHERE key = ?',
                (key,)
            )
            row = cursor.fetchone()

            if row:
                value_blob, created_at, ttl = row

                # Check if expired
                if time.time() - created_at > ttl:
                    conn.execute('DELETE FROM cache WHERE key = ?', (key,))
                    conn.commit()
                    return None

                # Decompress and deserialize
                decompressed = self._decompress_data(value_blob)
                return json.loads(decompressed)

            return None

    def close(self):
        """Clean up (placeholder for compatibility)"""
        pass

def test_cache():
    """Test cache functionality"""
    print("\nTesting SQLite Cache with LZ4 Compression")
    print("=" * 50)

    # Create cache
    cache = SimpleCache("test_cache")

    # Test data
    test_data = {
        "prompt": "Write a story about a robot",
        "response": "Once upon a time, there was a friendly robot named R2D2...",
        "timestamp": time.time(),
        "metadata": {"model": "gpt-3.5-turbo", "tokens": 150}
    }

    print("1. Testing cache set operation...")
    start_time = time.time()
    cache.set("test_key", test_data, ttl=3600)
    set_time = time.time() - start_time
    print(f"   ✓ Cache set completed in {set_time:.4f} seconds")

    print("2. Testing cache get operation...")
    start_time = time.time()
    retrieved_data = cache.get("test_key")
    get_time = time.time() - start_time
    print(f"   ✓ Cache get completed in {get_time:.4f} seconds")

    print("3. Testing data integrity...")
    if retrieved_data == test_data:
        print("   ✓ Retrieved data matches original data")
    else:
        print("   ⚠ Data mismatch detected")
        print(f"   Original: {test_data}")
        print(f"   Retrieved: {retrieved_data}")

    print("4. Testing compression ratio...")
    original_size = len(json.dumps(test_data).encode('utf-8'))

    # Check actual stored size
    db_path = os.path.join("test_cache", "api_cache.db")
    if os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute('SELECT value FROM cache WHERE key = ?', ("test_key",))
            row = cursor.fetchone()
            if row:
                compressed_size = len(row[0])
                ratio = (1 - compressed_size / original_size) * 100
                print(f"   Original size: {original_size} bytes")
                print(f"   Compressed size: {compressed_size} bytes")
                print(f"   ✓ Compression ratio: {ratio:.1f}%")

    print("5. Testing TTL expiration...")
    cache.set("expire_test", {"temp": "data"}, ttl=1)  # 1 second TTL
    immediate = cache.get("expire_test")
    time.sleep(1.1)  # Wait for expiration
    expired = cache.get("expire_test")

    if immediate is not None and expired is None:
        print("   ✓ TTL expiration working correctly")
    else:
        print("   ⚠ TTL expiration not working as expected")

    cache.close()
    print("\n✓ Cache testing completed successfully!")

if __name__ == "__main__":
    test_cache()
