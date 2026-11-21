## Approach

```python
def run_job(name, fn, status_dir, clock=None):
    clock = clock or (lambda: datetime.now(timezone.utc))
    Path(status_dir).mkdir(parents=True, exist_ok=True)
    start = clock()
    status = {"job": name, "start": start.isoformat()}
    log.info("job %s starting", name)
    try:
        status.update(ok=True, result=fn(), error=None)
        code = 0
    except Exception as e:
        log.error("job %s failed: %s", name, e)
        status.update(ok=False, result=None, error=f"{type(e).__name__}: {e}")
        code = 1
    status["end"] = clock().isoformat()
    write_json_atomic(Path(status_dir) / f"{name}.json", status)
    return code


def problem_with(status_file, max_age_hours, now):
    path = Path(status_file)
    if not path.exists():
        return "never ran"
    status = json.loads(path.read_text(encoding="utf-8"))
    if not status["ok"]:
        return "failed"
    if now - datetime.fromisoformat(status["end"]) > timedelta(hours=max_age_hours):
        return "stale"
    return None
```

The wrapper turns every run into a **record** (what, when, how long, result or error) and an **honest exit code**; the status file is written atomically so a crash during the write cannot leave a half file that the checker misreads. The checker is separate on purpose: it can run from another machine or a monitoring job, and it is the only way to catch "cron stopped", "the machine was off" or "someone deleted the crontab", because a job that never starts cannot report anything. Injecting the clock makes "more than 24 hours" exact in tests.

## Complexity

O(1) besides the job itself.

## Another way

Use a heartbeat service (section 13.2, for example Healthchecks.io): the job requests a URL on success, and the service alerts you when the ping does **not** arrive on time. That is the same dead-man's switch, run by someone else, so it also works when your whole machine is down. Many people do both: a local status file for details, a heartbeat for silence.
