## Approach

```python
async def get_session(request: Request):
    async with request.app.state.sessionmaker() as session:    # closed when the request is done
        yield session


def create_app(database_url: str) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_async_engine(database_url)               # startup: nothing touched the database before this
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        yield                                                    # the app serves requests here
        await engine.dispose()                                   # shutdown: close all connections

    app = FastAPI(lifespan=lifespan)

    @app.post("/tasks", response_model=TaskOut, status_code=201)
    async def create_task(data: TaskIn, session: Session):
        task = Task(title=data.title, done=data.done)
        session.add(task)
        await session.commit()
        return task

    @app.get("/tasks", response_model=list[TaskOut])
    async def list_tasks(session: Session):
        result = await session.execute(select(Task).order_by(Task.id))
        return result.scalars().all()

    @app.get("/tasks/{task_id}", response_model=TaskOut)
    async def get_task(task_id: int, session: Session):
        task = await session.get(Task, task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        return task

    return app
```

The life of one app in a test:

1. `create_app(url)` only **describes** the app: routes and a lifespan. No engine, no file.
2. `with TestClient(app)` runs the lifespan up to `yield`: the engine is made from *this* URL, the tables are created, and the session factory is put on `app.state`.
3. Each request: `get_session` opens a session from `request.app.state.sessionmaker`, the endpoint awaits its database calls, and `async with` closes the session.
4. Leaving the `with` block runs the code after `yield`: `engine.dispose()` closes the pooled connections, so the file is released.

`expire_on_commit=False` is what lets `return task` work after `await session.commit()`: the loaded `id`, `title` and `done` stay readable instead of being expired and lazily reloaded, which async SQLAlchemy cannot do (section 11.5).

## Complexity

Each request is one or two SQL statements; `GET /tasks` is O(n) rows.

## Another way

Keep the engine in the lifespan but pass the session factory to the routes through a dependency `get_sessionmaker(request)` instead of reading `app.state` directly in `get_session`; tests can then override that one dependency. For production schemas, create tables with Alembic migrations (swe.03) instead of `create_all` at startup.
