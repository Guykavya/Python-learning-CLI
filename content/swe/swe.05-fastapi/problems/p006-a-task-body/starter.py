from fastapi import FastAPI
from pydantic import BaseModel


class TaskIn(BaseModel):
    title: str
    # TODO: priority (int, default 3) and tags (list of str, default empty)


TASKS: dict[int, dict] = {}
app = FastAPI()


@app.post("/tasks")                 # TODO: the status must be 201
def create_task(task: TaskIn):
    # TODO: give an id, store the task in TASKS and return the stored dict
    return {"title": task.title}


@app.get("/tasks")
def list_tasks():
    return []                       # TODO: the stored tasks, in id order
