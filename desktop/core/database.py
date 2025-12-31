"""
Database management for the desktop application.
Uses SQLAlchemy with standalone configuration (no Flask).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

# Base class for all models
Base = declarative_base()

# Global database instance
_db_instance: Optional['Database'] = None


class Database:
    """
    Database manager for SQLAlchemy without Flask.
    Provides session management and connection handling.
    """
    
    def __init__(self, db_path: str = 'data/bass_practice.db'):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Ensure data directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Create engine
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            connect_args={'check_same_thread': False}
        )
        
        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def close_session(self):
        """Close the current session."""
        self.Session.remove()
    
    def execute(self, query):
        """Execute a raw SQL query."""
        with self.engine.connect() as conn:
            return conn.execute(query)


def init_db(db_path: str = 'data/bass_practice.db') -> Database:
    """
    Initialize the global database instance.
    
    Args:
        db_path: Path to SQLite database file
    
    Returns:
        Database instance
    """
    global _db_instance
    _db_instance = Database(db_path)
    _db_instance.create_tables()
    return _db_instance


def get_db() -> Database:
    """
    Get the global database instance.
    Initializes if not already done.
    
    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = init_db()
    return _db_instance


def get_session():
    """Get a database session from the global instance."""
    return get_db().get_session()
