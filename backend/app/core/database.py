"""
Database configuration - SQLAlchemy Async + Supabase
Production-ready with connection pooling and health checks
"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Async Engine with production pooling
, pool_pre_ping=True,
    settings.DATABASE_URL,
    poolclass=NullPool,
    isolation_level="AUTOCOMMIT",
   connect_args={"ssl": "require", "statement_cache_size": 0},
 echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting DB session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create tables if not exists"""
    try:
        async with engine.begin() as conn:
            # Import models to ensure they are registered
            from app.models import user, office, employee, target, audit, notification  # noqa
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_created")
    except Exception as e:
        logger.warning("init_db_skipped_or_failed", error=str(e), reason="Will use existing tables or Supabase directly")
        # In production with Supabase, tables are managed via Supabase dashboard / migrations


async def close_db() -> None:
    """Close database connections"""
    await engine.dispose()
    logger.info("database_connections_closed")


async def health_check_db() -> dict:
    """Check database health"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1 as health"))
            row = result.fetchone()
            return {"status": "healthy", "response": row[0] if row else None}
    except Exception as e:
        logger.error("db_health_check_failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


# Supabase client will be initialized separately in integrations
