import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger, set_correlation_id
from app.core.middleware import ProductionInfrastructureMiddleware, get_prometheus_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    logger.info("Initializing NexBank Agentic AI Customer Service Core System...")
    logger.info(f"Loaded environment parameters from settings (Env: {settings.ENVIRONMENT})")
    
    # Initialize DB tables
    try:
        await init_db()
        logger.info("PostgreSQL Database schema initialized.")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")

    yield

    # Shutdown Sequence
    logger.info("Shutting down NexBank Agentic AI Core System gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade Agentic AI Customer Service Platform with Hybrid RAG & Real-Time Governance for NexBank.",
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Custom Infrastructure Middleware
app.add_middleware(ProductionInfrastructureMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
    set_correlation_id(correlation_id)
    
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} [{duration_ms}ms]"
    )
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected enterprise system error occurred. Please contact NexBank operations.",
                "details": str(exc) if settings.ENVIRONMENT == "development" else None
            }
        }
    )


# Prometheus Scrape Endpoint
@app.get("/metrics", include_in_schema=False)
async def metrics_endpoint():
    return get_prometheus_metrics()


# Mount API Router (Multiple prefixes for Vercel Serverless rewrite routing compatibility)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(api_router, prefix="/v1")
app.include_router(api_router, prefix="/api")

# Health Check Root Endpoints
@app.get("/health", tags=["Health"])
async def root_health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Serve Frontend Dashboard
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/public"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
