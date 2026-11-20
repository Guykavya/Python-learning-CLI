"""TaskFlow: the task-management API of chapter section 22, in one file."""
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


# ---------------------------------------------------------------- dependencies (sections 9, 12.3)

async def get_session(request: Request):
    async with request.app.state.sessionmaker() as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_manager(request: Request) -> ConnectionManager:
    return request.app.state.manager


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
Manager = Annotated[ConnectionManager, Depends(get_manager)]


async def user_from_token(token: str, session: AsyncSession, settings: Settings) -> User | None:
    user_id = decode_token(token, settings)
    return await session.get(User, user_id) if user_id is not None else None


async def current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session,
                       settings: Annotated[Settings, Depends(get_settings)]) -> User:
    user = await user_from_token(token, session, settings)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})
    return user


CurrentUser = Annotated[User, Depends(current_user)]


async def find_membership(session: AsyncSession, user_id: int, team_id: int) -> Membership | None:
    stmt = select(Membership).where(Membership.user_id == user_id, Membership.team_id == team_id)
    return await session.scalar(stmt)


async def team_member(team_id: int, user: CurrentUser, session: Session) -> Membership:
    membership = await find_membership(session, user.id, team_id)
    if membership is None:
        raise HTTPException(404, "Team not found")           # 404, not 403: do not reveal that it exists
    return membership


Member = Annotated[Membership, Depends(team_member)]


async def team_owner(membership: Member) -> Membership:
    if membership.role != "owner":
        raise HTTPException(403, "Only the team owner can do this")
    return membership


Owner = Annotated[Membership, Depends(team_owner)]


# ---------------------------------------------------------------- routers (sections 17, 22)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, session: Session):
    if await session.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(409, "Email already registered")
    hashed = await run_in_threadpool(hash_password, data.password)
    user = User(email=data.email, name=data.name, password_hash=hashed)
    session.add(user)
    await session.commit()
    return user


@auth_router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, session: Session, settings: Annotated[Settings, Depends(get_settings)]):
    user = await session.scalar(select(User).where(User.email == data.email.lower()))
    ok = user is not None and await run_in_threadpool(verify_password, data.password, user.password_hash)
    if not ok:
        raise HTTPException(401, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return TokenOut(access_token=create_token(user.id, settings))


teams_router = APIRouter(prefix="/teams", tags=["teams"])


@teams_router.post("", response_model=TeamOut, status_code=201)
async def create_team(data: TeamCreate, user: CurrentUser, session: Session):
    team = Team(name=data.name)
    session.add(team)
    await session.flush()                                        # team.id without committing yet
    session.add(Membership(user_id=user.id, team_id=team.id, role="owner"))
    await session.commit()                                       # team + owner row: one transaction
    return team


@teams_router.get("", response_model=list[TeamOut])
async def my_teams(user: CurrentUser, session: Session):
    stmt = select(Team).join(Membership).where(Membership.user_id == user.id).order_by(Team.id)
    return (await session.scalars(stmt)).all()


@teams_router.post("/{team_id}/members", response_model=UserOut, status_code=201)
async def add_member(team_id: int, data: MemberAdd, owner: Owner, session: Session):
    new_user = await session.scalar(select(User).where(User.email == data.email.lower()))
    if new_user is None:
        raise HTTPException(404, "No user with that email")
    if await find_membership(session, new_user.id, team_id):
        raise HTTPException(409, "Already a member")
    session.add(Membership(user_id=new_user.id, team_id=team_id))
    await session.commit()
    return new_user


tasks_router = APIRouter(prefix="/teams/{team_id}/tasks", tags=["tasks"])


async def load_task(session: AsyncSession, team_id: int, task_id: int) -> Task:
    """Look the task up INSIDE the team from the URL: a task id from another team is a 404."""
    task = await session.scalar(select(Task).where(Task.id == task_id, Task.team_id == team_id))
    if task is None:
        raise HTTPException(404, "Task not found")
    return task


async def check_assignee(session: AsyncSession, team_id: int, assignee_id: int | None):
    if assignee_id is not None and await find_membership(session, assignee_id, team_id) is None:
        raise HTTPException(422, "assignee_id must belong to a member of this team")


@tasks_router.post("", response_model=TaskOut, status_code=201)
async def create_task(team_id: int, data: TaskCreate, member: Member, session: Session, manager: Manager):
    await check_assignee(session, team_id, data.assignee_id)
    task = Task(title=data.title, team_id=team_id, creator_id=member.user_id, assignee_id=data.assignee_id)
    session.add(task)
    await session.commit()
    out = TaskOut.model_validate(task)
    await manager.broadcast(team_room(team_id), {"event": "task.created", "task": out.model_dump(mode="json")})
    return out


@tasks_router.get("", response_model=TaskPage)
async def list_tasks(team_id: int, member: Member, session: Session,
                     status: Status | None = None,
                     limit: Annotated[int, Query(ge=1, le=100)] = 20,
                     offset: Annotated[int, Query(ge=0)] = 0):
    where = [Task.team_id == team_id] + ([Task.status == status.value] if status else [])
    total = await session.scalar(select(func.count()).select_from(Task).where(*where))
    rows = await session.scalars(select(Task).where(*where).order_by(Task.id).limit(limit).offset(offset))
    return {"items": rows.all(), "total": total}


@tasks_router.get("/{task_id}", response_model=TaskOut)
async def get_task(team_id: int, task_id: int, member: Member, session: Session):
    return await load_task(session, team_id, task_id)


@tasks_router.patch("/{task_id}", response_model=TaskOut)
async def update_task(team_id: int, task_id: int, data: TaskPatch, member: Member, session: Session,
                      manager: Manager):
    task = await load_task(session, team_id, task_id)
    changes = data.model_dump(exclude_unset=True)                # only what the client sent
    if "assignee_id" in changes:
        await check_assignee(session, team_id, changes["assignee_id"])
    for field, value in changes.items():
        setattr(task, field, value.value if isinstance(value, Status) else value)
    await session.commit()
    out = TaskOut.model_validate(task)
    await manager.broadcast(team_room(team_id), {"event": "task.updated", "task": out.model_dump(mode="json")})
    return out


@tasks_router.delete("/{task_id}", status_code=204)
async def delete_task(team_id: int, task_id: int, member: Member, session: Session, manager: Manager):
    task = await load_task(session, team_id, task_id)
    if member.role != "owner" and task.creator_id != member.user_id:
        raise HTTPException(403, "Only the team owner or the task's creator can delete it")
    await session.delete(task)
    await session.commit()
    await manager.broadcast(team_room(team_id), {"event": "task.deleted", "task_id": task_id})
    return Response(status_code=204)


ws_router = APIRouter(tags=["realtime"])


@ws_router.websocket("/ws/teams/{team_id}")
async def team_socket(websocket: WebSocket, team_id: int, token: str = ""):
    state = websocket.app.state
    async with state.sessionmaker() as session:                  # short-lived: closed before listening
        user = await user_from_token(token, session, state.settings)
        allowed = user is not None and await find_membership(session, user.id, team_id) is not None
    if not allowed:
        await websocket.close(code=1008)                         # policy violation: never accepted
        return
    room = team_room(team_id)
    await state.manager.connect(room, websocket)
    try:
        while True:
            await websocket.receive_text()                       # ignore client chatter
    except WebSocketDisconnect:
        state.manager.disconnect(room, websocket)


# ---------------------------------------------------------------- one error envelope (section 8.2)

ERROR_CODES = {400: "bad_request", 401: "unauthorized", 403: "forbidden", 404: "not_found",
               405: "method_not_allowed", 409: "conflict", 422: "validation_failed"}


def envelope(status_code, code, message, details=None, headers=None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(body, status_code=status_code, headers=headers)


async def http_error(request: Request, exc: StarletteHTTPException):
    code = ERROR_CODES.get(exc.status_code, "http_error")
    return envelope(exc.status_code, code, str(exc.detail), headers=getattr(exc, "headers", None))


async def validation_error(request: Request, exc: RequestValidationError):
    details = [{"loc": list(e["loc"]), "type": e["type"], "msg": e["msg"]} for e in exc.errors()]
    return envelope(422, "validation_failed", "Request data is invalid", details)


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
    app.add_exception_handler(StarletteHTTPException, http_error)
    app.add_exception_handler(RequestValidationError, validation_error)
    for router in (auth_router, teams_router, tasks_router, ws_router):
        app.include_router(router)

    @app.get("/health", tags=["meta"])
    async def health():
        return {"status": "ok"}

    return app
