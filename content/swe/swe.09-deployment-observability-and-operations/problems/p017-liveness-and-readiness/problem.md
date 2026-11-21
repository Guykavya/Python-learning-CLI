# Liveness and readiness

Chapter sections 9.1 to 9.3 (three different questions; what the service does; Docker and Compose health checks) and "Try it: which check?" and "Try it: why not just check everything?". A platform asks a service two questions with different consequences: **liveness** ("is the process broken in a way a restart would fix?" -> if not, **restart** it) and **readiness** ("can it serve traffic right now?" -> if not, **stop sending traffic**, but leave it running). Mixing them up causes restart storms: if liveness also tests the database, a database outage makes the platform restart every healthy container.

## What to write

```python
def create_app(checks: dict) -> FastAPI: ...
```

`checks` maps a **name** to a function with no arguments that **raises an exception when that dependency is not usable** and returns normally otherwise, for example `{"database": check_database, "redis": check_redis}`. The app must have `app.state.draining = False` at creation, and two endpoints:

- `GET /healthz` (liveness): always `200` with `{"status": "alive"}`. It must **never call any check** (it asks only "is the process answering?").
- `GET /readyz` (readiness): runs **every** check (not only until the first failure) and also looks at `app.state.draining`.
  - A check that raises adds an entry `name: message` to `problems`, where `message` is `str(exc)`, or the exception's class name if `str(exc)` is empty.
  - If `app.state.draining` is true, add `"draining": "shutting down"`.
  - No problems: `200` with `{"status": "ready"}`. Otherwise `503` with `{"status": "not ready", "problems": {...}}`.

## Example

```python
app = create_app({"database": check_database})
# database reachable
GET /healthz -> 200 {"status": "alive"}
GET /readyz  -> 200 {"status": "ready"}
# database down (check_database raises sqlite3.OperationalError("unable to open database file"))
GET /healthz -> 200 {"status": "alive"}        # still alive: a restart would not help
GET /readyz  -> 503 {"status": "not ready", "problems": {"database": "unable to open database file"}}
```

The chapter's own table of "Try it: which check?": a database outage fails **readiness**; a deadlocked process fails **liveness** (it cannot answer at all); a down optional recommendation service fails **neither**, so such a service must not be in `checks`.
