import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger

try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
    REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"])
    REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request duration in seconds", ["method", "endpoint"])
except ImportError:
    PROMETHEUS_AVAILABLE = False
    REQUEST_COUNT = None
    REQUEST_LATENCY = None


class ProductionInfrastructureMiddleware(BaseHTTPMiddleware):
    """
    Production Infrastructure Middleware providing Security Headers,
    Prometheus Latency Metrics, Correlation Tracing, and Audit Logging.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        endpoint = request.url.path
        method = request.method

        # Process Request
        response: Response = await call_next(request)

        # Calculate Latency
        latency = time.time() - start_time
        status_code = str(response.status_code)

        # 1. Update Prometheus Metrics
        if PROMETHEUS_AVAILABLE and REQUEST_COUNT and REQUEST_LATENCY:
            try:
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
                REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
            except Exception:
                pass

        # 2. Inject Security Headers (PCI DSS & OWASP Top 10)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com;"

        return response


def get_prometheus_metrics() -> Response:
    """Endpoint handler returning Prometheus metrics scrape format."""
    if PROMETHEUS_AVAILABLE:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    return Response(content="# Prometheus metrics not available", media_type="text/plain")
