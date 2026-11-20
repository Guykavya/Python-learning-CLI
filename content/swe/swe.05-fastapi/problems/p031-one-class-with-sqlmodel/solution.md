## Approach

```python
class TaskBase(SQLModel):                              # shared fields with their rules; no table
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=3, ge=1, le=5)


class Task(TaskBase, table=True):                      # the table
    id: int | None = Field(default=None, primary_key=True)


class TaskCreate(TaskBase):                            # input: no id, so a client cannot choose one
    pass


class TaskRead(TaskBase):                              # output: the id is always there
    id: int


@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(data: TaskCreate, session: SessionDep):
    task = Task.model_validate(data)               # copies title and priority; id stays None
    session.add(task)
    session.commit()
    session.refresh(task)                          # now task.id is set by the database
    return task
```

(The `GET` routes only gain `response_model=list[TaskRead]` and `response_model=TaskRead`.)

What each class is for:

- **`TaskBase`** holds the fields and their rules once. Because it is a plain `SQLModel` (no `table=True`), it behaves like a Pydantic model and **validates**.
- **`Task`** is the table. SQLModel skips validation when a `table=True` object is created (so the ORM can build half-filled rows), which is why it must never be the request body.
- **`TaskCreate`** is the input. It has no `id`, so `{"id": 99, ...}` loses the `id` key during validation. This blocks a whole class of bugs called *mass assignment*: the client sets fields it should not control (an id, an owner, an `is_admin` flag).
- **`TaskRead`** is the output, with `id: int` required, so the docs and clients know every task has one.

Example: `POST {"id": 99, "title": "sneaky"}`. FastAPI validates it as `TaskCreate(title="sneaky", priority=3)`; `Task.model_validate` makes a row with `id=None`; SQLite assigns 1; the answer is `{"title": "sneaky", "priority": 3, "id": 1}`.

## Complexity

O(1) per create or get, O(n) for the list.

## Another way

Plain SQLAlchemy for the table plus separate Pydantic models for input and output (section 7.2 and the project in section 22). It is more code, but the database layer and the API layer can then change independently; SQLModel is best when the two shapes are almost the same, as here.
