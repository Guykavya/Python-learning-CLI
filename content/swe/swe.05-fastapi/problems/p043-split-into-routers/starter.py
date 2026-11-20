from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

TASKS = {}                                  # id -> {"id": ..., "title": ...}


def require_user(x_user: Annotated[str | None, Header()] = None):
    if not x_user:
        raise HTTPException(401, "Login required")
    return x_user


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)


# TODO: move the routes into these routers, put require_user on tasks_router, include both
meta_router = APIRouter()
tasks_router = APIRouter()

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks(user: Annotated[str, Depends(require_user)]):
    return [TASKS[i] for i in sorted(TASKS)]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):                 # BUG: forgot the login check
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    return TASKS[task_id]


@app.post("/tasks", status_code=201)
def create_task(data: TaskIn, user: Annotated[str, Depends(require_user)]):
    task = {"id": len(TASKS) + 1, "title": data.title}
    TASKS[task["id"]] = task
    return task
