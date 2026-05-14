from datetime import datetime, timezone

import bcrypt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def authenticate_user(session: AsyncSession, username: str, password: str) -> bool:
    result = await session.execute(select(User).where(User.username == username))
    user: User | None = result.scalar_one_or_none()

    if user is None or not user.enabled:
        return False

    if not verify_password(password, user.password_hash):
        return False

    await session.execute(
        update(User)
        .where(User.username == username)
        .values(last_login=datetime.now(timezone.utc))
    )
    await session.commit()
    return True


async def create_user(session: AsyncSession, username: str, password: str, **kwargs) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        **kwargs,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
