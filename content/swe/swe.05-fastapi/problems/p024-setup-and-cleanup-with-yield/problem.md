# Setup and cleanup with `yield`

Chapter sections 9.3 (sub-dependencies), 9.5 (dependencies with `yield`) and 9.6 (`dependency_overrides`). The unit-of-work idea (commit or roll back as a whole) is from swe.03.

Every request that writes data needs the same frame around it:

```text
open a session  ->  run the endpoint  ->  success?  commit  : roll back  ->  ALWAYS close
```

Write the dependency **`get_session`** that gives each request this frame.

- It takes a **session factory** from another dependency, `get_session_factory` (already written), calls it once to open a session, and **yields** the session to the endpoint.
- If the endpoint finished without an exception: call `session.commit()`.
- If the endpoint raised **any** exception (an `HTTPException` included): call `session.rollback()` and then **re-raise** the exception, so FastAPI can still answer with the right status (409, 500...).
- In every case: call `session.close()` exactly once at the end.

A session has four methods: `add(item)`, `commit()`, `rollback()`, `close()`. In a real app the factory is SQLAlchemy's `sessionmaker` (swe.03); here the starter gives a tiny `ListSession` that keeps added items pending and moves them to the module list `SAVED` on commit. The endpoints are written for you:

| Endpoint | What it does |
|---|---|
| `POST /notes` body `{"text": ...}` | `session.add(text)`, answers 201 `{"text": ...}` |
| `POST /notes/duplicate` body `{"text": ...}` | `session.add(text)`, then raises `HTTPException(409, "Note already exists")` |
| `POST /notes/crash` body `{"text": ...}` | `session.add(text)`, then raises `RuntimeError` (a bug): 500 |

## Example

The tests replace `get_session_factory` with a fake whose sessions write every call into a log:

```text
POST /notes {"text": "hello"}      -> 201   log: open, add hello, commit,   close
POST /notes/duplicate {"text": "x"} -> 409   log: open, add x,     rollback, close
POST /notes/crash {"text": "x"}     -> 500   log: open, add x,     rollback, close
```

Without the fake, the real `ListSession` is used: after the first request `SAVED == ["hello"]`; after the other two nothing more is saved.

The tests import `app`, `get_session`, `get_session_factory` and `SAVED`.
