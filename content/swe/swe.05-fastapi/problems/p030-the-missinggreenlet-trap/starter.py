from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    tags: Mapped[list["Tag"]] = relationship(back_populates="task", order_by="Tag.id")


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    task: Mapped[Task] = relationship(back_populates="tags")


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    tags: list[TagOut]


class TaskIn(BaseModel):
    title: str = Field(min_length=1)
    tags: list[str] = []


class TagIn(BaseModel):
    name: str = Field(min_length=1)


async def get_session(request: Request):
    async with request.app.state.sessionmaker() as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]


def create_app(database_url: str) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_async_engine(database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        yield
        await engine.dispose()

    app = FastAPI(lifespan=lifespan)

    @app.post("/tasks", response_model=TaskOut, status_code=201)
    async def create_task(data: TaskIn, session: Session):
        task = Task(title=data.title, tags=[Tag(name=name) for name in data.tags])
        session.add(task)
        await session.commit()
        return task                       # fine: the tags were set in Python, nothing to load

    @app.get("/tasks", response_model=list[TaskOut])
    async def list_tasks(session: Session):
        result = await session.execute(select(Task).order_by(Task.id))          # BUG: tags not loaded
        return result.scalars().all()

    @app.get("/tasks/{task_id}", response_model=TaskOut)
    async def get_task(task_id: int, session: Session):
        task = await session.get(Task, task_id)                                 # BUG: tags not loaded
        if task is None:
            raise HTTPException(404, "Task not found")
        return task

    @app.post("/tasks/{task_id}/tags", response_model=TaskOut, status_code=201)
    async def add_tag(task_id: int, data: TagIn, session: Session):
        task = await session.get(Task, task_id)                                 # BUG: tags not loaded
        if task is None:
            raise HTTPException(404, "Task not found")
        task.tags.append(Tag(name=data.name))
        await session.commit()
        return task

    return app
