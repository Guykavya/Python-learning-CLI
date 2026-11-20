## Approach

```python
def get_session(factory: Annotated[type, Depends(get_session_factory)]):
    session = factory()
    try:
        yield session                 # the endpoint runs here
        session.commit()              # reached only if the endpoint did not raise
    except Exception:
        session.rollback()
        raise                         # let FastAPI answer 409 / 500 as usual
    finally:
        session.close()               # success or failure
```

Follow `POST /notes/duplicate` step by step:

1. FastAPI resolves `get_session_factory` (overridden by the test to return `FakeSession`), then starts `get_session`: `factory()` logs `open`, and the generator stops at `yield`, handing the session to the endpoint.
2. The endpoint logs `add x` and raises `HTTPException(409)`.
3. FastAPI throws that exception into the generator at the `yield`. `session.commit()` is skipped; `except Exception` runs `rollback`, and `raise` sends the same exception on.
4. `finally` runs `close`. FastAPI's own handler turns the `HTTPException` into the 409 response.

On success, the generator resumes after `yield` with no exception: `commit`, then `close`.

Taking the factory from `Depends(get_session_factory)` is what makes the frame testable: the test swaps the factory, not the frame, so the real `get_session` code is what gets tested.

## Complexity

O(1) work per request around the endpoint.

## Another way

Use the session's own context manager when it has one. With SQLAlchemy: `with SessionLocal() as session, session.begin(): yield session` commits on success, rolls back on an exception and closes, all in one line (swe.03). The explicit `try/except/finally` shows what that line does.

## Not covered

The code after `yield` runs after the endpoint has produced its response. In this FastAPI version, if `commit()` itself fails, the client has usually already been told 201. Real apps therefore often commit **inside** the endpoint (or a service function) when the client must know that the save succeeded, and keep the dependency for rollback and close.
