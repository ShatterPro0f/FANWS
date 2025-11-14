"""
Connection Pool for SQLite Database
Manages reusable database connections with health monitoring and automatic cleanup.
"""

import sqlite3
import threading
import time
from queue import Queue, Empty
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Manages a pool of SQLite database connections."""
    
    def __init__(self, database_path: str, pool_size: int = 5, timeout: int = 30):
        """
        Initialize connection pool.
        
        Args:
            database_path: Path to SQLite database file
            pool_size: Maximum number of connections in pool
            timeout: Connection timeout in seconds
        """
        self.database_path = database_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._active_connections = 0
        self._total_created = 0
        self._health_check_interval = 60  # seconds
        self._last_health_check = time.time()
        
        # Create initial connections
        for _ in range(pool_size):
            conn = self._create_connection()
            if conn:
                self._pool.put(conn)
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection."""
        try:
            conn = sqlite3.connect(
                self.database_path,
                timeout=self.timeout,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            # Set WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode = WAL")
            # Set synchronous mode
            conn.execute("PRAGMA synchronous = NORMAL")
            # Set cache size
            conn.execute("PRAGMA cache_size = 2000")
            # Set temp store to memory
            conn.execute("PRAGMA temp_store = MEMORY")
            
            self._total_created += 1
            logger.debug(f"Created new database connection (total: {self._total_created})")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    def get_connection(self, block: bool = True, timeout: Optional[float] = None) -> Optional[sqlite3.Connection]:
        """
        Get a connection from the pool.
        
        Args:
            block: Whether to block if no connection available
            timeout: Maximum time to wait for connection
        
        Returns:
            Database connection or None if unavailable
        """
        try:
            # Check if health check is needed
            if time.time() - self._last_health_check > self._health_check_interval:
                self._perform_health_check()
            
            conn = self._pool.get(block=block, timeout=timeout or self.timeout)
            
            # Verify connection is still valid
            if not self._is_connection_valid(conn):
                logger.warning("Retrieved invalid connection, creating new one")
                conn.close()
                conn = self._create_connection()
            
            with self._lock:
                self._active_connections += 1
            
            return conn
        except Empty:
            logger.warning("No connection available in pool")
            return None
    
    def return_connection(self, conn: sqlite3.Connection):
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        if conn is None:
            return
        
        with self._lock:
            self._active_connections -= 1
        
        try:
            # Rollback any uncommitted transactions
            conn.rollback()
            self._pool.put_nowait(conn)
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {e}")
            try:
                conn.close()
            except:
                pass
    
    def _is_connection_valid(self, conn: sqlite3.Connection) -> bool:
        """Check if a connection is still valid."""
        try:
            conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
    
    def _perform_health_check(self):
        """Perform health check on all connections in pool."""
        logger.debug("Performing connection pool health check")
        self._last_health_check = time.time()
        
        # This is a simplified health check
        # In production, you might want to temporarily drain and test all connections
    
    def close_all(self):
        """Close all connections in the pool."""
        logger.info("Closing all database connections")
        
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except Empty:
                break
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
    
    def get_stats(self) -> dict:
        """Get pool statistics."""
        return {
            'pool_size': self.pool_size,
            'available': self._pool.qsize(),
            'active': self._active_connections,
            'total_created': self._total_created
        }


class PooledConnection:
    """Context manager for pooled database connections."""
    
    def __init__(self, pool: ConnectionPool):
        self.pool = pool
        self.conn = None
    
    def __enter__(self) -> sqlite3.Connection:
        self.conn = self.pool.get_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                # Rollback on exception
                try:
                    self.conn.rollback()
                except:
                    pass
            self.pool.return_connection(self.conn)
        return False
