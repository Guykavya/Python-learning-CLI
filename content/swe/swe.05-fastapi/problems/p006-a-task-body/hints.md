## Hint 1

How does FastAPI know that `task` comes from the body and not from the query? (Section 3.1: look at its type.) Which decorator argument changes the success status from 200 to 201?

## Hint 2

The defaults belong in the model: `priority: int = 3`, `tags: list[str] = []`. In a Pydantic model a `[]` default is safe (section 5.2). In the function, build the stored dict from `task.title`, `task.priority`, `task.tags`.

## Hint 3

```text
@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    task_id = len(TASKS) + 1
    stored = {"id": task_id, "title": ..., "priority": ..., "tags": ...}
    TASKS[task_id] = stored
    return stored

@app.get("/tasks")  -> [TASKS[i] for i in sorted(TASKS)]
```
