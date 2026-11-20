from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Session, SQLModel, create_engine, select


# TODO: split into TaskBase, Task (table), TaskCreate (input, no id), TaskRead (output, with id)
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    priority: int = 3


class TaskCreate(SQLModel):
    pass


class TaskRead(SQLModel):
    pass


def create_app() -> FastAPI:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    app = FastAPI()

    def get_session():
        with Session(engine) as session:
            yield session

    SessionDep = Annotated[Session, Depends(get_session)]

    @app.post("/tasks", status_code=201)
    def create_task(data: Task, session: SessionDep):          # the client's id is accepted: a bug
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @app.get("/tasks")
    def list_tasks(session: SessionDep):
        return session.exec(select(Task).order_by(Task.id)).all()

    @app.get("/tasks/{task_id}")
    def get_task(task_id: int, session: SessionDep):
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        return task

    return app
