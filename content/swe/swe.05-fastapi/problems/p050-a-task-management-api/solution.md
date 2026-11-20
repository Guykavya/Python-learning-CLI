## Approach

Build the layers of section 22 in order and test after each one. The finished file is `reference.py` (about 490 lines, of which the starter gave about 270). Its parts:

```text
given        Settings.from_env, make_engine, tables, schemas, hash/verify, create/decode token, ConnectionManager
deps         get_session, get_settings, get_manager, oauth2_scheme, current_user, find_membership, team_member, team_owner
auth_router  register (409 on duplicate, hash in a thread), login (case-insensitive email, 401 on failure)
teams_router create (team + owner membership in one transaction), my teams, add member (owner only)
tasks_router create, list (filter + limit/offset + total), get one, patch (exclude_unset), delete (owner or creator)
ws_router    /ws/teams/{team_id}: token + membership checked before accept, else close 1008
errors       one handler for starlette's HTTPException, one for RequestValidationError, same envelope
create_app   lifespan (tables, sessionmaker, manager on app.state), handlers, routers, /health
```

The two excerpts that carry most of the rules:

```python
async def team_member(team_id: int, user: CurrentUser, session: Session) -> Membership:
    membership = await find_membership(session, user.id, team_id)
    if membership is None:
        raise HTTPException(404, "Team not found")           # 404, not 403: do not reveal that it exists
    return membership


async def load_task(session: AsyncSession, team_id: int, task_id: int) -> Task:
    """Look the task up INSIDE the team from the URL: a task id from another team is a 404."""
    task = await session.scalar(select(Task).where(Task.id == task_id, Task.team_id == team_id))
    if task is None:
        raise HTTPException(404, "Task not found")
    return task
```

And the envelope, registered on the **Starlette** class so that the router's own 404 for an unknown path uses it too:

```python
async def http_error(request: Request, exc: StarletteHTTPException):
    code = ERROR_CODES.get(exc.status_code, "http_error")
    return envelope(exc.status_code, code, str(exc.detail), headers=getattr(exc, "headers", None))


async def validation_error(request: Request, exc: RequestValidationError):
    details = [{"loc": list(e["loc"]), "type": e["type"], "msg": e["msg"]} for e in exc.errors()]
    return envelope(422, "validation_failed", "Request data is invalid", details)
```

Example (the `test_outsider_gets_404_everywhere` story): Cara sends `PATCH /teams/1/tasks/1`. FastAPI resolves `Member`: `team_member` needs `current_user`, which needs the token (valid: Cara exists) and a session. `find_membership(cara, team 1)` is `None`, so `team_member` raises 404 before `update_task` even runs; the handler turns it into `{"error": {"code": "not_found", "message": "Team not found"}}`. Nothing was changed, and Cara cannot even tell whether team 1 exists.

Differences from the chapter's code: the tasks router has a `GET` for one task; `create_task` and `delete_task` use `member.user_id` instead of declaring `CurrentUser` a second time (FastAPI would run it only once anyway, thanks to the per-request dependency cache); everything is in one file; and the error envelope of section 8.2 is added.

## Complexity

Each request costs a constant number of SQL statements (the list endpoint: one `count` and one page query; the dependency stack: one user lookup and one membership lookup). Registration and login each cost one scrypt hash (about 50 ms by design), run in a thread so the event loop stays free. A broadcast is O(k) for k sockets in the team's room.

## Another way

Split the file into the package layout of sections 17.2 and 22 (`app/config.py`, `models.py`, `schemas.py`, `security.py`, `deps.py`, `routers/`, `main.py`) and move the tests to `tests/` with a `conftest.py`. Then the chapter's extension ideas: refresh tokens, a `GET /teams/{id}` with its members (`selectinload`), Alembic migrations instead of `create_all`, cursor pagination, the request-id middleware of problem 36, rate limiting on `/auth/login`, and Redis pub/sub so that several worker processes share the WebSocket rooms (section 21).

## Not covered

A real database server (PostgreSQL), deployment behind a proxy, and email verification of new accounts.
