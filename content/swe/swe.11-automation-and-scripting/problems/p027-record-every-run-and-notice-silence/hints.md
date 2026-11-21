## Hint 1

Which statement runs `fn()`, catches *its* failure, and still lets you write the status file in both cases? Put only `fn()` inside the `try`; build the dictionary around it. For the checker, order the questions from "worst" to "fine": no file at all, a failed last run, an old last run. Which subtraction of two `datetime`s gives an age you can compare with `timedelta(hours=max_age_hours)`?

## Hint 2

```text
run_job:
    clock = clock or (lambda: datetime.now(timezone.utc))
    Path(status_dir).mkdir(parents=True, exist_ok=True)
    start = clock(); status = {"job": name, "start": start.isoformat()}
    try: status.update(ok=True, result=fn(), error=None); code = 0
    except Exception as e: log.error("job %s failed: %s", name, e); status.update(ok=False, result=None, error=f"{type(e).__name__}: {e}"); code = 1
    status["end"] = clock().isoformat(); write_json_atomic(Path(status_dir) / f"{name}.json", status); return code
problem_with:
    if not exists: "never ran"; data = json.loads(...)
    if not data["ok"]: "failed"
    if now - datetime.fromisoformat(data["end"]) > timedelta(hours=max_age_hours): "stale"
    return None
```
