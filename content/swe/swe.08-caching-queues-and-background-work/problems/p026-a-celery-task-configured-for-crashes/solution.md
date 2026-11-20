## Approach

```python
from celery import Celery

app = Celery("shop", broker="memory://")
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)


class ProviderTimeout(Exception):
    pass


def get_provider():
    raise RuntimeError("no provider configured")


@app.task(bind=True, acks_late=True, reject_on_worker_lost=True, autoretry_for=(ProviderTimeout,),
          max_retries=5, retry_backoff=True, retry_jitter=True)
def send_welcome_email(self, user_id, to):
    return get_provider().send(to, "Welcome!", "Hello and welcome.", idempotency_key=f"welcome:{user_id}")
```

How each setting maps to the queue you built:

| Celery | Your queue (chapter 9-12) |
|---|---|
| `acks_late` | `complete()` after the handler, not before: at-least-once |
| `reject_on_worker_lost` | an expired lease gives the job back |
| `worker_prefetch_multiplier=1` | `reserve()` one job at a time |
| `autoretry_for` + `max_retries` | `fail(retry_in=...)` until `max_attempts`, then dead |
| `retry_backoff`, `retry_jitter` | `backoff_delay` with jitter |
| the idempotency key | p022's business key |

## Cost

Late acks mean duplicates after crashes, which the idempotency key absorbs. Prefetch 1 lowers throughput for very short tasks (one broker round trip per task); raise it only for tasks that take milliseconds.

## Another way

`self.retry(exc=exc, countdown=...)` inside an `except` gives full control over which errors retry and how long to wait (for example honouring a provider's `Retry-After`). RQ (`Retry(max=3, interval=[10, 30, 60])`) and arq (`max_tries`, `Retry(defer=...)`) have the same knobs under other names (chapter 13.1).
