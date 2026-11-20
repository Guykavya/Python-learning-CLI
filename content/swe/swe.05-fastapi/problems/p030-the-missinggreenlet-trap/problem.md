# The `MissingGreenlet` trap

Chapter section 11.5 (the `MissingGreenlet` trap, `selectinload`), with 11.1 and 11.2 for the setup and 5.11 for `from_attributes`. Relationships and loading strategies are from swe.03.

The starter is a working async app (the same factory and lifespan as p029) with **tasks that have tags**: `Task.tags` is a one-to-many relationship to `Tag`. Creating a task works. But three endpoints answer **500**:

```text
POST /tasks {"title": "write", "tags": ["home", "urgent"]} -> 201 {"id": 1, "title": "write", "tags": [{"name": "home"}, {"name": "urgent"}]}
GET  /tasks                                               -> 500
GET  /tasks/1                                             -> 500
POST /tasks/1/tags {"name": "later"}                      -> 500
```

Behind each 500 is the same mistake. The query loads the `Task` rows but **not their tags**. Later something touches `task.tags`: Pydantic reading it to build `TaskOut` (the response model), or `task.tags.append(...)`. Touching an unloaded relationship means "go and fetch it now" (lazy loading), which is a database call hidden inside an attribute access. Async SQLAlchemy cannot do I/O there, because there is no `await`, so it raises `MissingGreenlet`.

When the response model is what touches it, FastAPI reports it as a **`ResponseValidationError`** whose error has type `get_attribute_error` and a message that starts with `Error extracting attribute: StatementError: (sqlalchemy.exc.MissingGreenlet) greenlet_spawn has not been called...`. You may also see `RuntimeWarning: coroutine 'Connection.cursor' was never awaited`, a side effect of the same mistake.

**Fix the three endpoints** so that the tags are loaded **in the query**, before anything touches them:

- `GET /tasks`: `select(Task).options(selectinload(Task.tags)).order_by(Task.id)`.
- `GET /tasks/{task_id}` and `POST /tasks/{task_id}/tags`: `session.get` accepts loader options too: `await session.get(Task, task_id, options=[selectinload(Task.tags)])`.

Do not change the models, the schemas or the response models (the API must still return the tags).

## Example

After the fix:

```text
GET  /tasks          -> 200 [{"id": 1, "title": "write", "tags": [{"name": "home"}, {"name": "urgent"}]},
                             {"id": 2, "title": "read", "tags": []}]
POST /tasks/2/tags {"name": "later"} -> 201 {"id": 2, "title": "read", "tags": [{"name": "later"}]}
GET  /tasks/9        -> 404 {"detail": "Task not found"}
```

The tests import `create_app` and use a new database file in `tmp_path` for every test. They use `TestClient(app, raise_server_exceptions=False)`, so the bug shows up as the 500 a user would see.
