from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.session import UserSession
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[UserSession]):
    """
    Session Repository managing refresh tokens, token rotation, and token revocation.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(UserSession, db)

    async def get_by_jti(self, jti: str) -> Optional[UserSession]:
        """Fetch active session by JWT ID (jti)."""
        stmt = select(UserSession).where(UserSession.refresh_token_jti == jti, UserSession.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_session(
        self,
        user_id: str,
        jti: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create new active user session."""
        session = UserSession(
            user_id=user_id,
            refresh_token_jti=jti,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            is_revoked=False
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def revoke_session(self, jti: str) -> bool:
        """Revoke session by jti."""
        stmt = update(UserSession).where(UserSession.refresh_token_jti == jti).values(is_revoked=True)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a specific user (e.g. on security breach or logout)."""
        stmt = update(UserSession).where(UserSession.user_id == user_id, UserSession.is_revoked == False).values(is_revoked=True)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
