from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# id -> {"id": int, "title": str, "done": bool, "due": date | None}
TASKS = {
    1: {"id": 1, "title": "write report", "done": False, "due": date(2026, 12, 1)},
}


class TaskPatch(BaseModel):
    # TODO: title, done and due, all optional with default None
    pass


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    return TASKS[task_id]


@app.patch("/tasks/{task_id}")
def patch_task(task_id: int, data: TaskPatch):
    # TODO: 404 for an unknown id; update only the fields the client sent; return the task
    return {}
