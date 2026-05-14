from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    username = Column(String(128), primary_key=True, index=True)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(256), nullable=True)
    email = Column(String(256), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)


# ---------- Pydantic schemas ----------

class ApmAuthRequest(BaseModel):
    username: str
    password: str


class ApmAuthResponse(BaseModel):
    username: str
    authenticated: bool


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: str | None = None


class UserRead(BaseModel):
    username: str
    full_name: str | None
    email: str | None
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}
