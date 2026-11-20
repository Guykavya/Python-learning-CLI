from celery import Celery

app = Celery("shop", broker="memory://")
app.conf.update(
    task_serializer="json",
    accept_content=["json"],                 # never pickle
    task_acks_late=True,                     # ack AFTER the task runs: at-least-once
    task_reject_on_worker_lost=True,         # requeue if the worker process dies mid-task
    worker_prefetch_multiplier=1,            # reserve one job at a time
)


class ProviderTimeout(Exception):
    pass


def get_provider():
    raise RuntimeError("no provider configured")


@app.task(bind=True, acks_late=True, reject_on_worker_lost=True, autoretry_for=(ProviderTimeout,),
          max_retries=5, retry_backoff=True, retry_jitter=True)
def send_welcome_email(self, user_id, to):
    key = f"welcome:{user_id}"               # a business key: retries and duplicates send one e-mail
    return get_provider().send(to, "Welcome!", "Hello and welcome.", idempotency_key=key)
