from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
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


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)

    participants = relationship("EventParticipant", back_populates="event")


class EventParticipant(Base):
    __tablename__ = "event_participants"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    username = Column(String(128), ForeignKey("users.username"), primary_key=True)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship("Event", back_populates="participants")
    user = relationship("User")


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


class EventParticipantRead(BaseModel):
    username: str
    registered_at: datetime

    model_config = {"from_attributes": True}
