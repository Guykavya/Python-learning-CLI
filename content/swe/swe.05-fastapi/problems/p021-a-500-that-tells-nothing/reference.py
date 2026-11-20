import logging
import secrets

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("tasks_api")


def create_app(new_id=None):
    if new_id is None:
        new_id = lambda: secrets.token_hex(8)          # a fresh random id each time
    app = FastAPI()

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        rid = new_id()
        # Not inside an except block, so hand the exception to the logger ourselves.
        logger.error("Unhandled error %s on %s %s", rid, request.method, request.url.path, exc_info=exc)
        body = {"error": {"code": "internal_error", "message": "Internal server error", "request_id": rid}}
        return JSONResponse(body, status_code=500, headers={"X-Request-ID": rid})

    @app.get("/tasks/{task_id}")
    def get_task(task_id: int):
        if task_id != 1:
            raise HTTPException(404, "Task not found")
        return {"id": 1, "title": "write chapter"}

    @app.get("/report")
    def report():
        raise RuntimeError("database refused login: password=hunter2")

    @app.get("/ratio")
    def ratio(a: int, b: int):
        return {"ratio": a / b}

    return app
