import functools


class Retry:
    def __init__(self, times=3, exceptions=(Exception,)):
        if times < 1:
            raise ValueError("times must be at least 1")
        self.times = times
        self.exceptions = exceptions
        self.failures = 0

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, self.times + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions:
                    self.failures += 1
                    if attempt == self.times:
                        raise
        return wrapper
