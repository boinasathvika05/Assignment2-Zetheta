import logging
import sys
from contextvars import ContextVar
from typing import Optional
from rich.logging import RichHandler

correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def set_correlation_id(correlation_id: str) -> None:
    correlation_id_ctx.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    return correlation_id_ctx.get()


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id() or "NO_CORRELATION_ID"
        return True


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("nexbank")
    logger.setLevel(log_level)
    logger.addFilter(CorrelationIdFilter())

    if not logger.handlers:
        handler = RichHandler(rich_tracebacks=True, show_time=True, show_path=False)
        formatter = logging.Formatter("[%(correlation_id)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
