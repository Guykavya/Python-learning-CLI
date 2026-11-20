## Approach

Describe the body with a model and let FastAPI do the checking. The function only stores and returns.

```python
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
```

Example: `{"title": "pay rent", "priority": "1"}` is valid JSON with the right shape; `"1"` is converted to `1`, so the function receives `TaskIn(title='pay rent', priority=1, tags=[])`. Form data `title=x` is not JSON at all, so Pydantic sees the string `'title=x'` where it wanted an object: one error at `["body"]` of type `model_attributes_type`, and the function never runs.

## Complexity

O(size of the body) to parse and validate; storing is O(1).

## Another way

Return the model itself: make `TaskOut(TaskIn)` with an `id: int` field and `return TaskOut(id=task_id, **task.model_dump())`, with `response_model=TaskOut`. The response is then documented in `/docs` too (section 7.1).

`len(TASKS) + 1` breaks once you can delete tasks (two tasks could get the same id). A real app lets the database give the id (swe.03), or keeps a counter that only grows.
