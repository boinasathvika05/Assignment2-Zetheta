from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.schemas.user import UserCreate, UserLogin, UserRead, TokenResponse, RefreshTokenRequest
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post(
    "/register",
    response_model=APIResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    summary="Register User Account",
    description="Registers a new user account across Customer, Support Agent, Supervisor, Risk Officer, or System Admin roles."
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user_read = await auth_service.register(user_in)
    return APIResponse(
        success=True,
        message="User account registered successfully.",
        data=user_read
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate User & Issue Tokens",
    description="Authenticates credentials, manages 5-attempt security lockout, and issues JWT Access and Refresh tokens."
)
async def login(login_data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    
    auth_service = AuthService(db)
    token_resp = await auth_service.login(login_data, ip_address=ip_addr, user_agent=user_agent)
    return APIResponse(
        success=True,
        message="Authentication successful.",
        data=token_resp
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate Refresh Token",
    description="Validates active refresh token, revokes old session, and returns new access & refresh token pair."
)
async def refresh_tokens(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    token_resp = await auth_service.refresh_tokens(req.refresh_token)
    return APIResponse(
        success=True,
        message="Token refreshed successfully.",
        data=token_resp
    )


@router.post(
    "/logout",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Revoke Session & Logout",
    description="Revokes refresh token session."
)
async def logout(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    revoked = await auth_service.logout(req.refresh_token)
    return APIResponse(
        success=True,
        message="Logged out successfully." if revoked else "Session already expired or revoked.",
        data={"revoked": revoked}
    )


@router.get(
    "/me",
    response_model=APIResponse[UserRead],
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Retrieves profile and active role of currently authenticated user."
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    user_read = UserRead.model_validate(current_user)
    return APIResponse(
        success=True,
        message="User profile retrieved successfully.",
        data=user_read
    )
