## Hint 1

What must be true after a crash at `"between"`? If the order exists, the outbox row must exist too, and if not, neither. Which database feature makes two inserts succeed or fail together? And for the relay: after a crash between "enqueue" and "mark sent", the row is relayed again. What makes the second enqueue harmless?

## Hint 2

```text
place_order:
    BEGIN IMMEDIATE
    try:   insert order; crash.hit("between"); insert outbox row; COMMIT
    except BaseException: ROLLBACK; raise
relay:
    for (id, kind, payload) in SELECT ... WHERE sent = 0 ORDER BY id:
        queue.enqueue(kind, json.loads(payload), dedupe_key=f"outbox:{id}")
        crash.hit("after-enqueue")
        UPDATE outbox SET sent = 1 WHERE id = ?
```

`except Exception` would miss the simulated crash: it is a `BaseException`.
