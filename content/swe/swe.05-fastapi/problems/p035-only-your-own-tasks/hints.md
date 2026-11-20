## Hint 1

Three endpoints need the same three steps: find the task by id, check that it exists, check that its owner is the caller. Where can you put steps that several endpoints share, so that FastAPI runs them before the endpoint? (Section 9.3; section 12.4 names the pattern.)

## Hint 2

Define `get_own_task(task_id: int, user: CurrentUser)` **inside** `create_app` (so it can see `tasks`). FastAPI reads `task_id` from the path of whichever route uses it. One `if task is None or task["owner"] != user: raise HTTPException(404, "Task not found")` covers both "missing" and "not yours". The endpoints then take `task: Annotated[dict, Depends(get_own_task)]`. For the list, filter by owner. For the ids, `ids = itertools.count(1)` in `create_app` and `next(ids)` for each new task: an id is never handed out twice, even after a delete.

## Hint 3

```text
def get_own_task(task_id: int, user: CurrentUser) -> dict:
    task = tasks.get(task_id)
    if task is None or task["owner"] != user: raise HTTPException(404, "Task not found")
    return task
OwnTask = Annotated[dict, Depends(get_own_task)]

GET /tasks:            [t for _, t in sorted(tasks.items()) if t["owner"] == user]
GET /tasks/{id}:       get_task(task: OwnTask): return task
PATCH /tasks/{id}:     update_task(data: TaskPatch, task: OwnTask): task["done"] = data.done; return task
DELETE /tasks/{id}:    delete_task(task: OwnTask): del tasks[task["id"]]
```
