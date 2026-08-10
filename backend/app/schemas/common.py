from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field

DataType = TypeVar("DataType")


class APIResponse(BaseModel, Generic[DataType]):
    """Standardized API Response Envelope for all endpoints."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[DataType] = None
    error: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel, Generic[DataType]):
    """Standardized Paginated List Response."""
    items: List[DataType]
    total: int
    page: int
    size: int
    pages: int
