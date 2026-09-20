"""
FeeAssist AI — Database Connection

Creates the SQLAlchemy engine and session factory.
get_db() is a FastAPI dependency that yields a session per request.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# psycopg3 requires postgresql+psycopg:// scheme
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # reconnect on stale connections
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
