import sqlite3
from contextlib import closing


def init_email_log(db_path):
    with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS email_log (key TEXT PRIMARY KEY, to_addr TEXT, state TEXT, provider_id TEXT)")


def make_safe_handler(db_path, provider, crash):
    def handler(payload, job):
        key = f"welcome:{payload['user_id']}"              # a BUSINESS key: the thing done, not the job
        with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
            crash.hit("start")
            row = db.execute("SELECT state FROM email_log WHERE key = ?", (key,)).fetchone()
            if row and row[0] == "sent":
                return                                      # a duplicate delivery: already done
            db.execute("INSERT OR IGNORE INTO email_log (key, to_addr, state) VALUES (?, ?, 'sending')",
                       (key, payload["to"]))
            crash.hit("after-claim")
            message_id = provider.send(payload["to"], "Welcome!", "Hello and welcome.", idempotency_key=key)
            crash.hit("after-send")
            db.execute("UPDATE email_log SET state = 'sent', provider_id = ? WHERE key = ?", (message_id, key))
            crash.hit("after-record")
    return handler
