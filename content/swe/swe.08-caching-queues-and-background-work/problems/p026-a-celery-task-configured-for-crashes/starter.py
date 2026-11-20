from celery import Celery

app = Celery("shop", broker="memory://")
# TODO: app.conf.update(...) with the five settings


class ProviderTimeout(Exception):
    pass


def get_provider():
    raise RuntimeError("no provider configured")


@app.task(bind=True)                       # TODO: the crash-safety options
def send_welcome_email(self, user_id, to):
    # TODO: send with idempotency_key=f"welcome:{user_id}" and return the message id
    return None
