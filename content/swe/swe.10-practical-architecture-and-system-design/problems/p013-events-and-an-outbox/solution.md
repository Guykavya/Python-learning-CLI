## Approach

```python
def assign_task(uow, task_id, user_id, now):
    with uow:
        task = uow.tasks.get(task_id)
        task.assign(user_id, is_member=uow.projects.is_member(task.project_id, user_id),
                    open_count=uow.tasks.open_count_for(user_id))
        uow.tasks.save(task)
        for kind, payload in drain_events(task):
            uow.outbox.add(kind, payload, now)
        uow.commit()
        return task


def dispatch(new_uow, handlers, now, limit=50):
    with new_uow() as uow:
        items = uow.outbox.pending(limit)
    delivered = failed = 0
    for item in items:
        try:
            with new_uow() as uow:
                handler = handlers.get(item.kind)
                if handler is not None:
                    handler(uow, item)
                uow.outbox.mark_sent(item.id, now)
                uow.commit()
            delivered += 1
        except Exception:
            failed += 1
    return delivered, failed
```

The guarantees (chapter 9.2), each one tested: a **rolled-back** request writes no outbox row, so no e-mail for a change that never happened (failure 1 of 9.1 fixed); a **failing provider** keeps the row pending and the client already got a success (failure 2 fixed); a **crash after commit** loses nothing, the row is in the database; a **crash after sending but before marking** sends again on the next run (at-least-once), which the **idempotency key** `outbox-<id>` turns into one e-mail. The unit of work (p009) is what makes "task and event, together or not at all" a property of the code instead of a hope.

## Cost

One extra table and a loop. The chapter's honest warnings (9.7): events make a program harder to follow ("why was this mail sent?" needs a search for the handler); delivery is at-least-once, so consumers must be idempotent; and with several dispatchers in parallel the order is not guaranteed (p014: claim the rows).

## Another way

Publish straight to a message broker after commit: you are back to the commit-then-send race. The outbox is also the **seam** for a future split (chapter 11.5): a relay copies outbox rows to a broker for other services, without changing the use case.
