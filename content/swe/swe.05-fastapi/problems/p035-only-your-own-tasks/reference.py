import itertools
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

# ---- given: a simplified login (p034 builds the real one) ----

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TOKENS = {"tok-asha": "asha", "tok-ben": "ben"}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    user = TOKENS.get(token)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    return user


CurrentUser = Annotated[str, Depends(get_current_user)]


class TaskIn(BaseModel):
    title: str = Field(min_length=1)


class TaskPatch(BaseModel):
    done: bool


# ---- your part ----

def create_app() -> FastAPI:
    app = FastAPI()
    tasks = {}          # id -> {"id", "title", "done", "owner"}
    ids = itertools.count(1)     # 1, 2, 3, ... never reused, even after a delete

    def get_own_task(task_id: int, user: CurrentUser) -> dict:
        task = tasks.get(task_id)
        # Missing and "not yours" get the SAME answer, so nobody learns which ids exist.
        if task is None or task["owner"] != user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
        return task

    OwnTask = Annotated[dict, Depends(get_own_task)]

    @app.get("/tasks")
    def list_tasks(user: CurrentUser):
        return [t for _, t in sorted(tasks.items()) if t["owner"] == user]

    @app.post("/tasks", status_code=201)
    def create_task(data: TaskIn, user: CurrentUser):
        task_id = next(ids)
        tasks[task_id] = {"id": task_id, "title": data.title, "done": False, "owner": user}   # owner = the caller
        return tasks[task_id]

    @app.get("/tasks/{task_id}")
    def get_task(task: OwnTask):
        return task

    @app.patch("/tasks/{task_id}")
    def update_task(data: TaskPatch, task: OwnTask):
        task["done"] = data.done
        return task

    @app.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task: OwnTask):
        del tasks[task["id"]]

    return app
