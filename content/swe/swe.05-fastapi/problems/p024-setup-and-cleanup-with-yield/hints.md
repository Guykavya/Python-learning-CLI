## Hint 1

Section 9.5 shows the shape: code before `yield` runs before the endpoint, the endpoint runs "at" the `yield`, and an exception from the endpoint is thrown **into** the generator at the `yield`. Which Python statement lets you run code on success, on failure, and in both cases?

## Hint 2

`try: yield session; session.commit()` / `except Exception: session.rollback(); raise` / `finally: session.close()`. The `raise` matters: if you swallow the exception, FastAPI cannot send the 409, and it fails with an error about a dependency that caught the exception.

## Hint 3

```text
get_session(factory = Depends(get_session_factory)):
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```
