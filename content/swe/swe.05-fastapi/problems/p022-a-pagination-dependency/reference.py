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


def page_params(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page:
    return Page(limit=limit, offset=offset)


Pagination = Annotated[Page, Depends(page_params)]


def paginate(data, page: Page):
    return {
        "items": data[page.offset:page.offset + page.limit],
        "total": len(data),
        "limit": page.limit,
        "offset": page.offset,
    }


@app.get("/tasks")
def list_tasks(page: Pagination):
    return paginate(TASKS, page)


@app.get("/users")
def list_users(page: Pagination):
    return paginate(USERS, page)


@app.get("/tags")
def list_tags(page: Pagination):
    return paginate(TAGS, page)
