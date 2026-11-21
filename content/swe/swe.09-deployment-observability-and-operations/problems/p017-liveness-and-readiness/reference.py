from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_app(checks):
    app = FastAPI()
    app.state.draining = False

    @app.get("/healthz")
    def healthz():
        return {"status": "alive"}                              # liveness checks NOTHING else

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
