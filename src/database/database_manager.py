"""
Database Manager for AAWT
Handles all database operations, schema management, and migrations.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from .connection_pool import ConnectionPool, PooledConnection

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages all database operations for AAWT."""
    
    def __init__(self, database_path: str, pool_size: int = 5):
        """
        Initialize database manager.
        
        Args:
            database_path: Path to SQLite database file
            pool_size: Size of connection pool
        """
        self.database_path = database_path
        
        # Ensure database directory exists
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize connection pool
        self.pool = ConnectionPool(database_path, pool_size)
        
        # Query cache
        self._query_cache = {}
        self._cache_expiry = {}
        self._cache_ttl = 3600  # 1 hour
        
        # Initialize schema
        self._initialize_schema()
        
        logger.info(f"Database manager initialized: {database_path}")
    
    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        with PooledConnection(self.pool) as conn:
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_date TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    settings TEXT,
                    word_count INTEGER DEFAULT 0,
                    target_words INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # API usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    api_type TEXT NOT NULL,
                    endpoint TEXT,
                    response_time REAL,
                    success INTEGER DEFAULT 1,
                    status_code INTEGER,
                    error_message TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    timestamp TEXT NOT NULL,
                    request_hash TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # Content cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    content_type TEXT NOT NULL,
                    content_key TEXT NOT NULL,
                    content_value TEXT,
                    content_hash TEXT,
                    created_date TEXT NOT NULL,
                    expires_date TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE(project_id, content_type, content_key)
                )
            """)
            
            # Writing sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS writing_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    words_written INTEGER DEFAULT 0,
                    session_type TEXT DEFAULT 'writing',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # Change history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS change_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    content_before TEXT,
                    content_after TEXT,
                    timestamp TEXT NOT NULL,
                    character_position INTEGER,
                    line_number INTEGER,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_usage_type_time 
                ON api_usage(api_type, timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp 
                ON api_usage(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_cache_expires 
                ON content_cache(expires_date)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_project_time 
                ON writing_sessions(project_id, start_time)
            """)
            
            conn.commit()
            logger.info("Database schema initialized")
    
    # Project operations
    def create_project(self, name: str, metadata: Optional[Dict] = None) -> Optional[int]:
        """Create a new project."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO projects (name, created_date, last_modified, metadata)
                    VALUES (?, ?, ?, ?)
                """, (name, now, now, json.dumps(metadata or {})))
                
                conn.commit()
                project_id = cursor.lastrowid
                logger.info(f"Created project: {name} (ID: {project_id})")
                return project_id
        except sqlite3.IntegrityError:
            logger.error(f"Project with name '{name}' already exists")
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to create project: {e}")
            return None
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get project: {e}")
            return None
    
    def get_project_by_name(self, name: str) -> Optional[Dict]:
        """Get project by name."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects WHERE name = ?", (name,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get project by name: {e}")
            return None
    
    def list_projects(self) -> List[Dict]:
        """List all projects."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects ORDER BY last_modified DESC")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to list projects: {e}")
            return []
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update project fields."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                
                # Build update query
                fields = []
                values = []
                for key, value in kwargs.items():
                    if key in ['name', 'status', 'settings', 'word_count', 'target_words', 'metadata']:
                        fields.append(f"{key} = ?")
                        if key in ['settings', 'metadata'] and isinstance(value, dict):
                            values.append(json.dumps(value))
                        else:
                            values.append(value)
                
                if not fields:
                    return False
                
                # Always update last_modified
                fields.append("last_modified = ?")
                values.append(datetime.now().isoformat())
                values.append(project_id)
                
                query = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
                logger.debug(f"Updated project {project_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update project: {e}")
            return False
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()
                logger.info(f"Deleted project {project_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to delete project: {e}")
            return False
    
    # API usage tracking
    def log_api_usage(self, api_type: str, endpoint: str, response_time: float,
                     success: bool, status_code: int = 200, error_message: str = None,
                     tokens_used: int = 0, cost: float = 0.0, project_id: int = None,
                     request_hash: str = None) -> Optional[int]:
        """Log an API call."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO api_usage (
                        project_id, api_type, endpoint, response_time, success,
                        status_code, error_message, tokens_used, cost, timestamp, request_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (project_id, api_type, endpoint, response_time, 1 if success else 0,
                      status_code, error_message, tokens_used, cost,
                      datetime.now().isoformat(), request_hash))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to log API usage: {e}")
            return None
    
    def get_api_usage_stats(self, days: int = 30) -> Dict:
        """Get API usage statistics."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                
                # Total calls
                cursor.execute("""
                    SELECT COUNT(*) as total, SUM(cost) as total_cost, SUM(tokens_used) as total_tokens
                    FROM api_usage
                    WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
                """, (days,))
                row = cursor.fetchone()
                
                stats = {
                    'total_calls': row['total'] or 0,
                    'total_cost': row['total_cost'] or 0.0,
                    'total_tokens': row['total_tokens'] or 0
                }
                
                # By API type
                cursor.execute("""
                    SELECT api_type, COUNT(*) as count, SUM(cost) as cost, SUM(tokens_used) as tokens
                    FROM api_usage
                    WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
                    GROUP BY api_type
                """, (days,))
                stats['by_api'] = [dict(row) for row in cursor.fetchall()]
                
                return stats
        except sqlite3.Error as e:
            logger.error(f"Failed to get API usage stats: {e}")
            return {}
    
    # Cache operations
    def cache_content(self, content_type: str, content_key: str, content_value: Any,
                     project_id: int = None, ttl_days: int = 7) -> bool:
        """Cache content."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Calculate expiration
                cursor.execute("""
                    SELECT datetime(?, '+' || ? || ' days')
                """, (now, ttl_days))
                expires = cursor.fetchone()[0]
                
                # Store content
                content_str = json.dumps(content_value) if not isinstance(content_value, str) else content_value
                
                cursor.execute("""
                    INSERT OR REPLACE INTO content_cache (
                        project_id, content_type, content_key, content_value,
                        created_date, expires_date, access_count, last_accessed
                    ) VALUES (?, ?, ?, ?, ?, ?, 0, ?)
                """, (project_id, content_type, content_key, content_str, now, expires, now))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to cache content: {e}")
            return False
    
    def get_cached_content(self, content_type: str, content_key: str, project_id: int = None) -> Optional[Any]:
        """Retrieve cached content."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT content_value FROM content_cache
                    WHERE content_type = ? AND content_key = ?
                    AND datetime(expires_date) > datetime('now')
                """
                params = [content_type, content_key]
                
                if project_id is not None:
                    query += " AND project_id = ?"
                    params.append(project_id)
                
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                if row:
                    # Update access count
                    cursor.execute("""
                        UPDATE content_cache
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE content_type = ? AND content_key = ?
                    """, (datetime.now().isoformat(), content_type, content_key))
                    conn.commit()
                    
                    try:
                        return json.loads(row['content_value'])
                    except json.JSONDecodeError:
                        return row['content_value']
                
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get cached content: {e}")
            return None
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM content_cache
                    WHERE datetime(expires_date) <= datetime('now')
                """)
                conn.commit()
                deleted = cursor.rowcount
                logger.info(f"Cleared {deleted} expired cache entries")
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Failed to clear expired cache: {e}")
            return 0
    
    # Writing session operations
    def start_session(self, project_id: int, session_type: str = 'writing') -> Optional[int]:
        """Start a new writing session."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO writing_sessions (project_id, start_time, session_type)
                    VALUES (?, ?, ?)
                """, (project_id, datetime.now().isoformat(), session_type))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to start session: {e}")
            return None
    
    def end_session(self, session_id: int, words_written: int) -> bool:
        """End a writing session."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE writing_sessions
                    SET end_time = ?, words_written = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), words_written, session_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    def get_session_stats(self, project_id: int, days: int = 30) -> Dict:
        """Get session statistics."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(words_written) as total_words,
                        AVG(words_written) as avg_words
                    FROM writing_sessions
                    WHERE project_id = ?
                    AND datetime(start_time) >= datetime('now', '-' || ? || ' days')
                """, (project_id, days))
                row = cursor.fetchone()
                return dict(row) if row else {}
        except sqlite3.Error as e:
            logger.error(f"Failed to get session stats: {e}")
            return {}
    
    # Maintenance operations
    def optimize_database(self):
        """Optimize database performance."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                cursor.execute("ANALYZE")
                cursor.execute("VACUUM")
                conn.commit()
                logger.info("Database optimized")
        except sqlite3.Error as e:
            logger.error(f"Failed to optimize database: {e}")
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        try:
            with PooledConnection(self.pool) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Project count
                cursor.execute("SELECT COUNT(*) FROM projects")
                stats['total_projects'] = cursor.fetchone()[0]
                
                # Cache entries
                cursor.execute("SELECT COUNT(*) FROM content_cache")
                stats['cache_entries'] = cursor.fetchone()[0]
                
                # API calls
                cursor.execute("SELECT COUNT(*) FROM api_usage")
                stats['total_api_calls'] = cursor.fetchone()[0]
                
                # Sessions
                cursor.execute("SELECT COUNT(*) FROM writing_sessions")
                stats['total_sessions'] = cursor.fetchone()[0]
                
                # Database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                stats['database_size_bytes'] = cursor.fetchone()[0]
                
                # Pool stats
                stats['connection_pool'] = self.pool.get_stats()
                
                return stats
        except sqlite3.Error as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def close(self):
        """Close database manager."""
        logger.info("Closing database manager")
        self.pool.close_all()
