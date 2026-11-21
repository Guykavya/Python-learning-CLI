## Approach

```python
def create_app(checks):
    app = FastAPI()
    app.state.draining = False

    @app.get("/healthz")
    def healthz():
        return {"status": "alive"}

    @app.get("/readyz")
    def readyz():
        problems = {}
        if app.state.draining:
            problems["draining"] = "shutting down"
        for name, check in checks.items():
            try:
                check()
            except Exception as exc:
                problems[name] = str(exc) or type(exc).__name__
        if problems:
            return JSONResponse({"status": "not ready", "problems": problems}, status_code=503)
        return {"status": "ready"}

    return app
```

The chapter's experiment (9.3): with Redis stopped, liveness stayed green, readiness turned red naming `redis`, Docker marked the container unhealthy (it does not restart on that alone), and when Redis returned everything recovered with no restart. Dependencies are passed in as functions, which makes the endpoint testable without a real database.

## Complexity

`/healthz` is O(1) and touches nothing. `/readyz` costs one cheap call per dependency (`SELECT 1`, `PING`); keep each check fast with a short timeout.

## Another way

Add a third endpoint for **startup** (has the app finished warming its cache?) as Kubernetes does (chapter 9.4), so liveness does not kill a slow starter. Put only what is **necessary to serve and under your control** into `checks`; an outside payment provider belongs in metrics and alerts, not in readiness (chapter "Try it: why not just check everything?").
