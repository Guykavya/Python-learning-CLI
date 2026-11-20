import os
from datetime import date, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

TASKS = {
    1: {"title": "pay rent", "due": date(2020, 1, 10)},
    2: {"title": "file taxes", "due": date(2020, 1, 20)},
    3: {"title": "renew passport", "due": date(2020, 3, 1)},
}


class Settings(BaseModel):
    grace_days: int = 0


def get_clock() -> date:
    return date.today()


def get_settings() -> Settings:
    return Settings(grace_days=int(os.environ.get("GRACE_DAYS", "0")))


# TODO: the endpoints below read the clock and the environment directly.
#       Make them receive both through Depends(get_clock) and Depends(get_settings).

@app.get("/tasks/{task_id}/status")
def task_status(task_id: int):
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    today = date.today()
    grace = int(os.environ.get("GRACE_DAYS", "0"))
    task = TASKS[task_id]
    return {
        "id": task_id,
        "title": task["title"],
        "overdue": today > task["due"] + timedelta(days=grace),
        "days_left": (task["due"] - today).days,
    }


@app.get("/overdue")
def overdue():
    today = date.today()
    grace = int(os.environ.get("GRACE_DAYS", "0"))
    return {"overdue": [i for i in sorted(TASKS) if today > TASKS[i]["due"] + timedelta(days=grace)]}
