import json
import sqlite3
from contextlib import closing

import pytest

from solution import init_shop, place_order, relay


def counts(db):
    return (db.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0])


def jobs(queue):
    with closing(sqlite3.connect(queue.path)) as q:
        return q.execute("SELECT kind, payload, dedupe_key FROM jobs ORDER BY id").fetchall()


def test_tables(shop):
    init_shop(shop)
    init_shop(shop)                      # safe to call twice
    assert counts(shop) == (0, 0)


def test_order_and_outbox_row(shop, crash_at):
    init_shop(shop)
    oid = place_order(shop, "ada", 2500, crash_at(None))
    assert counts(shop) == (1, 1), "One order and one outbox row."
    kind, payload, sent = shop.execute("SELECT kind, payload, sent FROM outbox").fetchone()
    assert (kind, json.loads(payload), sent) == ("receipt", {"order_id": oid}, 0), \
        "The outbox row: kind 'receipt', payload {'order_id': <id>} as JSON, sent = 0."


def test_crash_between_saves_nothing(shop, crash_at, crash_type):
    init_shop(shop)
    with pytest.raises(crash_type):
        place_order(shop, "ada", 2500, crash_at("between"))
    assert counts(shop) == (0, 0), \
        "A crash between the two inserts must leave NOTHING: put both in one transaction and ROLLBACK on any BaseException."
    assert not shop.in_transaction, "After the crash the transaction must be rolled back, not left open."
    place_order(shop, "bo", 990, crash_at(None))
    assert counts(shop) == (1, 1), "The next order works normally after a rolled-back one."


def test_relay_moves_rows(shop, queue, crash_at):
    init_shop(shop)
    a = place_order(shop, "ada", 2500, crash_at(None))
    b = place_order(shop, "bo", 990, crash_at(None))
    assert relay(shop, queue, crash_at(None)) == 2
    assert jobs(queue) == [("receipt", json.dumps({"order_id": a}), "outbox:1"),
                           ("receipt", json.dumps({"order_id": b}), "outbox:2")], \
        f"Each outbox row becomes one job with dedupe_key 'outbox:<row id>'; got {jobs(queue)}"
    assert shop.execute("SELECT SUM(sent) FROM outbox").fetchone()[0] == 2, "Relayed rows are marked sent = 1."
    assert relay(shop, queue, crash_at(None)) == 0, "A second relay finds nothing unsent."
    assert len(jobs(queue)) == 2


def test_crash_after_enqueue_is_absorbed(shop, queue, crash_at, crash_type):
    init_shop(shop)
    place_order(shop, "ada", 2500, crash_at(None))
    with pytest.raises(crash_type):
        relay(shop, queue, crash_at("after-enqueue"))
    assert len(jobs(queue)) == 1, "The job reached the queue before the crash."
    assert shop.execute("SELECT sent FROM outbox").fetchone()[0] == 0, "...but the row was not marked: it will be relayed again."
    assert relay(shop, queue, crash_at(None)) == 1
    assert len(jobs(queue)) == 1, \
        "Relaying the same row again must NOT create a second job: enqueue with dedupe_key=f'outbox:{row id}'."
    assert shop.execute("SELECT sent FROM outbox").fetchone()[0] == 1


def test_relay_order(shop, queue, crash_at):
    init_shop(shop)
    for name in ("ada", "bo", "cy"):
        place_order(shop, name, 100, crash_at(None))
    relay(shop, queue, crash_at(None))
    keys = [k for _, _, k in jobs(queue)]
    assert keys == ["outbox:1", "outbox:2", "outbox:3"], "Relay rows in id order."
