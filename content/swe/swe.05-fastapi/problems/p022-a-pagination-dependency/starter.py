from typing import Annotated

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

TASKS = [f"task {i}" for i in range(1, 26)]
USERS = [f"user {i}" for i in range(1, 13)]
TAGS = ["home", "work", "urgent", "later", "ideas"]


class Page(BaseModel):
    limit: int
    offset: int


def page_params(limit: int = 10, offset: int = 0) -> Page:
    # TODO: constrain limit to 1..100 and offset to >= 0 with Annotated + Query
    return Page(limit=limit, offset=offset)


Pagination = Annotated[Page, Depends(page_params)]


@app.get("/tasks")
def list_tasks():
    # TODO: take page: Pagination and return the slice
    return {"items": TASKS, "total": len(TASKS), "limit": 10, "offset": 0}


@app.get("/users")
def list_users():
    return {"items": USERS, "total": len(USERS), "limit": 10, "offset": 0}


@app.get("/tags")
def list_tags():
    return {"items": TAGS, "total": len(TAGS), "limit": 10, "offset": 0}
