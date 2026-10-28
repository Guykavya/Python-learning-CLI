import functools


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


class RetryExhausted(Exception):
    def __init__(self, attempts, last_error):
        # TODO: store both and pass the message to the parent
        super().__init__("")


def retry(func, attempts=3, on_retry=None):
    # TODO: try up to `attempts` times, only for TransientError
    return func()


def retrying(attempts=3):
    def decorator(func):
        return func
    return decorator
