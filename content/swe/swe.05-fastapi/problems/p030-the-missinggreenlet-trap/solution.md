## Approach

```python
@app.get("/tasks", response_model=list[TaskOut])
async def list_tasks(session: Session):
    stmt = select(Task).options(selectinload(Task.tags)).order_by(Task.id)  # tags loaded with the tasks
    result = await session.execute(stmt)
    return result.scalars().all()


@app.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, session: Session):
    task = await session.get(Task, task_id, options=[selectinload(Task.tags)])
    if task is None:
        raise HTTPException(404, "Task not found")
    return task


@app.post("/tasks/{task_id}/tags", response_model=TaskOut, status_code=201)
async def add_tag(task_id: int, data: TagIn, session: Session):
    task = await session.get(Task, task_id, options=[selectinload(Task.tags)])
    if task is None:
        raise HTTPException(404, "Task not found")
    task.tags.append(Tag(name=data.name))   # the list is loaded, so appending needs no hidden query
    await session.commit()
    return task
```

Why the original failed, step by step, for `GET /tasks`:

1. `await session.execute(select(Task))` runs `SELECT ... FROM tasks`. The `Task` objects have `id` and `title`; `tags` is **not loaded**.
2. The endpoint returns the list. FastAPI validates it against `list[TaskOut]`; with `from_attributes=True`, Pydantic reads `task.tags`.
3. The default loading strategy is "lazy": on first access, run `SELECT ... FROM tags WHERE task_id = ?`. That query would need an `await`, but attribute access is plain synchronous code. SQLAlchemy raises `MissingGreenlet`.
4. Pydantic catches the error while reading the attribute and reports it as `get_attribute_error`; FastAPI raises `ResponseValidationError`, a 500.

With `selectinload(Task.tags)`, step 1 runs two queries, both awaited: the tasks, then `SELECT ... FROM tags WHERE task_id IN (1, 2)`. Every `task.tags` is then a plain loaded list, and reading or appending touches no database.

`POST /tasks` never failed because the tags of a **new** object were set in Python, and `expire_on_commit=False` kept them; nothing had to be loaded.

## Complexity

Two queries for the whole list (tasks, then all their tags), instead of 1 + n lazy queries in synchronous code: `selectinload` is also the cure for the N+1 problem (swe.03, section 11.2 of the chapter).

## Another way

- Set `lazy="selectin"` on the relationship itself (`relationship(back_populates="task", lazy="selectin")`): every query then loads tags automatically. Convenient, but it also loads them where nobody needs them.
- Set `lazy="raise"` on the relationship: an accidental lazy load then fails immediately with a clear message, in both sync and async code, so the bug shows up in the first test instead of in production.
- For a single parent object (a many-to-one like `Tag.task`), `joinedload` loads it in the same query with a JOIN.
