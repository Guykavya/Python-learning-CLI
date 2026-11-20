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


Today = Annotated[date, Depends(get_clock)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def is_overdue(due: date, today: date, settings: Settings) -> bool:
    return today > due + timedelta(days=settings.grace_days)


@app.get("/tasks/{task_id}/status")
def task_status(task_id: int, today: Today, settings: AppSettings):
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    task = TASKS[task_id]
    return {
        "id": task_id,
        "title": task["title"],
        "overdue": is_overdue(task["due"], today, settings),
        "days_left": (task["due"] - today).days,
    }


@app.get("/overdue")
def overdue(today: Today, settings: AppSettings):
    return {"overdue": [i for i in sorted(TASKS) if is_overdue(TASKS[i]["due"], today, settings)]}
