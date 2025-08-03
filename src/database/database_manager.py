"""
Enhanced Database Layer for FANWS - Priority 4.2
Provides unified database abstraction with connection pooling, migrations, and optimization.
"""

import sqlite3
import threading
import time
import logging
import json
import os
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import weakref
from queue import Queue, Empty
import hashlib

# Configuration constants
DEFAULT_POOL_SIZE = 5
DEFAULT_MAX_CONNECTIONS = 20
DEFAULT_CONNECTION_TIMEOUT = 30
DEFAULT_QUERY_TIMEOUT = 30
MIGRATION_VERSION_KEY = "schema_version"

class ConnectionState(Enum):
    """Database connection states."""
    IDLE = "idle"
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    database_path: str = "fanws.db"
    pool_size: int = DEFAULT_POOL_SIZE
    max_connections: int = DEFAULT_MAX_CONNECTIONS
    connection_timeout: int = DEFAULT_CONNECTION_TIMEOUT
    query_timeout: int = DEFAULT_QUERY_TIMEOUT
    enable_wal_mode: bool = True
    enable_foreign_keys: bool = True
    enable_query_cache: bool = True
    auto_vacuum: bool = True
    cache_size: int = 2000  # Pages
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    temp_store: str = "MEMORY"

@dataclass
class QueryMetrics:
    """Query performance metrics."""
    query_hash: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    query_type: str
    success: bool
    error_message: Optional[str] = None

class DatabaseConnection:
    """Enhanced database connection with state management."""

    def __init__(self, connection: sqlite3.Connection, config: DatabaseConfig):
        self.connection = connection
        self.config = config
        self.state = ConnectionState.IDLE
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.transaction_count = 0
        self.query_count = 0
        self.lock = threading.Lock()
        self._configure_connection()

    def _configure_connection(self):
        """Configure connection with optimal settings."""
        cursor = self.connection.cursor()

        # Enable foreign keys
        if self.config.enable_foreign_keys:
            cursor.execute("PRAGMA foreign_keys = ON")

        # Set journal mode
        cursor.execute(f"PRAGMA journal_mode = {self.config.journal_mode}")

        # Set synchronous mode
        cursor.execute(f"PRAGMA synchronous = {self.config.synchronous}")

        # Set cache size
        cursor.execute(f"PRAGMA cache_size = {self.config.cache_size}")

        # Set temp store
        cursor.execute(f"PRAGMA temp_store = {self.config.temp_store}")

        # Enable auto vacuum
        if self.config.auto_vacuum:
            cursor.execute("PRAGMA auto_vacuum = INCREMENTAL")

        # Set row factory for dict-like access
        self.connection.row_factory = sqlite3.Row

        cursor.close()

    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        try:
            with self.lock:
                if self.state == ConnectionState.CLOSED:
                    return False

                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
        except Exception:
            self.state = ConnectionState.ERROR
            return False

    def mark_used(self):
        """Mark connection as recently used."""
        with self.lock:
            self.last_used = datetime.now()
            self.query_count += 1

    def close(self):
        """Close the connection."""
        with self.lock:
            if self.state != ConnectionState.CLOSED:
                try:
                    self.connection.close()
                except Exception:
                    pass
                self.state = ConnectionState.CLOSED

class ConnectionPool:
    """Advanced connection pool with health monitoring."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = Queue(maxsize=config.max_connections)
        self.active_connections = weakref.WeakSet()
        self.total_connections = 0
        self.pool_lock = threading.Lock()
        self.metrics = {
            'connections_created': 0,
            'connections_reused': 0,
            'connections_failed': 0,
            'pool_hits': 0,
            'pool_misses': 0
        }

        # Initialize pool
        self._initialize_pool()

        # Start health check thread
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()

    def _initialize_pool(self):
        """Initialize connection pool with minimum connections."""
        for _ in range(self.config.pool_size):
            try:
                conn = self._create_connection()
                self.pool.put(conn)
            except Exception as e:
                logging.error(f"Failed to initialize connection pool: {e}")
                break

    def _create_connection(self) -> DatabaseConnection:
        """Create a new database connection."""
        try:
            sqlite_conn = sqlite3.connect(
                self.config.database_path,
                timeout=self.config.connection_timeout,
                check_same_thread=False
            )

            conn = DatabaseConnection(sqlite_conn, self.config)

            with self.pool_lock:
                self.total_connections += 1
                self.metrics['connections_created'] += 1

            return conn

        except Exception as e:
            with self.pool_lock:
                self.metrics['connections_failed'] += 1
            raise

    def get_connection(self) -> DatabaseConnection:
        """Get a connection from the pool."""
        try:
            # Try to get from pool first
            conn = self.pool.get_nowait()

            # Check if connection is healthy
            if conn.is_healthy():
                conn.mark_used()
                self.active_connections.add(conn)
                with self.pool_lock:
                    self.metrics['pool_hits'] += 1
                    self.metrics['connections_reused'] += 1
                return conn
            else:
                # Connection is unhealthy, close it
                conn.close()

        except Empty:
            # Pool is empty
            pass

        # Create new connection if pool is empty or connection was unhealthy
        with self.pool_lock:
            if self.total_connections < self.config.max_connections:
                conn = self._create_connection()
                conn.mark_used()
                self.active_connections.add(conn)
                self.metrics['pool_misses'] += 1
                return conn
            else:
                self.metrics['pool_misses'] += 1
                raise Exception("Connection pool exhausted")

    def return_connection(self, conn: DatabaseConnection):
        """Return a connection to the pool."""
        if conn.is_healthy() and conn.state != ConnectionState.CLOSED:
            conn.state = ConnectionState.IDLE
            try:
                self.pool.put_nowait(conn)
            except:
                # Pool is full, close connection
                conn.close()
                with self.pool_lock:
                    self.total_connections -= 1
        else:
            # Connection is unhealthy, close it
            conn.close()
            with self.pool_lock:
                self.total_connections -= 1

    def _health_check_loop(self):
        """Background health check for connections."""
        while True:
            try:
                time.sleep(60)  # Check every minute
                self._perform_health_check()
            except Exception as e:
                logging.error(f"Health check error: {e}")

    def _perform_health_check(self):
        """Perform health check on idle connections."""
        connections_to_check = []

        # Get all connections from pool without blocking
        while True:
            try:
                conn = self.pool.get_nowait()
                connections_to_check.append(conn)
            except Empty:
                break

        # Check each connection and put healthy ones back
        for conn in connections_to_check:
            if conn.is_healthy():
                try:
                    self.pool.put_nowait(conn)
                except:
                    # Pool is full, close connection
                    conn.close()
                    with self.pool_lock:
                        self.total_connections -= 1
            else:
                # Connection is unhealthy, close it
                conn.close()
                with self.pool_lock:
                    self.total_connections -= 1

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self.pool_lock:
            return {
                'total_connections': self.total_connections,
                'pool_size': self.pool.qsize(),
                'active_connections': len(self.active_connections),
                'max_connections': self.config.max_connections,
                'metrics': self.metrics.copy()
            }

    def close_all(self):
        """Close all connections in the pool."""
        # Close connections in pool
        while True:
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except Empty:
                break

        # Close active connections
        for conn in list(self.active_connections):
            conn.close()

        with self.pool_lock:
            self.total_connections = 0

class DatabaseMigration:
    """Database migration management."""

    def __init__(self, version: int, description: str, up_sql: str, down_sql: str = ""):
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql

    def apply(self, connection: sqlite3.Connection):
        """Apply migration."""
        cursor = connection.cursor()
        try:
            cursor.executescript(self.up_sql)
            connection.commit()
            logging.info(f"Applied migration {self.version}: {self.description}")
        except Exception as e:
            connection.rollback()
            logging.error(f"Failed to apply migration {self.version}: {e}")
            raise
        finally:
            cursor.close()

    def rollback(self, connection: sqlite3.Connection):
        """Rollback migration."""
        if not self.down_sql:
            raise ValueError(f"No rollback SQL for migration {self.version}")

        cursor = connection.cursor()
        try:
            cursor.executescript(self.down_sql)
            connection.commit()
            logging.info(f"Rolled back migration {self.version}: {self.description}")
        except Exception as e:
            connection.rollback()
            logging.error(f"Failed to rollback migration {self.version}: {e}")
            raise
        finally:
            cursor.close()

class DatabaseManager:
    """Enhanced database manager with connection pooling and migrations."""

    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.pool = ConnectionPool(self.config)
        self.query_cache = {} if self.config.enable_query_cache else None
        self.migrations = self._load_migrations()
        self.query_metrics = []
        self.metrics_lock = threading.Lock()

        # Ensure database exists and is migrated
        self._ensure_database()
        self._run_migrations()

    def _ensure_database(self):
        """Ensure database file exists."""
        db_path = Path(self.config.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create database if it doesn't exist
        if not db_path.exists():
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS _metadata (key TEXT PRIMARY KEY, value TEXT)")
                conn.commit()

    def _load_migrations(self) -> List[DatabaseMigration]:
        """Load database migrations."""
        migrations = []

        # Migration 1: Initial schema
        migrations.append(DatabaseMigration(
            version=1,
            description="Initial schema",
            up_sql="""
                CREATE TABLE IF NOT EXISTS _metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_date TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    settings TEXT,
                    word_count INTEGER DEFAULT 0,
                    target_words INTEGER DEFAULT 50000,
                    metadata TEXT
                );

                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    api_type TEXT NOT NULL,
                    endpoint TEXT,
                    timestamp TEXT NOT NULL,
                    tokens_used INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    response_time REAL DEFAULT 0.0,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    request_hash TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );

                CREATE TABLE IF NOT EXISTS content_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    content_type TEXT NOT NULL,
                    content_key TEXT NOT NULL,
                    content_value TEXT,
                    content_hash TEXT,
                    created_date TEXT NOT NULL,
                    expires_date TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    UNIQUE(project_id, content_type, content_key)
                );

                CREATE TABLE IF NOT EXISTS writing_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    words_written INTEGER DEFAULT 0,
                    session_type TEXT DEFAULT 'writing',
                    notes TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );

                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    project_id INTEGER,
                    additional_data TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );
            """,
            down_sql="""
                DROP TABLE IF EXISTS performance_metrics;
                DROP TABLE IF EXISTS writing_sessions;
                DROP TABLE IF EXISTS content_cache;
                DROP TABLE IF EXISTS api_usage;
                DROP TABLE IF EXISTS projects;
            """
        ))

        # Migration 2: Add indexes for performance (corrected for actual schema)
        migrations.append(DatabaseMigration(
            version=2,
            description="Add performance indexes",
            up_sql="""
                CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
                CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
                CREATE INDEX IF NOT EXISTS idx_projects_last_modified ON projects(last_modified);

                CREATE INDEX IF NOT EXISTS idx_api_usage_project_name ON api_usage(project_name);
                CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp);
                CREATE INDEX IF NOT EXISTS idx_api_usage_api_type ON api_usage(api_type);

                CREATE INDEX IF NOT EXISTS idx_content_cache_project_name ON content_cache(project_name);
                CREATE INDEX IF NOT EXISTS idx_content_cache_content_type ON content_cache(content_type);
                CREATE INDEX IF NOT EXISTS idx_content_cache_created_date ON content_cache(created_date);
                CREATE INDEX IF NOT EXISTS idx_content_cache_expires_date ON content_cache(expires_date);

                CREATE INDEX IF NOT EXISTS idx_writing_sessions_project_name ON writing_sessions(project_name);
                CREATE INDEX IF NOT EXISTS idx_writing_sessions_start_time ON writing_sessions(start_time);

                CREATE INDEX IF NOT EXISTS idx_performance_metrics_project_name ON performance_metrics(project_name);
                CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);
                CREATE INDEX IF NOT EXISTS idx_performance_metrics_metric_type ON performance_metrics(metric_type);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_performance_metrics_metric_type;
                DROP INDEX IF EXISTS idx_performance_metrics_timestamp;
                DROP INDEX IF EXISTS idx_performance_metrics_project_name;
                DROP INDEX IF EXISTS idx_writing_sessions_start_time;
                DROP INDEX IF EXISTS idx_writing_sessions_project_name;
                DROP INDEX IF EXISTS idx_content_cache_expires_date;
                DROP INDEX IF EXISTS idx_content_cache_created_date;
                DROP INDEX IF EXISTS idx_content_cache_content_type;
                DROP INDEX IF EXISTS idx_content_cache_project_name;
                DROP INDEX IF EXISTS idx_api_usage_api_type;
                DROP INDEX IF EXISTS idx_api_usage_timestamp;
                DROP INDEX IF EXISTS idx_api_usage_project_name;
                DROP INDEX IF EXISTS idx_projects_last_modified;
                DROP INDEX IF EXISTS idx_projects_status;
                DROP INDEX IF EXISTS idx_projects_name;
            """
        ))

        return migrations

    def _get_schema_version(self) -> int:
        """Get current schema version."""
        try:
            with self.get_connection() as conn:
                cursor = conn.connection.cursor()
                cursor.execute("SELECT value FROM _metadata WHERE key = ?", (MIGRATION_VERSION_KEY,))
                result = cursor.fetchone()
                return int(result[0]) if result else 0
        except Exception:
            return 0

    def _set_schema_version(self, version: int):
        """Set schema version."""
        with self.get_connection() as conn:
            cursor = conn.connection.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO _metadata (key, value) VALUES (?, ?)",
                (MIGRATION_VERSION_KEY, str(version))
            )
            conn.connection.commit()

    def _run_migrations(self):
        """Run pending migrations."""
        current_version = self._get_schema_version()

        for migration in self.migrations:
            if migration.version > current_version:
                logging.info(f"Running migration {migration.version}: {migration.description}")

                with self.get_connection() as conn:
                    migration.apply(conn.connection)
                    self._set_schema_version(migration.version)

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        conn = self.pool.get_connection()
        try:
            conn.state = ConnectionState.ACTIVE
            yield conn
        finally:
            conn.state = ConnectionState.IDLE
            self.pool.return_connection(conn)

    def execute_query(self, query: str, params: Tuple = None, fetch: str = "all") -> Any:
        """Execute a query with performance tracking."""
        start_time = time.time()
        query_hash = hashlib.md5(query.encode()).hexdigest()

        # Check query cache
        if self.query_cache and params is None:
            cached_result = self.query_cache.get(query_hash)
            if cached_result:
                return cached_result

        try:
            with self.get_connection() as conn:
                cursor = conn.connection.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Fetch results based on fetch parameter
                if fetch == "all":
                    result = cursor.fetchall()
                elif fetch == "one":
                    result = cursor.fetchone()
                elif fetch == "many":
                    result = cursor.fetchmany()
                else:
                    result = cursor.rowcount

                # Cache result if caching is enabled
                if self.query_cache and params is None and fetch in ["all", "one"]:
                    self.query_cache[query_hash] = result

                # Track metrics
                execution_time = time.time() - start_time
                self._track_query_metrics(query_hash, execution_time, cursor.rowcount, True)

                return result

        except Exception as e:
            execution_time = time.time() - start_time
            self._track_query_metrics(query_hash, execution_time, 0, False, str(e))
            raise

    def execute_transaction(self, operations: List[Tuple[str, Tuple]]) -> bool:
        """Execute multiple operations in a transaction."""
        try:
            with self.get_connection() as conn:
                conn.connection.execute("BEGIN")

                for query, params in operations:
                    cursor = conn.connection.cursor()
                    cursor.execute(query, params)

                conn.connection.commit()
                return True

        except Exception as e:
            conn.connection.rollback()
            logging.error(f"Transaction failed: {e}")
            raise

    def _track_query_metrics(self, query_hash: str, execution_time: float,
                            rows_affected: int, success: bool, error_message: str = None):
        """Track query performance metrics."""
        metric = QueryMetrics(
            query_hash=query_hash,
            execution_time=execution_time,
            rows_affected=rows_affected,
            timestamp=datetime.now(),
            query_type="SELECT" if query_hash.startswith("SELECT") else "OTHER",
            success=success,
            error_message=error_message
        )

        with self.metrics_lock:
            self.query_metrics.append(metric)

            # Keep only last 1000 metrics
            if len(self.query_metrics) > 1000:
                self.query_metrics = self.query_metrics[-1000:]

    def get_query_metrics(self) -> List[QueryMetrics]:
        """Get query performance metrics."""
        with self.metrics_lock:
            return self.query_metrics.copy()

    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        stats = {
            'pool_stats': self.pool.get_stats(),
            'database_path': self.config.database_path,
            'schema_version': self._get_schema_version(),
            'cache_enabled': self.config.enable_query_cache,
            'cache_size': len(self.query_cache) if self.query_cache else 0
        }

        # Add database size
        try:
            db_path = Path(self.config.database_path)
            if db_path.exists():
                stats['database_size'] = db_path.stat().st_size
        except Exception:
            stats['database_size'] = 0

        return stats

    def optimize_database(self):
        """Optimize database performance."""
        try:
            with self.get_connection() as conn:
                cursor = conn.connection.cursor()

                # Analyze tables for query optimization
                cursor.execute("ANALYZE")

                # Incremental vacuum
                cursor.execute("PRAGMA incremental_vacuum")

                # Optimize indexes
                cursor.execute("REINDEX")

                conn.connection.commit()
                logging.info("Database optimization completed")

        except Exception as e:
            logging.error(f"Database optimization failed: {e}")
            raise

    def store_performance_metrics(self, metrics: dict):
        """Store performance metrics in the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.connection.cursor()

                # Create table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metric_type TEXT,
                        metric_data TEXT
                    )
                ''')

                # Store metrics as JSON
                import json
                metric_data = json.dumps(metrics)
                cursor.execute('''
                    INSERT INTO performance_metrics (metric_type, metric_data)
                    VALUES (?, ?)
                ''', ('system_metrics', metric_data))

                conn.connection.commit()

        except Exception as e:
            logging.error(f"Failed to store performance metrics: {e}")

    def close(self):
        """Close database manager and all connections."""
        self.pool.close_all()
        if self.query_cache:
            self.query_cache.clear()

# Singleton instance
_enhanced_db_manager = None
_db_manager_lock = threading.Lock()

def get_db_manager(config: DatabaseConfig = None) -> DatabaseManager:
    """Get singleton enhanced database manager."""
    global _enhanced_db_manager

    if _enhanced_db_manager is None:
        with _db_manager_lock:
            if _enhanced_db_manager is None:
                _enhanced_db_manager = DatabaseManager(config)

    return _enhanced_db_manager

# Legacy compatibility alias - now points to the main class
class DatabaseIntegrationLayer:
    """Integration layer for database operations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize with an enhanced database manager."""
        self.db_manager = db_manager

    def __getattr__(self, name):
        """Delegate method calls to the database manager."""
        return getattr(self.db_manager, name)
