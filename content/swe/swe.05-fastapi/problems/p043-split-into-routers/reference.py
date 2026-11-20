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


meta_router = APIRouter(tags=["meta"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_user)])


@meta_router.get("/health")
def health():
    return {"status": "ok"}


@tasks_router.get("")
def list_tasks():
    return [TASKS[i] for i in sorted(TASKS)]


@tasks_router.get("/{task_id}")
def get_task(task_id: int):                 # protected by the router's dependency
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    return TASKS[task_id]


@tasks_router.post("", status_code=201)
def create_task(data: TaskIn):
    task = {"id": len(TASKS) + 1, "title": data.title}
    TASKS[task["id"]] = task
    return task


app = FastAPI()
app.include_router(meta_router)
app.include_router(tasks_router, prefix="/api")      # prefixes add up: /api/tasks
