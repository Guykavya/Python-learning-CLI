## Hint 1

What has to exist before the first request, and what must be cleaned up at the end? Section 11.1's lifespan does both around a `yield`. Here the URL is not a module constant but an argument of `create_app`, so the lifespan must be defined **inside** `create_app` (a closure that can see `database_url`). Section 22 Step 6 shows this shape.

## Hint 2

The dependency cannot see a local variable of `create_app`, but it can see the app: `request.app.state.sessionmaker`. Store the factory there in the lifespan. In the endpoints: `session.add(task)` then `await session.commit()`; `await session.execute(select(Task).order_by(Task.id))` then `.scalars().all()`; `await session.get(Task, task_id)`.

## Hint 3

```text
create_app(database_url):
    @asynccontextmanager
    async def lifespan(app):
        engine = create_async_engine(database_url)
        async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        yield
        await engine.dispose()
    app = FastAPI(lifespan=lifespan)
    ... endpoints ...

async def get_session(request):
    async with request.app.state.sessionmaker() as session:
        yield session
```
