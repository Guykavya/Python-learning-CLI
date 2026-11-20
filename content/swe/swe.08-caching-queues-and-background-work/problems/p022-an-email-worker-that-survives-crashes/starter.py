import sqlite3
from contextlib import closing


def init_email_log(db_path):
    with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS email_log (key TEXT PRIMARY KEY, to_addr TEXT, state TEXT, provider_id TEXT)")


def make_safe_handler(db_path, provider, crash):
    # The NAIVE handler: no key, no record. Make it idempotent.
    def handler(payload, job):
        crash.hit("start")
        crash.hit("after-claim")
        provider.send(payload["to"], "Welcome!", "Hello and welcome.")
        crash.hit("after-send")
        crash.hit("after-record")
    return handler
