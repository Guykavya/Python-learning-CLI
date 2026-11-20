# Make it testable with overrides

Chapter sections 9.1 (dependencies) and 9.6 (`dependency_overrides`, the injected clock).

The starter's API works, but nobody can test it: both endpoints call `date.today()` and read the environment variable `GRACE_DAYS` **inside** the endpoint. A test written today ("task 2 is not overdue") fails next month, and a test cannot change the grace period without changing the real environment.

Refactor it so that the endpoints **receive** the date and the settings:

1. `get_clock()` returns `date.today()`.
2. `Settings` is a Pydantic model with one field `grace_days: int = 0`. `get_settings()` returns `Settings(grace_days=int(os.environ.get("GRACE_DAYS", "0")))`.
3. Both endpoints take `today: Annotated[date, Depends(get_clock)]` and `settings: Annotated[Settings, Depends(get_settings)]`, and use **only** those. No `date.today()` and no `os.environ` inside an endpoint.

The rules of the API stay the same:

- A task is **overdue** when `today > due + grace_days` days (on the last day of the grace period it is not overdue yet).
- `days_left = (due - today).days` (negative when the due date has passed; the grace period does not change it).
- `GET /tasks/{task_id}/status` → `{"id", "title", "overdue", "days_left"}`, or 404 `{"detail": "Task not found"}`.
- `GET /overdue` → `{"overdue": [ids of overdue tasks, in increasing order]}`.

The tasks (in the starter): 1 "pay rent" due 2020-01-10, 2 "file taxes" due 2020-01-20, 3 "renew passport" due 2020-03-01.

## Example

The tests set `app.dependency_overrides[get_clock] = lambda: date(2020, 1, 15)` and `app.dependency_overrides[get_settings] = lambda: Settings(grace_days=0)`:

```text
GET /tasks/1/status -> {"id": 1, "title": "pay rent",   "overdue": true,  "days_left": -5}
GET /tasks/2/status -> {"id": 2, "title": "file taxes", "overdue": false, "days_left": 5}
GET /overdue        -> {"overdue": [1]}
```

With `Settings(grace_days=7)` on the same day, task 1 is not overdue yet (2020-01-15 is not after 2020-01-17), so `/overdue` gives `[]`.

The tests import `app`, `get_clock`, `get_settings` and `Settings`, and clear the overrides after every test.
