# Events and an outbox

Chapter section 9 (events and the outbox). So far, assigning a task sends an e-mail from **inside** the service, before `commit()`. There are two failure modes, and neither order of "commit" and "send" is right: send first and a **rolled-back** change still e-mails the assignee; commit first and a failing provider breaks the request that **already saved** its data (the client retries and creates a duplicate). You cannot make a database commit and an e-mail send atomic: they are two different systems.

The idea (chapter 9.2): **save the intention, deliver it later.** In the **same transaction** that saves the task, also save a row in an **outbox** table: "someone should be told that this task was assigned". Because it is the same transaction, the row exists **if and only if** the change is saved. A separate step, the **dispatcher**, reads the pending rows and does the real work, then marks them sent. If sending fails, the row stays pending and is retried.

## What is given

In the starter: the domain errors, the event `TaskAssigned(assignee_id, title)` and `Task`, which **records** that event when `assign` succeeds (`task.events`), plus `drain_events(task)`, which takes the pending events out as `(kind, payload)` pairs, for example `("TaskAssigned", {"task_id": 1, "assignee_id": 1, "title": "Ship it"})`. A copy of a task never carries pending events.

The tests give your functions a **fake unit of work** (a transactional in-memory fake, as in chapter 7.3) with these members, used as a context manager:

```text
uow.tasks.get(task_id) -> Task (a copy; raises NotFound)     uow.tasks.save(task)     uow.tasks.open_count_for(user_id)
uow.projects.is_member(project_id, user_id)
uow.outbox.add(kind, payload, at)    uow.outbox.pending(limit=50) -> items with .id .kind .payload    uow.outbox.mark_sent(item_id, at)
uow.commit()
```

## What to write

```python
def assign_task(uow, task_id, user_id, now) -> Task: ...
def dispatch(new_uow, handlers, now, limit=50) -> tuple[int, int]: ...
```

**`assign_task`**: the use case. Inside `with uow:` load the task, let the task decide (`task.assign(user_id, is_member=..., open_count=...)`; the facts come from the repositories), save it, write **every pending event of the task to the outbox** with `uow.outbox.add(kind, payload, now)`, and `uow.commit()` **once, at the end**. Return the task. It **sends nothing** and never touches e-mail. A rule violation or a failed commit must leave **no task change and no outbox row**: both succeed or neither does.

**`dispatch(new_uow, handlers, now, limit=50)`**: `new_uow()` returns a fresh unit of work; `handlers` maps an event kind to a function `handler(uow, item)`. Read the pending items (at most `limit`, in order) in one unit of work. Then deliver **each item in its own unit of work**: call its handler (an item whose kind has **no** handler is simply marked sent), `uow.outbox.mark_sent(item.id, now)`, `uow.commit()`. If the handler (or the commit) raises, **nothing of that item's unit of work is saved**, the item **stays pending** for the next run, and the loop **continues** with the next item: one bad item must not block the others. Return `(delivered, failed)`.

## Example

```python
assign_task(uow, 1, 1, now)                       # task 1 assigned to user 1; the outbox now holds one TaskAssigned
dispatch(new_uow, {"TaskAssigned": on_assigned}, now)     # (1, 0): the handler sent the e-mail; the item is marked sent
dispatch(new_uow, {"TaskAssigned": on_assigned}, now)     # (0, 0): nothing pending
```

Guarantees (chapter 9.2): a rolled-back request publishes nothing; a crash after commit loses nothing (the row is in the database); a crash after **sending** but before marking sent sends the event **again** on the next run: this is **at-least-once**, so the handler must be idempotent (the tests use an idempotency key `outbox-<item id>`).
