## Hint 1

Which class should FastAPI use to read the body: one that has an `id` field, or one that does not? Pydantic simply ignores keys it does not know, so if the input model has no `id`, a client's `"id": 99` has nowhere to go.

## Hint 2

Put the shared fields and their `Field(...)` rules in `TaskBase(SQLModel)` (no `table=True`). Three classes inherit from it: the table adds the optional primary key; `TaskCreate` adds nothing; `TaskRead` adds `id: int`. In `POST`, the body is `TaskCreate`; `Task.model_validate(data)` builds the row; after `commit()`, `refresh(task)` loads the new id. Declare `response_model=TaskRead` (or `list[TaskRead]`).

## Hint 3

```text
class TaskBase(SQLModel): title = Field(min_length=1, max_length=100); priority = Field(default=3, ge=1, le=5)
class Task(TaskBase, table=True): id: int | None = Field(default=None, primary_key=True)
class TaskCreate(TaskBase): pass
class TaskRead(TaskBase): id: int

@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(data: TaskCreate, session):
    task = Task.model_validate(data); session.add(task); session.commit(); session.refresh(task); return task
GET routes: response_model=list[TaskRead] / TaskRead
```
