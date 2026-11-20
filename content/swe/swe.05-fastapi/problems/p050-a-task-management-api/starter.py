"""TaskFlow: the task-management API of chapter section 22, in one file.

Given: settings, engine, models, schemas, security helpers, the connection manager.
Your job (see problem.md): dependencies, routers, the WebSocket route, the error envelope, the wiring."""
import base64
import hashlib
import hmac
import os
import time
from contextlib import asynccontextmanager
from enum import Enum
from typing import Annotated

import jwt
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Query, Request, Response,
                     WebSocket, WebSocketDisconnect, status)
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy import ForeignKey, UniqueConstraint, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool
from starlette.exceptions import HTTPException as StarletteHTTPException


# ---------------------------------------------------------------- settings (section 18)

class Settings(BaseModel):
    model_config = {"frozen": True}
    database_url: str = "sqlite+aiosqlite://"
    secret_key: str = Field(min_length=32)
    token_minutes: int = Field(default=15, ge=1, le=1440)

    @classmethod
    def from_env(cls, environ=None):
        if environ is None:
            environ = os.environ
        names = {"database_url": "APP_DATABASE_URL", "secret_key": "APP_SECRET_KEY",
                 "token_minutes": "APP_TOKEN_MINUTES"}
        values = {field: environ[name] for field, name in names.items() if name in environ}
        try:
            return cls.model_validate(values)
        except ValidationError as exc:
            problems = "; ".join(f"{names[e['loc'][0]]}: {e['msg']}" for e in exc.errors())
            raise RuntimeError("Invalid configuration: " + problems) from None


# ---------------------------------------------------------------- database (section 11)

def make_engine(url):
    if url in ("sqlite+aiosqlite://", "sqlite+aiosqlite:///:memory:"):
        # one shared connection, or every session would see its own empty in-memory database
        return create_async_engine(url, poolclass=StaticPool, connect_args={"check_same_thread": False})
    return create_async_engine(url)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    password_hash: Mapped[str]


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "team_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    role: Mapped[str] = mapped_column(default="member")          # "owner" or "member"


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    status: Mapped[str] = mapped_column(default="todo")
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


# ---------------------------------------------------------------- schemas (section 7)

class Status(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class UserCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    name: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()


class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserOut(Out):
    id: int
    email: str
    name: str


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class TeamOut(Out):
    id: int
    name: str


class MemberAdd(BaseModel):
    email: str


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    assignee_id: int | None = None


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    status: Status | None = None
    assignee_id: int | None = None


class TaskOut(Out):
    id: int
    title: str
    status: Status
    team_id: int
    creator_id: int
    assignee_id: int | None


class TaskPage(BaseModel):
    items: list[TaskOut]
    total: int


# ---------------------------------------------------------------- security (section 12)

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(digest).decode()


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_b64, digest_b64 = stored.split("$")
        salt, expected = base64.b64decode(salt_b64), base64.b64decode(digest_b64)
    except ValueError:
        return False
    actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(actual, expected)


def create_token(user_id: int, settings: Settings) -> str:
    now = int(time.time())
    claims = {"sub": str(user_id), "iat": now, "exp": now + settings.token_minutes * 60}
    return jwt.encode(claims, settings.secret_key, algorithm="HS256")


def decode_token(token: str, settings: Settings) -> int | None:
    try:
        return int(jwt.decode(token, settings.secret_key, algorithms=["HS256"])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


# ---------------------------------------------------------------- real time (section 15.3)

class ConnectionManager:
    def __init__(self):
        self.rooms = {}

    async def connect(self, room, websocket):
        await websocket.accept()
        self.rooms.setdefault(room, []).append(websocket)

    def disconnect(self, room, websocket):
        sockets = self.rooms.get(room, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets:
            self.rooms.pop(room, None)

    async def broadcast(self, room, message):
        for connection in list(self.rooms.get(room, [])):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(room, connection)


def team_room(team_id: int) -> str:
    return f"team-{team_id}"


# ---------------------------------------------------------------- TODO: dependencies (sections 9, 12.3, 22 step 4)
# get_session(request), get_settings(request), get_manager(request), oauth2_scheme,
# user_from_token, current_user, find_membership, team_member (404 for outsiders), team_owner (403)


# ---------------------------------------------------------------- TODO: routers (sections 17, 22 step 5)
# auth: POST /auth/register, POST /auth/login
# teams: POST /teams, GET /teams, POST /teams/{team_id}/members
# tasks: POST/GET /teams/{team_id}/tasks, GET/PATCH/DELETE /teams/{team_id}/tasks/{task_id}
# realtime: WebSocket /ws/teams/{team_id}?token=...


# ---------------------------------------------------------------- TODO: one error envelope (section 8.2)
# {"error": {"code": ..., "message": ...}} for every HTTPException (starlette's class),
# plus "details" for validation errors (status 422, code "validation_failed")


# ---------------------------------------------------------------- the factory (section 22, step 6)

def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = make_engine(settings.database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        app.state.settings = settings
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        app.state.manager = ConnectionManager()
        yield
        await engine.dispose()

    app = FastAPI(title="TaskFlow", version="1.0.0", lifespan=lifespan)
    # TODO: exception handlers and include_router for every router

    @app.get("/health", tags=["meta"])
    async def health():
        return {"status": "ok"}

    return app
