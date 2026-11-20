# A Celery task configured for crashes

Chapter sections 13.1 (how the concepts map), 13.2 (Celery) and "Try it: read the config". You built a queue by hand; now set the same knobs in **Celery**. Celery is installed in the course, but there is no broker (no Redis, no RabbitMQ), so the tests only **inspect the configuration** and run the task once in **eager** mode (`task_always_eager`: `.delay()` runs the task at once, in the same process).

## What to write

In `solution.py`:

1. `app = Celery("shop", broker="memory://")` with these settings in `app.conf`:

   | Setting | Value | Why (chapter) |
   |---|---|---|
   | `task_serializer` | `"json"` | never pickle |
   | `accept_content` | `["json"]` | refuse anything else |
   | `task_acks_late` | `True` | ack after the work: at-least-once (8.4) |
   | `task_reject_on_worker_lost` | `True` | requeue if the worker process dies mid-task |
   | `worker_prefetch_multiplier` | `1` | reserve one job at a time |

2. `class ProviderTimeout(Exception)`.
3. `def get_provider()`: returns the e-mail provider. Leave it raising `RuntimeError("no provider configured")`; the tests replace it.
4. A task `send_welcome_email(self, user_id, to)` declared with `@app.task(bind=True, ...)` and these options:
   `acks_late=True`, `reject_on_worker_lost=True`, `autoretry_for=(ProviderTimeout,)`, `max_retries=5`, `retry_backoff=True`, `retry_jitter=True`.
   It calls `get_provider().send(to, "Welcome!", "Hello and welcome.", idempotency_key=f"welcome:{user_id}")` and returns the message id. The **idempotency key** is what makes the late acks and retries safe (section 11).

## Example

```python
send_welcome_email.acks_late          # True
send_welcome_email.autoretry_for      # (ProviderTimeout,)
app.conf.task_always_eager = True     # (the tests do this)
send_welcome_email.delay(7, "ada@example.com").get()    # 'msg-1'
```

Note what the tests do **not** check: real retries. In eager mode, `autoretry_for` raises `celery.exceptions.Retry` instead of waiting and retrying (measured with Celery 5.7), so a retry can only be seen with a real broker and worker ("Try it on your machine" in section 13.2).
