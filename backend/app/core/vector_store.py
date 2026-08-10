import os
import time
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

_chroma_client: Optional[Any] = None
_chroma_collection: Optional[Any] = None


def get_vector_store():
    """
    Get or initialize the persistent ChromaDB client and default collection.
    """
    global _chroma_client, _chroma_collection
    if not HAS_CHROMADB:
        logger.warning("ChromaDB is not installed in environment.")
        return None, None

    if _chroma_client is None:
        try:
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            _chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
            )
            _chroma_collection = _chroma_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized ChromaDB collection: {settings.CHROMA_COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB vector store: {str(e)}")
            return None, None
    return _chroma_client, _chroma_collection


async def check_vector_store_health() -> Dict[str, Any]:
    """
    Diagnostic health check function verifying vector database operational state.
    """
    start_time = time.time()
    try:
        client, collection = get_vector_store()
        latency_ms = round((time.time() - start_time) * 1000, 2)
        if client is not None and collection is not None:
            count = collection.count()
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "document_count": count
            }
        return {
            "status": "degraded",
            "latency_ms": latency_ms,
            "error": "Vector store running in memory/mock fallback mode"
        }
    except Exception as e:
        logger.error(f"Vector store health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "error": str(e)
        }
