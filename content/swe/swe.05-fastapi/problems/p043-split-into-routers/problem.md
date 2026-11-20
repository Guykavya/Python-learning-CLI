# Split into routers

Chapter section 17.1. The starter is a small task API written directly on `app`. Each task endpoint repeats the same login check, and one endpoint (`GET /tasks/{task_id}`) **forgot it**. That is exactly the bug that routers with shared dependencies prevent: put the check on the router once, and every route in it is protected, including the ones added next year.

Rewrite `solution.py` with two routers:

- `meta_router = APIRouter(tags=["meta"])` with `GET /health` → `{"status": "ok"}`. No login.
- `tasks_router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_user)])` with:
  - `GET ""` → the list of tasks (values of `TASKS`, in id order),
  - `GET "/{task_id}"` → one task, or **404** `"Task not found"`,
  - `POST ""` with body `TaskIn` (`title: str`, 1 to 100 characters) → **201** and the new task `{"id": ..., "title": ...}` (ids 1, 2, 3, ... = `len(TASKS) + 1`).

Then plug them in: `app.include_router(meta_router)` and `app.include_router(tasks_router, prefix="/api")`. Prefixes add up, so the task routes become `/api/tasks` and `/api/tasks/{task_id}`.

`require_user` (given) reads the header `X-User` and raises **401** when it is missing. With the dependency on the router, the endpoint functions themselves no longer mention the user at all.

## Example

```text
GET  /health                              -> 200 {"status": "ok"}
GET  /api/tasks                           -> 401 (no X-User header)
POST /api/tasks  X-User: asha  {"title": "write"}  -> 201 {"id": 1, "title": "write"}
GET  /api/tasks/1  X-User: asha            -> 200 {"id": 1, "title": "write"}
GET  /api/tasks/1                          -> 401 (the starter forgot this one and answered 200!)
GET  /tasks                                -> 404 (the old path is gone)
```

The tests also read `app.openapi()` to check the final paths and tags, and they check that `require_user` sits in `tasks_router.dependencies` (once for the router, not in each endpoint).
