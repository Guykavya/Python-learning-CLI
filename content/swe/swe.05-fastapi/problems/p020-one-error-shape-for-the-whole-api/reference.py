from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
TASKS = {1: "write chapter"}


class NotFound(Exception):
    """Raised by the business logic when something does not exist."""

    def __init__(self, resource, item_id):
        super().__init__(f"{resource} {item_id} not found")
        self.resource = resource
        self.item_id = item_id


def envelope(status, code, message, details=None, headers=None):
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(body, status_code=status, headers=headers)


@app.exception_handler(NotFound)
async def not_found(request: Request, exc: NotFound):
    return envelope(404, "not_found", f"{exc.resource} {exc.item_id} not found")


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return envelope(exc.status_code, "http_error", str(exc.detail), headers=getattr(exc, "headers", None))


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    details = [{"loc": list(e["loc"]), "type": e["type"], "message": e["msg"]} for e in exc.errors()]
    return envelope(422, "validation_failed", "Request data is invalid", details)


class TaskIn(BaseModel):
    title: str
    priority: int = Field(3, ge=1, le=5)


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in TASKS:
        raise NotFound("Task", task_id)
    return {"id": task_id, "title": TASKS[task_id]}


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    return {"id": 2, "title": task.title, "priority": task.priority}


@app.get("/secret")
def secret():
    raise HTTPException(401, "Login required", headers={"WWW-Authenticate": "Bearer"})


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    raise HTTPException(409, "Task is locked")
