import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session, init_db
from .auth import authenticate_user
from .models import ApmAuthRequest, ApmAuthResponse, Event, EventParticipant, EventParticipantRead
from .admin import router as admin_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBasic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="F5 APM SQL Auth Service",
    description="HTTP authentication backend for F5 Access Policy Manager backed by a SQL database",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(admin_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/auth", response_model=ApmAuthResponse)
async def apm_auth_post(
    request: ApmAuthRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    JSON auth endpoint for F5 APM HTTP Auth agent (POST body).
    APM sends { "username": "...", "password": "..." }.
    Returns 200 on success, 401 on failure.
    """
    ok = await authenticate_user(session, request.username, request.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    logger.info("APM auth success for user=%s", request.username)
    return ApmAuthResponse(username=request.username, authenticated=True)


@app.get("/auth/basic")
async def apm_auth_basic(
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    """
    HTTP Basic Auth endpoint for F5 APM HTTP Auth agent.
    Returns 200 on success, 401 on failure.
    """
    ok = await authenticate_user(session, credentials.username, credentials.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    logger.info("APM basic auth success for user=%s", credentials.username)
    return {"username": credentials.username, "authenticated": True}


@app.get("/events/{event_id}/participants", response_model=list[EventParticipantRead])
async def get_event_participants(
    event_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Return all participants registered for a given event.
    """
    event_result = await session.execute(select(Event).where(Event.id == event_id))
    if event_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    result = await session.execute(
        select(EventParticipant).where(EventParticipant.event_id == event_id)
    )
    return result.scalars().all()
