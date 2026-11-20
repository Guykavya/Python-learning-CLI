from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    done: bool = False


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    done: bool


async def get_session(request: Request):
    # TODO: open a session from request.app.state.sessionmaker and yield it
    yield None


Session = Annotated[AsyncSession, Depends(get_session)]


def create_app(database_url: str) -> FastAPI:
    # TODO: a lifespan that creates the engine and the tables, stores the session
    #       factory in app.state.sessionmaker, and disposes the engine at shutdown.
    app = FastAPI()

    @app.post("/tasks", response_model=TaskOut, status_code=201)
    async def create_task(data: TaskIn, session: Session):
        return {"id": 0, "title": data.title, "done": data.done}

    @app.get("/tasks", response_model=list[TaskOut])
    async def list_tasks(session: Session):
        return []

    @app.get("/tasks/{task_id}", response_model=TaskOut)
    async def get_task(task_id: int, session: Session):
        raise HTTPException(404, "Task not found")

    return app
