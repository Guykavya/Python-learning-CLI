# Read a 422

Chapter sections 6.1 (the request lifecycle) and 6.2 (the anatomy of a 422), with 4.3 (invalid JSON versus invalid data) and 5.8 (`loc` paths into lists). This is the chapter's `POST /projects/{project_id}/tasks` endpoint with one more field, `tags`. The program sends five bad requests and prints **every** item of each 422 `detail` list, one line per item: the request number, the status, the `loc` parts joined with dots, and the error `type`.

```python
from typing import Annotated

from fastapi import FastAPI, Header, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


class TaskIn(BaseModel):
    title: str = Field(min_length=3)
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []


app = FastAPI()


@app.post("/projects/{project_id}/tasks")
def create(
    project_id: int,
    task: TaskIn,
    notify: Annotated[bool, Query()] = False,
    x_client: Annotated[str, Header()] = "web",
):
    return {"ok": True}


GOOD = {"title": "write tests", "priority": 2}
requests = [
    ("/projects/abc/tasks", GOOD),
    ("/projects/1/tasks", {"title": "write tests"}),
    ("/projects/1/tasks", {"title": "write tests", "priority": 2, "tags": ["api", 5, "db"]}),
    ("/projects/1/tasks?notify=maybe", {"title": "ab", "priority": 0}),
    ("/projects/abc/tasks?notify=maybe", '{"title": "write tests",'),
]

client = TestClient(app)
for number, (url, body) in enumerate(requests, 1):
    if isinstance(body, str):
        r = client.post(url, content=body.encode(), headers={"content-type": "application/json"})
    else:
        r = client.post(url, json=body)
    for error in r.json()["detail"]:
        where = ".".join(str(part) for part in error["loc"])
        print(f"{number}: {r.status_code} {where} {error['type']}")
```

Write your answer in `answer.txt`: one line per error, in the format of the `print` (for example `6: 422 query.page int_parsing`), in the order the program prints them. A request with three errors gives three lines with the same number. Do not run it.

Things to decide for each request: **which** values are wrong, **how many** errors FastAPI reports, in **what order**, and the exact error `type` (section 6.2's table lists the common ones; `string_type` is "not a string", `missing` is "not sent"). For request 5, think about **when** the body is read in the lifecycle of section 6.1, and what a `loc` looks like for broken JSON (it ends with the character position where the parser gave up).

## After you answer

1. Request 4 has three problems but got one response. Why is that better for the client than stopping at the first problem?
2. Request 5 also has a bad path id and a bad query value. Why are they not reported?
3. A mobile app shows the user "Title is too short". Should it look at `msg` or at `type` and `loc`? Why?
