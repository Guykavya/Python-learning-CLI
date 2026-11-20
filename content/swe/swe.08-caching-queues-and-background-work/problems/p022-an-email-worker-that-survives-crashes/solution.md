## Approach

Four defences, one per crash window (chapter 11.5):

| Crash after... | The retry... | Why only one e-mail |
|---|---|---|
| `start` | runs everything | nothing had happened |
| `after-claim` (`sending`) | sees `sending`, sends with the key | first real send |
| `after-send` | sees `sending`, sends again **with the same key** | the provider recognises the key and does not send |
| `after-record` (`sent`) | sees `sent` and returns | the log says it is done |
| lost response | `ProviderTimeout` is an ordinary error, the job retries with the same key | the provider recognises the key |
| a second job for the same user | uses the same **business key** | the log or the provider stops it |

```python
def make_safe_handler(db_path, provider, crash):
    def handler(payload, job):
        key = f"welcome:{payload['user_id']}"
        with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
            crash.hit("start")
            row = db.execute("SELECT state FROM email_log WHERE key = ?", (key,)).fetchone()
            if row and row[0] == "sent":
                return
            db.execute("INSERT OR IGNORE INTO email_log (key, to_addr, state) VALUES (?, ?, 'sending')",
                       (key, payload["to"]))
            crash.hit("after-claim")
            message_id = provider.send(payload["to"], "Welcome!", "Hello and welcome.", idempotency_key=key)
            crash.hit("after-send")
            db.execute("UPDATE email_log SET state = 'sent', provider_id = ? WHERE key = ?", (message_id, key))
            crash.hit("after-record")
    return handler
```

## Cost

One small table row per e-mail, one read and two writes per job, and a provider that supports idempotency keys. The proof costs a test that crashes at every point: here 5 + 3 scenarios in well under a second.

## Another way

If the provider has **no** idempotency key, the window between "send" and "record" cannot be closed. Then choose consciously (chapter 11.5): at-least-once (send, then record: a rare duplicate), at-most-once (record `sent` first, then send: a rare loss), or reconcile (record intent, then ask the provider "did message X go out?" before resending). For payments, insist on a provider with idempotency keys.
