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
    async with request.app.state.sessionmaker() as session:    # closed when the request is done
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]


def create_app(database_url: str) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_async_engine(database_url)               # startup: nothing touched the database before this
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        yield                                                    # the app serves requests here
        await engine.dispose()                                   # shutdown: close all connections

    app = FastAPI(lifespan=lifespan)

    @app.post("/tasks", response_model=TaskOut, status_code=201)
    async def create_task(data: TaskIn, session: Session):
        task = Task(title=data.title, done=data.done)
        session.add(task)
        await session.commit()
        return task

    @app.get("/tasks", response_model=list[TaskOut])
    async def list_tasks(session: Session):
        result = await session.execute(select(Task).order_by(Task.id))
        return result.scalars().all()

    @app.get("/tasks/{task_id}", response_model=TaskOut)
    async def get_task(task_id: int, session: Session):
        task = await session.get(Task, task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        return task

    return app
