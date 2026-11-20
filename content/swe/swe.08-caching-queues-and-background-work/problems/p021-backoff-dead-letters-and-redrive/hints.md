## Hint 1

`process_one` is the chapter's `Worker.run_once` with the error classes passed in. Which three outcomes does a handler call have (success, permanent error, other error), and which queue method does each one call? How do you know afterwards whether a failed job was buried?

## Hint 2

```text
job = queue.reserve(worker); if None: return None
try: handler(json.loads(job["payload"]))
except Exception as exc:
    text = f"{type(exc).__name__}: {exc}"
    if isinstance(exc, permanent): ok = queue.fail(job, text, permanent=True); return "dead" or "lease-lost"
    ok = queue.fail(job, text, retry_in=backoff_delay(job["attempts"], base, cap, rng))
    if not ok: return "lease-lost"
    return "dead" if queue.get(job["id"])["state"] == "dead" else "retry"
return "done" if queue.complete(job["id"], worker) else "lease-lost"
```

`isinstance(exc, ())` is `False`, so an empty `permanent` tuple means "nothing is permanent".
