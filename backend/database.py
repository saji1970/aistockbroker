#!/usr/bin/env python3
"""
Database Configuration and Management for AI Stock Trading Platform
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._engine = None
        self._SessionLocal = None
        self.database_url = self._get_database_url()

    def _get_database_url(self):
        """Get database URL from environment or use SQLite as fallback"""
        # Try to get from environment
        db_url = os.environ.get('DATABASE_URL')

        if db_url:
            return db_url

        # Check for individual components
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')

        if all([db_host, db_name, db_user, db_password]):
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        # Fallback to SQLite for development
        sqlite_path = os.path.join(os.path.dirname(__file__), 'trading_platform.db')
        return f"sqlite:///{sqlite_path}"

    @property
    def engine(self):
        """Get or create database engine"""
        if self._engine is None:
            if self.database_url.startswith('sqlite'):
                # SQLite specific configuration
                self._engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    },
                    echo=False
                )
            else:
                # PostgreSQL configuration
                self._engine = create_engine(
                    self.database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=False
                )
        return self._engine

    @property
    def SessionLocal(self):
        """Get session factory"""
        if self._SessionLocal is None:
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        return self._SessionLocal

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_session_sync(self) -> Session:
        """Get a synchronous database session (remember to close it!)"""
        return self.SessionLocal()

    def health_check(self):
        """Check database connectivity"""
        try:
            from sqlalchemy import text
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

def get_db():
    """Dependency injection for FastAPI/Flask routes"""
    db = db_manager.get_session_sync()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database - create tables"""
    try:
        db_manager.create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    print("Database initialized successfully!")