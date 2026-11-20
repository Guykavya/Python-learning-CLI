import json


def init_shop(db):
    db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, total_cents INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY, kind TEXT, payload TEXT, sent INTEGER NOT NULL DEFAULT 0)")


def place_order(db, customer, total_cents, crash):
    # Two steps, no transaction: a crash in between leaves an order without a receipt. Fix it.
    order_id = db.execute("INSERT INTO orders (customer, total_cents) VALUES (?, ?)", (customer, total_cents)).lastrowid
    crash.hit("between")
    db.execute("INSERT INTO outbox (kind, payload) VALUES ('receipt', ?)", (json.dumps({"order_id": order_id}),))
    return order_id


def relay(db, queue, crash):
    # TODO: enqueue every unsent outbox row with a dedupe key, then mark it sent
    return 0
