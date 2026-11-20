# An async database with a lifespan

Chapter sections 11.1 (engine, session factory, lifespan), 11.2 (using it), 9.5 (dependencies with `yield`) and section 22, Step 6 (an app factory that keeps the session factory on `app.state`). Async SQLAlchemy itself is from swe.03 section 17.

Build a small task API on an **async** SQLite database, written so that **each app gets its own database**: the URL is an argument of the factory, and the engine is created when the app **starts**, not when the module is imported.

The starter gives the table `Task` (`id`, `title`, `done`) and the schemas `TaskIn` (`title`: 1 to 200 characters, `done`: default `False`) and `TaskOut`. You write:

1. **`create_app(database_url)`** returning a FastAPI app with a **lifespan** (`@asynccontextmanager`) that:
   - at startup: creates the engine with `create_async_engine(database_url)`, creates the tables (`await conn.run_sync(Base.metadata.create_all)` inside `async with engine.begin() as conn`), and stores `async_sessionmaker(engine, expire_on_commit=False)` in **`app.state.sessionmaker`**;
   - at shutdown (after `yield`): `await engine.dispose()`.
2. **`get_session(request: Request)`**, a module-level **async generator** dependency: `async with request.app.state.sessionmaker() as session: yield session`.
3. The endpoints (all `async def`, every database call `await`ed):

| Request | Answer |
|---|---|
| `POST /tasks` body `TaskIn` | **201** `TaskOut` (with the new id) |
| `GET /tasks` | 200, list of `TaskOut`, ordered by `id` |
| `GET /tasks/{task_id}` | 200 `TaskOut`, or 404 `{"detail": "Task not found"}` |

Why the factory and the lifespan? A test can call `create_app(...)` with a **new database file** and get an app that shares nothing with the previous test. And nothing touches the database until the app really starts (`with TestClient(app)` runs the lifespan; section 11.2).

## Example

```text
app = create_app("sqlite+aiosqlite:///<tmp>/one.db")
with TestClient(app) as client:
    POST /tasks {"title": "write tests"}   -> 201 {"id": 1, "title": "write tests", "done": false}
    POST /tasks {"title": "ship", "done": true} -> 201 {"id": 2, "title": "ship", "done": true}
    GET  /tasks                            -> 200 [{"id": 1, ...}, {"id": 2, ...}]
    GET  /tasks/9                          -> 404 {"detail": "Task not found"}
    POST /tasks {"title": ""}              -> 422, loc ["body", "title"], type "string_too_short"

app2 = create_app("sqlite+aiosqlite:///<tmp>/two.db")
with TestClient(app2) as client:
    GET  /tasks                            -> 200 []        (a fresh database)
```

The tests import `create_app` and `get_session`, and give every app its own file in pytest's `tmp_path`.
