## Approach

Match each proxy with the context that backs it.

```text
1: ok
2: RuntimeError
3: ok
4: RuntimeError
5: ok
6: RuntimeError
7: RuntimeError
8: ok
9: RuntimeError
10: ok
```

| Proxy | Needs |
|---|---|
| `app.config` (the object) | nothing |
| `current_app`, `g` | application context |
| `request`, `session` | request context |
| `url_for` | request context (to know the host), **or** an app context with `SERVER_NAME` set |

- **7** is the one that surprises: an app context says *which app*, but not *which host* the URL should have. Flask raises `RuntimeError: Unable to build URLs outside an active request without 'SERVER_NAME' configured`. With `app.config["SERVER_NAME"] = "example.com"` it would work.
- **9:** `session` is read from the request's cookie; no request, no session.

Real output of the program, run with Flask 3.1.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

`flask shell` and `with app.app_context():` give scripts and tests an app context. `app.test_request_context(...)` builds a fake request for code that needs one. For work in another thread, copy what you need first (or use `copy_current_request_context`).

## Not covered

`RuntimeError: Working outside of application context` vs `... of request context`: the message names the missing one; read it.
