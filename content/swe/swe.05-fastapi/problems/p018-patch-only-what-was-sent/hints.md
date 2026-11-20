## Hint 1

After Pydantic has parsed the body, `data.due` is `None` both when the client sent `"due": null` and when it did not send `due` at all. Which method of a Pydantic model remembers the difference? (Chapter section 7.5.)

## Hint 2

`data.model_dump(exclude_unset=True)` returns a dict with **only** the keys that were present in the JSON. `{"due": null}` gives `{"due": None}`; `{"done": true}` gives `{"done": True}`; `{}` gives `{}`. A dict has a method that copies all keys of another dict into it.

## Hint 3

```text
class TaskPatch: title, done, due, each "X | None = None"

patch_task(task_id, data):
    if task_id not in TASKS: raise HTTPException(404, "Task not found")
    changes = data.model_dump(exclude_unset=True)
    TASKS[task_id].update(changes)
    return TASKS[task_id]
```
