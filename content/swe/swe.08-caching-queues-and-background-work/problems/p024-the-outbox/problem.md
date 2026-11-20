# The outbox

Chapter section 11.7 (the outbox: enqueue in the same transaction as the business change). A shop saves an order and must send a receipt. If it saves the order and **then** enqueues the receipt job, a crash in between leaves an order with no receipt, for ever. If the broker is a different system from the database (Redis, RabbitMQ, or here: a queue in a **different** SQLite file), one transaction cannot cover both. The **outbox** solves it in two steps:

1. `place_order` writes the order **and** an outbox row in **one transaction** of the shop database.
2. A **relay** reads unsent outbox rows, enqueues each one to the queue, and marks it sent. A crash between "enqueue" and "mark" makes the relay enqueue the row again later; a **dedupe key** derived from the outbox row id absorbs that duplicate.

## What to write

```python
def init_shop(db): ...
def place_order(db, customer, total_cents, crash) -> int: ...      # the order id
def relay(db, queue, crash) -> int: ...                            # how many rows were relayed
```

- `init_shop` creates two tables (if they do not exist):
  `orders (id INTEGER PRIMARY KEY, customer TEXT, total_cents INTEGER)` and
  `outbox (id INTEGER PRIMARY KEY, kind TEXT, payload TEXT, sent INTEGER NOT NULL DEFAULT 0)`.
- `place_order`: `BEGIN IMMEDIATE`; insert the order; call `crash.hit("between")`; insert an outbox row with `kind="receipt"` and `payload=json.dumps({"order_id": <id>})`; `COMMIT`. If **anything** is raised (including the simulated crash, a `BaseException`), `ROLLBACK` and raise it again.
- `relay`: for each outbox row with `sent = 0`, in id order: `queue.enqueue(kind, json.loads(payload), dedupe_key=f"outbox:{id}")`, then `crash.hit("after-enqueue")`, then `UPDATE outbox SET sent = 1 WHERE id = ?`. Return the number of rows marked sent.

`db` is an autocommit connection (`isolation_level=None`) to the shop database, so `BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK` are statements you execute yourself. `queue` is the chapter's `JobQueue` in another file.

## Example

```python
init_shop(db)
place_order(db, "ada", 2500, CrashAt("between"))   # raises Crash; nothing was saved
place_order(db, "ada", 2500, CrashAt(None))        # the order id; 1 order and 1 outbox row in total
relay(db, queue, CrashAt("after-enqueue"))         # raises Crash: the job is in the queue, the row not marked
relay(db, queue, CrashAt(None))                    # 1: enqueued again, the dedupe key makes it the same job
```
