import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database import get_session
from app.models import Base
from app.auth import create_user

TEST_DB = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DB)
TestSession = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_session():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as session:
        await create_user(session, "alice", "secret", full_name="Alice")
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_post_auth_success(client):
    r = await client.post("/auth", json={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    assert r.json()["authenticated"] is True


@pytest.mark.asyncio
async def test_post_auth_wrong_password(client):
    r = await client.post("/auth", json={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_post_auth_unknown_user(client):
    r = await client.post("/auth", json={"username": "nobody", "password": "x"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_basic_auth_success(client):
    r = await client.get("/auth/basic", auth=("alice", "secret"))
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_basic_auth_fail(client):
    r = await client.get("/auth/basic", auth=("alice", "bad"))
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_admin_create_and_auth(client):
    r = await client.post("/admin/users", json={"username": "bob", "password": "pass123"})
    assert r.status_code == 201

    r = await client.post("/auth", json={"username": "bob", "password": "pass123"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_admin_delete_user(client):
    r = await client.delete("/admin/users/alice")
    assert r.status_code == 204

    r = await client.post("/auth", json={"username": "alice", "password": "secret"})
    assert r.status_code == 401
