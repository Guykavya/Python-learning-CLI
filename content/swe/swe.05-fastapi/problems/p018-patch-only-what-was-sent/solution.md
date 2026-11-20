## Approach

```python
class TaskPatch(BaseModel):
    title: str | None = None
    done: bool | None = None
    due: date | None = None


@app.patch("/tasks/{task_id}")
def patch_task(task_id: int, data: TaskPatch):
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    changes = data.model_dump(exclude_unset=True)     # only the keys the client really sent
    TASKS[task_id].update(changes)
    return TASKS[task_id]
```

Pydantic keeps a set of the fields that were **set** when the model was built (`data.model_fields_set`). `exclude_unset=True` uses it: defaults that were filled in by Pydantic are left out, values the client sent are kept, even when the value is `null`.

Example: body `{"due": null}`.

- `data.model_dump()` gives `{"title": None, "done": None, "due": None}`; updating with it would wipe the title and the done flag.
- `data.model_dump(exclude_none=True)` gives `{}`; the client's request to clear the date is lost.
- `data.model_dump(exclude_unset=True)` gives `{"due": None}`: exactly what the client asked for.

The stored `due` stays a `date` object (`model_dump` in Python mode keeps dates as `date`); FastAPI turns it into `"2026-12-01"` when it writes the JSON.

## Complexity

O(k) per request, where k is the number of fields sent.

## Another way

Loop over `data.model_fields_set` (the names of the fields that were sent) and copy `getattr(data, name)` for each one. It is the same idea written by hand. In a database version you would set the attributes on the ORM row instead: `for key, value in changes.items(): setattr(row, key, value)`.

## Not covered

Here a client could also send `{"title": null}` and get a task without a title. A real API forbids that with a field validator that rejects `None` for `title` (section 5.5) while still allowing the field to be left out.
