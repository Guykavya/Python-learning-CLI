from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Session, SQLModel, create_engine, select


class TaskBase(SQLModel):                              # shared fields with their rules; no table
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=3, ge=1, le=5)


class Task(TaskBase, table=True):                      # the table
    id: int | None = Field(default=None, primary_key=True)


class TaskCreate(TaskBase):                            # input: no id, so a client cannot choose one
    pass


class TaskRead(TaskBase):                              # output: the id is always there
    id: int


def create_app() -> FastAPI:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    app = FastAPI()

    def get_session():
        with Session(engine) as session:
            yield session

    SessionDep = Annotated[Session, Depends(get_session)]

    @app.post("/tasks", response_model=TaskRead, status_code=201)
    def create_task(data: TaskCreate, session: SessionDep):
        task = Task.model_validate(data)               # copies title and priority; id stays None
        session.add(task)
        session.commit()
        session.refresh(task)                          # now task.id is set by the database
        return task

    @app.get("/tasks", response_model=list[TaskRead])
    def list_tasks(session: SessionDep):
        return session.exec(select(Task).order_by(Task.id)).all()

    @app.get("/tasks/{task_id}", response_model=TaskRead)
    def get_task(task_id: int, session: SessionDep):
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        return task

    return app
