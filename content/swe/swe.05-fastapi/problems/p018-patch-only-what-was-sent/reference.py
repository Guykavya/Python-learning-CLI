from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# id -> {"id": int, "title": str, "done": bool, "due": date | None}
TASKS = {
    1: {"id": 1, "title": "write report", "done": False, "due": date(2026, 12, 1)},
}


class TaskPatch(BaseModel):
    title: str | None = None
    done: bool | None = None
    due: date | None = None


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    return TASKS[task_id]


@app.patch("/tasks/{task_id}")
def patch_task(task_id: int, data: TaskPatch):
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    changes = data.model_dump(exclude_unset=True)     # only the keys the client really sent
    TASKS[task_id].update(changes)
    return TASKS[task_id]
