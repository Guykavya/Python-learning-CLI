## Approach

Two atomic pieces. The business change and the "please send a receipt" note commit together (one transaction in one database). The relay copies notes to the queue with **at-least-once** semantics, and the dedupe key makes the queue side idempotent.

```python
def place_order(db, customer, total_cents, crash):
    db.execute("BEGIN IMMEDIATE")
    try:
        order_id = db.execute("INSERT INTO orders (customer, total_cents) VALUES (?, ?)",
                              (customer, total_cents)).lastrowid
        crash.hit("between")
        db.execute("INSERT INTO outbox (kind, payload) VALUES ('receipt', ?)", (json.dumps({"order_id": order_id}),))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise
    return order_id


def relay(db, queue, crash):
    rows = db.execute("SELECT id, kind, payload FROM outbox WHERE sent = 0 ORDER BY id").fetchall()
    relayed = 0
    for row_id, kind, payload in rows:
        queue.enqueue(kind, json.loads(payload), dedupe_key=f"outbox:{row_id}")
        crash.hit("after-enqueue")
        db.execute("UPDATE outbox SET sent = 1 WHERE id = ?", (row_id,))
        relayed += 1
    return relayed
```

## Cost

One extra row per business change, and a relay that polls (every second or so) or is triggered after commits. The receipt is delayed by up to one relay interval. A real broker without dedupe keys would deliver the rare duplicate to the consumer, which must then be idempotent (p022).

## Another way

When the queue lives **in the same database** (chapter 9), the outbox is not needed: `enqueue_in(db, ...)` writes the job row in the business transaction directly (chapter 11.7). **Change data capture** (reading the database's log, e.g. Debezium) is the heavy-duty version of the relay.
