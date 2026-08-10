from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User
from app.repositories.base import BaseRepository

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class UserRepository(BaseRepository[User]):
    """
    User entity repository managing user queries, login failure counters, and security lockouts.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find active user by email address."""
        stmt = select(User).where(User.email == email.lower().strip(), User.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def increment_failed_login(self, user: User) -> User:
        """
        Increments failed login counter and locks account if failed attempts exceed threshold (5).
        """
        attempts = user.failed_login_attempts + 1
        locked_until = None
        if attempts >= MAX_FAILED_ATTEMPTS:
            locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

        user.failed_login_attempts = attempts
        user.locked_until = locked_until
        self.db.add(user)
        await self.db.flush()
        return user

    async def reset_failed_login(self, user: User) -> User:
        """Resets failed login attempts and clears lockout timer upon successful authentication."""
        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.add(user)
        await self.db.flush()
        return user
