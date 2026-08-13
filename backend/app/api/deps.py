from typing import List, Callable, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.core.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_optional_user(
    token: str = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Optional dependency extracting User from JWT if present, returning None otherwise."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            return None
        user_repo = UserRepository(db)
        return await user_repo.get_by_id(user_id)
    except Exception:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency extracting and decoding JWT Access Token to return active User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency verifying user account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account."
        )
    return current_user


class RequireRole:
    """
    Role-Based Access Control (RBAC) Dependency Guard.
    Enforces that the current authenticated user possesses one of the allowed UserRoles.
    """
    def __init__(self, allowed_roles: List[Any]):
        self.allowed_roles = [r.value if hasattr(r, "value") else str(r) for r in allowed_roles]

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Action requires one of roles: {self.allowed_roles}"
            )
        return current_user

