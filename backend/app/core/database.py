"""
Database engine and session management.
Uses async SQLAlchemy with aiosqlite driver.
"""

import os
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _get_database_url() -> str:
    """Resolve the DATABASE_URL to use an absolute path for SQLite."""
    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        # Extract the file path from the URL (after sqlite+aiosqlite:///)
        prefix = url.split("///")[0] + "///"
        db_path = url.split("///")[1]
        if not os.path.isabs(db_path):
            # Make relative paths absolute based on this file's directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, db_path.lstrip("./"))
        return f"{prefix}{db_path}"
    return url


# Async engine for SQLite — NullPool creates fresh connections each time
engine = create_async_engine(
    _get_database_url(),
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable WAL journal mode and foreign keys for SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async DB session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

