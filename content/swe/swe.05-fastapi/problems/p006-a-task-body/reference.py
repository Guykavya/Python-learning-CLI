from fastapi import FastAPI
from pydantic import BaseModel


class TaskIn(BaseModel):
    title: str
    priority: int = 3
    tags: list[str] = []


TASKS: dict[int, dict] = {}
app = FastAPI()


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    task_id = len(TASKS) + 1
    stored = {"id": task_id, "title": task.title, "priority": task.priority, "tags": task.tags}
    TASKS[task_id] = stored
    return stored


@app.get("/tasks")
def list_tasks():
    return [TASKS[task_id] for task_id in sorted(TASKS)]
