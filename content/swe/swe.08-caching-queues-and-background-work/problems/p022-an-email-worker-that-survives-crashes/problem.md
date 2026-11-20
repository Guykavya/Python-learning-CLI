# An e-mail worker that survives crashes

Chapter sections 11.2 to 11.5. This is the module's outcome: **a worker that gives the same result when a task runs twice.** Write a handler for "welcome e-mail" jobs such that **each user gets exactly one e-mail**, whatever happens: the worker dies at any point, the provider loses its answer, the same job is enqueued twice.

## What you get

- `provider.send(to, subject, body, idempotency_key=None)` returns a message id. Like real e-mail APIs it **honours an idempotency key**: a second call with the same key sends nothing and returns the first message id. It can also fail in the nastiest way: **send the message and then raise `ProviderTimeout`** (the response was lost).
- `crash.hit(name)` is a test hook: it may raise `Crash` at that point, which stands for **the process dying**. `Crash` derives from `BaseException`, so `except Exception` does not catch it. Never catch it.
- The job payload: `{"user_id": 7, "to": "ada@example.com"}`. Your handler is called as `handler(payload, job)`.

## What to write

```python
def init_email_log(db_path): ...                         # create the table email_log
def make_safe_handler(db_path, provider, crash): ...     # returns handler(payload, job)
```

The table: `email_log (key TEXT PRIMARY KEY, to_addr TEXT, state TEXT, provider_id TEXT)`.

The handler must call `crash.hit(...)` at exactly these four points, in this order, so the tests can kill it there:

| Point | Where |
|---|---|
| `"start"` | first thing, before reading anything |
| `"after-claim"` | after recording the intent to send (state `sending`) |
| `"after-send"` | after `provider.send` returned |
| `"after-record"` | after marking the log `sent` |

The rules from the chapter, each aimed at a crash window:

1. Use a **business key**, `welcome:<user_id>`: it names the thing done, so two different jobs for the same e-mail share it. (The job id would not.)
2. If the log already says `sent` for this key, return at once (a duplicate delivery).
3. Record the intent (`INSERT OR IGNORE ... state 'sending'`) before sending.
4. Pass the key to `provider.send(..., idempotency_key=key)`, so a retry after a crash (or a lost response) cannot send a second message.
5. Then mark the log `sent` with the provider's message id.

Subject `"Welcome!"`, body `"Hello and welcome."`. Open the database with `sqlite3.connect(db_path, isolation_level=None)` and close it.

## Example

The tests run the chapter's harness: a first worker runs the job and is killed at a point; time passes, the lease expires, and a second worker drains the queue.

```text
scenario                                   e-mails received
no crash                                   1
crash after the send, before the record    1
provider loses the response once           1
the same job was enqueued twice            1
enqueued twice AND a crash after the send  1
```

The handler in the starter is the chapter's naive one: it sends 2 e-mails in three of those scenarios.
