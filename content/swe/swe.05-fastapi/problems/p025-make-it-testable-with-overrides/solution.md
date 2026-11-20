## Approach

```python
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
```

The change is small, but it moves **who decides** the date and the settings: before, the endpoint decided; now the caller (FastAPI in production, the test in tests) decides. That is dependency injection.

Example: the test installs `date(2020, 1, 15)` and `Settings(grace_days=7)`. For task 1: `due + 7 days` is 2020-01-17; 2020-01-15 is not after it, so `overdue` is `False`; `days_left` is `(2020-01-10 − 2020-01-15).days = -5`. The answer is the same next year, on any machine, whatever `GRACE_DAYS` says.

In production nothing changes: no override is installed, so FastAPI calls the real `get_clock()` and `get_settings()` for each request.

## Complexity

O(n) for `/overdue` over n tasks, O(1) for one task.

## Another way

Inject one object that holds both: a `Context` dependency returning `{"today": ..., "settings": ...}`. Fewer parameters, but a test that only wants to change the date must now build the whole context. Small, separate dependencies are easier to override one at a time.
