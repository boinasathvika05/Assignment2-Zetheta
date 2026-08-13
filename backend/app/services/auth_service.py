import uuid
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token, REFRESH_TOKEN_EXPIRE_DAYS
from app.core.enums import UserRole, AuthLevel
from app.models.user import User
from app.models.customer import CustomerProfile
from app.models.session import UserSession
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.user import UserCreate, UserLogin, UserRead, TokenResponse
from app.core.logging import logger


class AuthService:
    """
    Service layer encapsulating authentication, session management, security lockouts,
    and token rotation logic.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)

    async def register(self, user_in: UserCreate) -> UserRead:
        """Register a new user and create customer profile if role is CUSTOMER."""
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email.lower().strip(),
            password_hash=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=True
        )
        user = await self.user_repo.create(new_user)

        # If user is a CUSTOMER, create corresponding CustomerProfile entity
        if user.role == UserRole.CUSTOMER or str(user.role).upper() == "CUSTOMER":
            phone = user_in.phone_number or f"+91{str(uuid.uuid4().int)[:10]}"
            # Check if phone number already exists
            existing_profile = (await self.db.execute(
                select(CustomerProfile).where(CustomerProfile.phone_number == phone)
            )).scalar_one_or_none()
            if existing_profile:
                phone = f"+91{str(uuid.uuid4().int)[:10]}"
            
            profile = CustomerProfile(
                user_id=user.id,
                phone_number=phone,
                auth_level=AuthLevel.ANONYMOUS,
                segment="STANDARD",
                pep_flag=False
            )
            self.db.add(profile)
            await self.db.flush()

        logger.info(f"Successfully registered user: {user.email} [{user.role}]")
        return UserRead.model_validate(user)

    async def login(self, login_data: UserLogin, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        """Authenticate user credentials with security lockout & session creation."""
        user = await self.user_repo.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )

        # Check account lockout
        if user.locked_until:
            now = datetime.now(timezone.utc)
            locked_until_utc = user.locked_until.replace(tzinfo=timezone.utc) if user.locked_until.tzinfo is None else user.locked_until
            if now < locked_until_utc:
                remaining_sec = int((locked_until_utc - now).total_seconds())
                minutes = round(remaining_sec / 60, 1)
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked due to repeated failed login attempts. Please try again in {minutes} minutes."
                )
            else:
                # Lock expired, reset failed counter
                await self.user_repo.reset_failed_login(user)

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            updated_user = await self.user_repo.increment_failed_login(user)
            await self.db.commit()  # Commit incremented failed login attempt to DB before throwing exception!
            if updated_user.locked_until:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account has been locked for 15 minutes due to 5 consecutive failed login attempts."
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Reset failed login counter upon success
        await self.user_repo.reset_failed_login(user)

        # Generate tokens
        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token, jti = create_refresh_token(subject=user.id)

        # Track user session
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await self.session_repo.create_session(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        user_read = UserRead.model_validate(user)
        logger.info(f"User logged in successfully: {user.email}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in_seconds=1800,
            user=user_read
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Perform token rotation: validate refresh token, revoke old session, issue new tokens."""
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type."
            )

        user_id = payload.get("sub")
        jti = payload.get("jti")

        # Verify session in DB
        session = await self.session_repo.get_by_jti(jti)
        if not session or session.is_revoked:
            # Possible token reuse attack! Revoke all user sessions for safety.
            if user_id:
                await self.session_repo.revoke_all_user_sessions(user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or reused."
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User inactive or not found."
            )

        # Revoke old session (Token Rotation)
        await self.session_repo.revoke_session(jti)

        # Issue new pair
        new_access_token = create_access_token(subject=user.id, role=user.role)
        new_refresh_token, new_jti = create_refresh_token(subject=user.id)

        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await self.session_repo.create_session(
            user_id=user.id,
            jti=new_jti,
            expires_at=expires_at
        )

        user_read = UserRead.model_validate(user)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in_seconds=1800,
            user=user_read
        )

    async def logout(self, refresh_token: str) -> bool:
        """Logout user by revoking their refresh session."""
        try:
            payload = decode_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                await self.session_repo.revoke_session(jti)
                logger.info(f"Session revoked for jti: {jti}")
                return True
        except Exception:
            pass
        return False
