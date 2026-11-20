# `PATCH` only what was sent

Chapter sections 5.7 (`model_dump`) and 7.5 (partial updates with `PATCH`).

A small task API keeps its tasks in a module-level dict `TASKS`. Each task is a dict:

```python
TASKS[1] = {"id": 1, "title": "write report", "done": False, "due": date(2026, 12, 1)}
```

`due` is a `datetime.date` or `None` (no due date). `GET /tasks/{task_id}` is already written. Your job is the partial update:

1. A model **`TaskPatch`** with three fields, **all optional with default `None`**: `title: str | None`, `done: bool | None`, `due: date | None`.
2. **`PATCH /tasks/{task_id}`** takes a `TaskPatch` body and changes **only the fields the client actually sent**, then returns the whole updated task (status 200). An unknown id gives **404** with `{"detail": "Task not found"}`.

The hard part is telling apart two requests that look the same once they are parsed:

| Body sent | Meaning | `due` afterwards |
|---|---|---|
| `{"done": true}` | change `done`, leave the rest | unchanged |
| `{"due": null}` | **remove** the due date | `None` |
| `{}` | change nothing | unchanged |

In both of the first two cases `data.due` is `None` inside your function. Only `data.model_dump(exclude_unset=True)` remembers which fields were **really sent**.

Pydantic still validates what is sent: `{"due": "next week"}` is a 422 at `loc` `["body", "due"]`.

## Example

Start: task 1 is `{"id": 1, "title": "write report", "done": false, "due": "2026-12-01"}`.

```text
PATCH /tasks/1 {"done": true}         -> 200 {"id": 1, "title": "write report", "done": true,  "due": "2026-12-01"}
PATCH /tasks/1 {"due": null}          -> 200 {"id": 1, "title": "write report", "done": true,  "due": null}
PATCH /tasks/1 {"due": "2027-01-15"}  -> 200 {... "due": "2027-01-15"}
PATCH /tasks/9 {"done": true}         -> 404 {"detail": "Task not found"}
```

The change must be **stored**: a `GET /tasks/1` afterwards shows the same task.

The tests import `app`, `TASKS` and `TaskPatch` from your `solution.py`, and they fill `TASKS` themselves before each test.
