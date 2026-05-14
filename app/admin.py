"""
Admin router — manage local SQL users for APM authentication.
Mount at /admin only on internal/management networks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from .models import User, UserCreate, UserRead
from .auth import create_user, hash_password

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).order_by(User.username))
    return result.scalars().all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def add_user(body: UserCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.get(User, body.username)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    return await create_user(
        session,
        body.username,
        body.password,
        full_name=body.full_name,
        email=body.email,
    )


@router.put("/{username}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    username: str, body: dict, session: AsyncSession = Depends(get_session)
):
    user = await session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(body["password"])
    await session.commit()


@router.put("/{username}/enabled", status_code=status.HTTP_204_NO_CONTENT)
async def set_enabled(
    username: str, body: dict, session: AsyncSession = Depends(get_session)
):
    user = await session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.enabled = bool(body["enabled"])
    await session.commit()


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(username: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(delete(User).where(User.username == username))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    await session.commit()
