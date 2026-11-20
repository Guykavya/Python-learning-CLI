## Hint 1

Map each chapter idea to a Celery name: "ack after the work" -> `acks_late`; "the worker died, put the task back" -> `reject_on_worker_lost`; "retry these errors" -> `autoretry_for`; "how many times" -> `max_retries`; "wait longer each time, with randomness" -> `retry_backoff`, `retry_jitter`. Some are app settings (`app.conf`, with a `task_` or `worker_` prefix), some are task options.

## Hint 2

```text
app.conf.update(task_serializer="json", accept_content=["json"], task_acks_late=True,
                task_reject_on_worker_lost=True, worker_prefetch_multiplier=1)

@app.task(bind=True, acks_late=True, reject_on_worker_lost=True, autoretry_for=(ProviderTimeout,),
          max_retries=5, retry_backoff=True, retry_jitter=True)
def send_welcome_email(self, user_id, to):
    return get_provider().send(to, "Welcome!", "Hello and welcome.", idempotency_key=f"welcome:{user_id}")
```
