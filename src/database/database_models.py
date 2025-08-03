"""
Database management modules for FANWS
Contains database connection, pooling, and management functionality
"""

from .database_manager import DatabaseManager

__all__ = [
    'DatabaseManager'
]
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.exc import SQLAlchemyError
import os

logger = logging.getLogger(__name__)

Base = declarative_base()

class WorkflowVersion(Base):
    """Model for tracking workflow versions and conflicts"""
    __tablename__ = 'workflow_versions'

    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), nullable=False, index=True)
    project_name = Column(String(100), nullable=False)
    version_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), default='local_user')
    workflow_data = Column(JSON)
    checksum = Column(String(64))  # SHA256 hash
    is_active = Column(Boolean, default=True)
    parent_version = Column(Integer, nullable=True)
    conflict_resolved = Column(Boolean, default=False)
    resolution_strategy = Column(String(50), nullable=True)  # 'merge', 'override', 'manual'

class ApiCache(Base):
    """Model for API response caching"""
    __tablename__ = 'api_cache'

    id = Column(Integer, primary_key=True)
    cache_key = Column(String(64), unique=True, nullable=False, index=True)
    response_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    hit_count = Column(Integer, default=0)
    compressed = Column(Boolean, default=False)

class ProjectMetadata(Base):
    """Model for project metadata and collaboration info"""
    __tablename__ = 'project_metadata'

    id = Column(Integer, primary_key=True)
    project_name = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    active_users = Column(JSON, default=list)  # List of active users
    settings = Column(JSON, default=dict)
    collaboration_enabled = Column(Boolean, default=False)
    version_conflict_strategy = Column(String(50), default='prompt')  # 'prompt', 'auto_merge', 'manual'

class DatabaseManager:
    """Enhanced database manager with SQLAlchemy connection pooling"""

    def __init__(self, database_url: Optional[str] = None, pool_size: int = 5, max_overflow: int = 10):
        """
        Initialize database manager with connection pooling

        Args:
            database_url: Database URL (defaults to SQLite)
            pool_size: Number of connections to maintain in pool
            max_overflow: Maximum overflow connections beyond pool_size
        """
        if database_url is None:
            # Default to SQLite with WAL mode for better concurrency
            db_path = os.path.join(os.getcwd(), 'fanws.db')
            database_url = f'sqlite:///{db_path}?check_same_thread=False'

        self.database_url = database_url
        self._engine = None
        self._session_factory = None
        self._scoped_session = None
        self._lock = threading.RLock()

        # Configure engine based on database type
        if database_url.startswith('sqlite'):
            # SQLite configuration for single-file database
            self._engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={
                    'check_same_thread': False,
                    'timeout': 30,
                    'isolation_level': None  # Enable autocommit mode
                },
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600    # Recycle connections every hour
            )
        else:
            # PostgreSQL/MySQL configuration with connection pooling
            self._engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )

        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine)
        self._scoped_session = scoped_session(self._session_factory)

        # Initialize database
        self._init_database()

        logger.info(f"Database manager initialized with {database_url}")

    def _init_database(self):
        """Initialize database tables"""
        try:
            # Create all tables
            Base.metadata.create_all(self._engine)

            # Enable SQLite optimizations if using SQLite
            if self.database_url.startswith('sqlite'):
                with self._engine.connect() as conn:
                    # Enable WAL mode for better concurrency
                    conn.execute(text("PRAGMA journal_mode=WAL"))
                    # Optimize SQLite settings
                    conn.execute(text("PRAGMA synchronous=NORMAL"))
                    conn.execute(text("PRAGMA cache_size=10000"))
                    conn.execute(text("PRAGMA temp_store=MEMORY"))
                    conn.execute(text("PRAGMA mmap_size=268435456"))  # 256MB

            logger.info("Database tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_session(self) -> Session:
        """Get a database session from the pool"""
        return self._scoped_session()

    def close_session(self):
        """Close the current scoped session"""
        self._scoped_session.remove()

    def execute_with_retry(self, operation, max_retries: int = 3):
        """Execute database operation with retry logic"""
        for attempt in range(max_retries):
            try:
                session = self.get_session()
                try:
                    result = operation(session)
                    session.commit()
                    return result
                except Exception as e:
                    session.rollback()
                    raise
                finally:
                    session.close()
            except SQLAlchemyError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Database operation failed (attempt {attempt + 1}), retrying: {e}")

    def create_workflow_version(self, workflow_id: str, project_name: str,
                               workflow_data: Dict[str, Any], created_by: str = 'local_user') -> int:
        """Create a new workflow version with conflict detection"""
        def operation(session: Session):
            # Get the latest version number
            latest_version = session.query(WorkflowVersion)\
                .filter_by(workflow_id=workflow_id, project_name=project_name)\
                .order_by(WorkflowVersion.version_number.desc())\
                .first()

            next_version = (latest_version.version_number + 1) if latest_version else 1

            # Calculate checksum for conflict detection
            import hashlib
            import json
            checksum = hashlib.sha256(
                json.dumps(workflow_data, sort_keys=True).encode()
            ).hexdigest()

            # Create new version
            version = WorkflowVersion(
                workflow_id=workflow_id,
                project_name=project_name,
                version_number=next_version,
                created_by=created_by,
                workflow_data=workflow_data,
                checksum=checksum,
                parent_version=latest_version.version_number if latest_version else None
            )

            session.add(version)
            session.flush()
            return version.version_number

        return self.execute_with_retry(operation)

    def get_workflow_versions(self, workflow_id: str, project_name: str) -> List[Dict[str, Any]]:
        """Get all versions of a workflow"""
        def operation(session: Session):
            versions = session.query(WorkflowVersion)\
                .filter_by(workflow_id=workflow_id, project_name=project_name)\
                .order_by(WorkflowVersion.version_number.desc())\
                .all()

            return [{
                'version_number': v.version_number,
                'created_at': v.created_at.isoformat(),
                'modified_at': v.modified_at.isoformat(),
                'created_by': v.created_by,
                'checksum': v.checksum,
                'is_active': v.is_active,
                'conflict_resolved': v.conflict_resolved,
                'workflow_data': v.workflow_data
            } for v in versions]

        return self.execute_with_retry(operation)

    def detect_version_conflicts(self, workflow_id: str, project_name: str,
                                current_checksum: str) -> List[Dict[str, Any]]:
        """Detect version conflicts based on timestamps and checksums"""
        def operation(session: Session):
            # Get all active versions that might conflict
            recent_versions = session.query(WorkflowVersion)\
                .filter_by(workflow_id=workflow_id, project_name=project_name, is_active=True)\
                .filter(WorkflowVersion.checksum != current_checksum)\
                .order_by(WorkflowVersion.modified_at.desc())\
                .limit(10)\
                .all()

            conflicts = []
            for version in recent_versions:
                # Check if this version was modified recently (within last hour)
                time_diff = datetime.utcnow() - version.modified_at
                if time_diff.total_seconds() < 3600:  # 1 hour
                    conflicts.append({
                        'version_number': version.version_number,
                        'modified_at': version.modified_at.isoformat(),
                        'created_by': version.created_by,
                        'checksum': version.checksum,
                        'time_since_modification': time_diff.total_seconds()
                    })

            return conflicts

        return self.execute_with_retry(operation)

    def resolve_version_conflict(self, workflow_id: str, project_name: str,
                                version_number: int, resolution_strategy: str) -> bool:
        """Mark a version conflict as resolved"""
        def operation(session: Session):
            version = session.query(WorkflowVersion)\
                .filter_by(
                    workflow_id=workflow_id,
                    project_name=project_name,
                    version_number=version_number
                ).first()

            if version:
                version.conflict_resolved = True
                version.resolution_strategy = resolution_strategy
                version.modified_at = datetime.utcnow()
                return True
            return False

        return self.execute_with_retry(operation)

    def update_project_metadata(self, project_name: str, metadata: Dict[str, Any]) -> bool:
        """Update project metadata for collaboration tracking"""
        def operation(session: Session):
            project = session.query(ProjectMetadata)\
                .filter_by(project_name=project_name).first()

            if not project:
                project = ProjectMetadata(
                    project_name=project_name,
                    settings=metadata
                )
                session.add(project)
            else:
                project.settings.update(metadata)
                project.modified_at = datetime.utcnow()

            session.flush()
            return True

        return self.execute_with_retry(operation)

    def add_active_user(self, project_name: str, user_id: str) -> bool:
        """Add user to active users list for collaboration"""
        def operation(session: Session):
            project = session.query(ProjectMetadata)\
                .filter_by(project_name=project_name).first()

            if not project:
                project = ProjectMetadata(
                    project_name=project_name,
                    active_users=[user_id],
                    collaboration_enabled=True
                )
                session.add(project)
            else:
                if user_id not in project.active_users:
                    project.active_users.append(user_id)
                    project.modified_at = datetime.utcnow()

            session.flush()
            return True

        return self.execute_with_retry(operation)

    def remove_active_user(self, project_name: str, user_id: str) -> bool:
        """Remove user from active users list"""
        def operation(session: Session):
            project = session.query(ProjectMetadata)\
                .filter_by(project_name=project_name).first()

            if project and user_id in project.active_users:
                project.active_users.remove(user_id)
                project.modified_at = datetime.utcnow()
                session.flush()
                return True
            return False

        return self.execute_with_retry(operation)

    def get_active_users(self, project_name: str) -> List[str]:
        """Get list of active users for a project"""
        def operation(session: Session):
            project = session.query(ProjectMetadata)\
                .filter_by(project_name=project_name).first()

            return project.active_users if project else []

        return self.execute_with_retry(operation)

    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        def operation(session: Session):
            current_time = datetime.utcnow()
            expired_count = session.query(ApiCache)\
                .filter(ApiCache.expires_at < current_time)\
                .delete()

            logger.info(f"Cleaned up {expired_count} expired cache entries")
            return expired_count

        return self.execute_with_retry(operation)

    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        return {
            'database_url': self.database_url,
            'engine_info': str(self._engine),
            'pool_size': getattr(self._engine.pool, 'size', 'N/A'),
            'checked_out_connections': getattr(self._engine.pool, 'checkedout', 'N/A'),
            'overflow_connections': getattr(self._engine.pool, 'overflow', 'N/A'),
            'invalidated_connections': getattr(self._engine.pool, 'invalidated', 'N/A')
        }

    def close(self):
        """Close all database connections"""
        try:
            self._scoped_session.remove()
            if self._engine:
                self._engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Global database manager instance
_db_manager = None

def get_database_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager

def close_database_connections():
    """Close all database connections"""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None
