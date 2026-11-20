## Hint 1

`dependency_overrides` can only replace something the endpoint **asks for**. Which two values does each endpoint fetch for itself today? Turn each into a parameter with `Depends(...)` (section 9.6 does exactly this for the clock).

## Hint 2

Make two aliases, `Today = Annotated[date, Depends(get_clock)]` and `AppSettings = Annotated[Settings, Depends(get_settings)]`, and add `today: Today, settings: AppSettings` to both endpoints. Then delete every `date.today()` and `os.environ` from the endpoint bodies. A small helper `is_overdue(due, today, settings)` keeps the rule in one place.

## Hint 3

```text
is_overdue(due, today, settings): return today > due + timedelta(days=settings.grace_days)

task_status(task_id, today: Today, settings: AppSettings):
    404 if missing
    return {"id", "title", "overdue": is_overdue(...), "days_left": (due - today).days}

overdue(today: Today, settings: AppSettings):
    return {"overdue": [i for i in sorted(TASKS) if is_overdue(TASKS[i]["due"], today, settings)]}
```
