import json


def init_shop(db):
    db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, total_cents INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY, kind TEXT, payload TEXT, sent INTEGER NOT NULL DEFAULT 0)")


def place_order(db, customer, total_cents, crash):
    db.execute("BEGIN IMMEDIATE")
    try:
        order_id = db.execute("INSERT INTO orders (customer, total_cents) VALUES (?, ?)",
                              (customer, total_cents)).lastrowid
        crash.hit("between")
        db.execute("INSERT INTO outbox (kind, payload) VALUES ('receipt', ?)", (json.dumps({"order_id": order_id}),))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")                     # the order and its outbox row vanish TOGETHER
        raise
    return order_id


def relay(db, queue, crash):
    rows = db.execute("SELECT id, kind, payload FROM outbox WHERE sent = 0 ORDER BY id").fetchall()
    relayed = 0
    for row_id, kind, payload in rows:
        queue.enqueue(kind, json.loads(payload), dedupe_key=f"outbox:{row_id}")   # a repeat is absorbed
        crash.hit("after-enqueue")
        db.execute("UPDATE outbox SET sent = 1 WHERE id = ?", (row_id,))
        relayed += 1
    return relayed
