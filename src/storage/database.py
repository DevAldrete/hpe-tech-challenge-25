"""
Database connection and session management using SQLAlchemy Async.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.storage.config import storage_config


class Database:
    """Manages database connection and session lifecycle."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def connect(self) -> None:
        """Initialize the database engine and session factory."""
        if self.engine is not None:
            return

        self.engine = create_async_engine(
            storage_config.database_url,
            pool_size=storage_config.db_pool_size,
            max_overflow=storage_config.db_max_overflow,
            echo=storage_config.db_echo,
            future=True,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def disconnect(self) -> None:
        """Close the database engine."""
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        """Provide a transactional scope around a series of operations."""
        if self.session_factory is None:
            raise RuntimeError("Database is not connected. Call connect() first.")

        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Global database instance
db = Database()
