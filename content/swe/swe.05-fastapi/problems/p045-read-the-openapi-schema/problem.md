# Read the OpenAPI schema

Chapter section 19.1 (and 3.4 for headers, 7.6 for status codes). FastAPI builds the OpenAPI document from your code. Here is a three-endpoint app and a loop that prints, for every operation, the **required** inputs, the **optional** ones and the **response status codes** that `app.openapi()` lists. The last line lists the names of the schemas in `components`.

```python
from typing import Annotated

from fastapi import FastAPI, Header, Query, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Mini tasks")


class TaskIn(BaseModel):
    title: str = Field(min_length=1)
    priority: int = 3


class TaskOut(TaskIn):
    id: int


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks():
    return []


@app.post("/tasks", status_code=201, response_model=TaskOut)
def create_task(task: TaskIn, x_user: Annotated[str, Header()]):
    return {"id": 1, **task.model_dump()}


@app.delete("/tasks/{task_id}", status_code=204, responses={404: {"description": "No such task"}})
def delete_task(task_id: int, force: Annotated[bool, Query()] = False):
    return Response(status_code=204)


spec = app.openapi()
for path in sorted(spec["paths"]):
    for method in sorted(spec["paths"][path]):
        operation = spec["paths"][path][method]
        params = operation.get("parameters", [])
        required = sorted(f"{p['name']}({p['in']})" for p in params if p.get("required"))
        optional = sorted(f"{p['name']}({p['in']})" for p in params if not p.get("required"))
        if operation.get("requestBody", {}).get("required"):
            required.append("body")
        responses = ",".join(sorted(operation["responses"]))
        print(f"{method.upper()} {path} | required: {', '.join(required) or '-'}"
              f" | optional: {', '.join(optional) or '-'} | responses: {responses}")
print("schemas:", ", ".join(sorted(spec["components"]["schemas"])))
```

Write your answer in `answer.txt`: the four lines the program prints, exactly in its format (`|` separators, `-` for an empty list, the inputs as `name(in)`; note that `body` is added **after** the sorting).

Things to decide for each operation: which parameters exist and where they come from (`path`, `query`, `header`); how a header parameter's **name** is written in the spec; whether there is a request body; the success status; and when FastAPI adds a `422` response by itself. Do not run it.

## After you answer

1. Why does `GET /tasks` have no `422` in its responses, while `DELETE /tasks/{task_id}` has one?
2. The Python parameter is `x_user`. Why is the name in the spec different, and what header does a client send?
3. Where do the two schemas `HTTPValidationError` and `ValidationError` come from, given that you never defined them?
