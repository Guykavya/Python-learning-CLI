import logging
import secrets

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("tasks_api")


def create_app(new_id=None):
    app = FastAPI()

    # TODO: a catch-all handler for Exception that logs the traceback with a request id
    #       and answers a 500 envelope that contains only that id.

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
