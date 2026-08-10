import time
import psutil
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.deps import get_db
from app.core.config import settings
from app.core.redis_client import check_redis_health
from app.core.vector_store import check_vector_store_health
from app.schemas.common import APIResponse

router = APIRouter()

START_TIME = time.time()


@router.get(
    "/health",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Comprehensive System Health Check",
    description="Diagnostics for PostgreSQL DB, Redis Cache, ChromaDB Vector Store, Memory usage, and Uptime."
)
async def get_system_health(db: AsyncSession = Depends(get_db)):
    # 1. Database Health Check
    db_healthy = False
    try:
        res = await db.execute(text("SELECT 1"))
        if res.scalar() == 1:
            db_healthy = True
    except Exception:
        db_healthy = False

    # 2. Redis Cache Health Check
    redis_healthy = await check_redis_health()

    # 3. Vector DB Health Check
    vector_res = await check_vector_store_health()
    vector_healthy = isinstance(vector_res, dict) and vector_res.get("status") in ["healthy", "degraded"]

    # 4. System Resource Stats
    memory = psutil.virtual_memory()
    uptime_seconds = round(time.time() - START_TIME, 2)

    overall_healthy = db_healthy

    health_data = {
        "status": "healthy" if overall_healthy else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": uptime_seconds,
        "subsystems": {
            "database": "connected" if db_healthy else "disconnected",
            "redis_cache": "connected" if redis_healthy else "disconnected",
            "vector_store": "connected" if vector_healthy else "disconnected"
        },
        "resources": {
            "memory_used_mb": round(memory.used / (1024 * 1024), 2),
            "memory_percent": memory.percent
        }
    }

    return APIResponse(
        success=overall_healthy,
        message="System operational." if overall_healthy else "Subsystems experiencing degradation.",
        data=health_data
    )
