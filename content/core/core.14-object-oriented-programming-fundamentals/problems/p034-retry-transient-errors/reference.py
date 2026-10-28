import functools


class TransientError(Exception):
    """A failure that may go away if you try again."""


class PermanentError(Exception):
    """A failure that will not go away by trying again."""


class RetryExhausted(Exception):
    def __init__(self, attempts, last_error):
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"gave up after {attempts} attempts")


def retry(func, attempts=3, on_retry=None):
    if not isinstance(attempts, int) or attempts < 1:
        raise ValueError(f"attempts must be a whole number of at least 1, got {attempts!r}")
    for number in range(1, attempts + 1):
        try:
            return func()
        except TransientError as err:
            if number == attempts:
                raise RetryExhausted(attempts, err) from err
            if on_retry is not None:
                on_retry(number, err)


def retrying(attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry(lambda: func(*args, **kwargs), attempts)
        return wrapper
    return decorator
