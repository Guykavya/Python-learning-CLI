## Hint 1

A router is used exactly like `app`: `@tasks_router.get(...)` instead of `@app.get(...)`. Where do you write the parts that all task routes share: the `/tasks` prefix, the `tasks` tag, the login check? And where does the extra `/api` come from?

## Hint 2

Create the routers with their settings, decorate the endpoints with the router, and **remove** `user: Annotated[str, Depends(require_user)]` from the endpoints (the router runs it for them). Inside a router with `prefix="/tasks"`, the list route is `""` (giving `/tasks`) and the detail route is `"/{task_id}"`. At the end: `app.include_router(meta_router)` and `app.include_router(tasks_router, prefix="/api")`.

## Hint 3

```text
meta_router  = APIRouter(tags=["meta"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_user)])
@meta_router.get("/health")         -> {"status": "ok"}
@tasks_router.get("")               -> list
@tasks_router.get("/{task_id}")     -> one or 404
@tasks_router.post("", status_code=201) -> create
app = FastAPI(); app.include_router(meta_router); app.include_router(tasks_router, prefix="/api")
```
