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

    # TODO: a dependency get_own_task(task_id, user) that returns the caller's task or raises 404

    @app.get("/tasks")
    def list_tasks(user: CurrentUser):
        return list(tasks.values())                      # TODO: only the caller's

    @app.post("/tasks", status_code=201)
    def create_task(data: TaskIn, user: CurrentUser):
        task_id = len(tasks) + 1
        tasks[task_id] = {"id": task_id, "title": data.title, "done": False, "owner": user}
        return tasks[task_id]

    @app.get("/tasks/{task_id}")
    def get_task(task_id: int, user: CurrentUser):
        return tasks[task_id]                            # TODO: anybody's task, and a KeyError when missing

    @app.patch("/tasks/{task_id}")
    def update_task(task_id: int, data: TaskPatch, user: CurrentUser):
        tasks[task_id]["done"] = data.done               # TODO
        return tasks[task_id]

    @app.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int, user: CurrentUser):
        tasks.pop(task_id, None)                         # TODO

    return app
