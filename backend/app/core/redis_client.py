import time
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    aioredis = None

redis_pool: Optional[Any] = None
_redis_disabled: bool = False


async def get_redis_client() -> Optional[Any]:
    """Get or initialize the global async Redis client."""
    global redis_pool, _redis_disabled
    if not HAS_REDIS or _redis_disabled:
        return None

    if redis_pool is None:
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=0.1,
                socket_connect_timeout=0.1
            )
            await client.ping()
            redis_pool = client
        except Exception as e:
            logger.warning(f"Redis unavailable (operating in memory/DB fallback mode): {str(e)}")
            _redis_disabled = True
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
