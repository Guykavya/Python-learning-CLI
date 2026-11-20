## Approach

```python
meta_router = APIRouter(tags=["meta"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_user)])


@meta_router.get("/health")
def health():
    return {"status": "ok"}


@tasks_router.get("")
def list_tasks():
    return [TASKS[i] for i in sorted(TASKS)]


@tasks_router.get("/{task_id}")
def get_task(task_id: int):                 # protected by the router's dependency
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    return TASKS[task_id]


@tasks_router.post("", status_code=201)
def create_task(data: TaskIn):
    task = {"id": len(TASKS) + 1, "title": data.title}
    TASKS[task["id"]] = task
    return task


app = FastAPI()
app.include_router(meta_router)
app.include_router(tasks_router, prefix="/api")      # prefixes add up: /api/tasks
```

Example: `GET /api/tasks/1` with no header. The path is `/api` (include) + `/tasks` (router) + `/{task_id}` (route). Before the endpoint runs, FastAPI runs the router's dependencies; `require_user` raises 401, and `get_task` never runs. In the starter the same request got a 200 with the task, because that one route had no check: the bug a router-level dependency makes impossible.

`dependencies=[...]` runs the dependency only for its **effect** (raising 401); its return value is thrown away. When an endpoint also needs the user's name, declare the dependency again as a parameter: FastAPI caches it per request, so it still runs only once.

Why 401 before 422 in `test_auth_runs_before_body_validation`: FastAPI runs the dependencies first and validates the body parameters after them, and a dependency that raises stops everything. So an anonymous caller learns nothing about your validation rules.

## Complexity

Not about speed: routers cost nothing at request time (they are flattened into the app's route list at `include_router`).

## Another way

Put each router in its own module (`routers/tasks.py`, `routers/meta.py`) and keep `main.py` for wiring only (section 17.2). You can also attach dependencies at include time instead of creation time: `app.include_router(tasks_router, prefix="/api", dependencies=[Depends(require_user)])`. That is handy when the same router is mounted twice with different rules (a public read-only mount and an admin mount).
