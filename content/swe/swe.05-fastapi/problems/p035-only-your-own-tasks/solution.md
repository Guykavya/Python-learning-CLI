## Approach

```python
def create_app() -> FastAPI:
    app = FastAPI()
    tasks = {}          # id -> {"id", "title", "done", "owner"}
    ids = itertools.count(1)     # 1, 2, 3, ... never reused, even after a delete

    def get_own_task(task_id: int, user: CurrentUser) -> dict:
        task = tasks.get(task_id)
        # Missing and "not yours" get the SAME answer, so nobody learns which ids exist.
        if task is None or task["owner"] != user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
        return task

    OwnTask = Annotated[dict, Depends(get_own_task)]

    @app.get("/tasks")
    def list_tasks(user: CurrentUser):
        return [t for _, t in sorted(tasks.items()) if t["owner"] == user]

    @app.post("/tasks", status_code=201)
    def create_task(data: TaskIn, user: CurrentUser):
        task_id = next(ids)
        tasks[task_id] = {"id": task_id, "title": data.title, "done": False, "owner": user}   # owner = the caller
        return tasks[task_id]

    @app.get("/tasks/{task_id}")
    def get_task(task: OwnTask):
        return task

    @app.patch("/tasks/{task_id}")
    def update_task(data: TaskPatch, task: OwnTask):
        task["done"] = data.done
        return task

    @app.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task: OwnTask):
        del tasks[task["id"]]

    return app
```

Trace `DELETE /tasks/1` with ben's token. FastAPI resolves `get_own_task`: its `user` parameter resolves `get_current_user` → `"ben"`; `task_id` comes from the path → 1. Task 1's owner is `"asha"`, so it raises 404. `delete_task` never runs, so nothing can be deleted by accident: the endpoint body cannot even see a task that is not the caller's.

The two layers:

- **Authentication** (`get_current_user`): who are you? Failing it is 401.
- **Authorisation** (`get_own_task`, the list filter, the owner set from the user): may *you* touch *this*? Failing it is a 404 here, by choice.

The owner comes from the token, never from the body: `TaskIn` has no `owner` field, so Pydantic drops it (the mass-assignment lesson of p031).

## Complexity

O(1) per single-task request; O(n log n) for the list (sorting n tasks). A database would filter with `WHERE owner_id = ?` and an index.

## Another way

With a database, put the owner into the query itself: `select(Task).where(Task.id == task_id, Task.owner_id == user.id)`. A row that is not yours is then simply "not found" by the database, and there is no second check to forget. Teams and shared tasks (the project in section 22) extend the same dependency with "or the user is a member of the task's team".
