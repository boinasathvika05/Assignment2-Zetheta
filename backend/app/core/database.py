import time
import sys
import os
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import logger
import app.models  # Ensures all models are registered with Base.metadata!
from app.models.base import Base

# Create SQLAlchemy Async Engine
db_url = settings.get_database_url()
is_testing = bool(os.getenv("PYTEST_CURRENT_TEST") or "pytest" in sys.modules)

engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
    "pool_pre_ping": True,
}
if is_testing:
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(db_url, **engine_kwargs)

# Create Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


_db_initialized = False


async def ensure_db_initialized() -> None:
    global _db_initialized
    if not _db_initialized:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            _db_initialized = True
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for FastAPI endpoint database sessions."""
    await ensure_db_initialized()
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> Dict[str, Any]:
    """
    Diagnostic health check function executing a lightweight query on the database.
    """
    start_time = time.time()
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            latency_ms = round((time.time() - start_time) * 1000, 2)
            if val == 1:
                return {"status": "healthy", "latency_ms": latency_ms, "engine": engine.dialect.name}
            return {"status": "degraded", "latency_ms": latency_ms, "error": "Unexpected query output"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "error": str(e)
        }


async def init_db() -> None:
    """Initialize database tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
