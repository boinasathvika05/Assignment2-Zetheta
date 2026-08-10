import time
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

redis_pool: Optional[aioredis.Redis] = None


async def get_redis_client() -> Optional[aioredis.Redis]:
    """Get or initialize the global async Redis client."""
    global redis_pool
    if redis_pool is None:
        try:
            redis_pool = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Redis pool: {str(e)}")
            return None
    return redis_pool


async def check_redis_health() -> Dict[str, Any]:
    """
    Diagnostic health check function executing a ping against Redis.
    """
    start_time = time.time()
    try:
        client = await get_redis_client()
        if client is None:
            return {"status": "unhealthy", "latency_ms": 0.0, "error": "Redis client not initialized"}
        pong = await client.ping()
        latency_ms = round((time.time() - start_time) * 1000, 2)
        if pong:
            return {"status": "healthy", "latency_ms": latency_ms}
        return {"status": "degraded", "latency_ms": latency_ms, "error": "No PONG response"}
    except Exception as e:
        logger.warning(f"Redis health check failed (optional component for local dev): {str(e)}")
        return {
            "status": "degraded",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "error": str(e)
        }
