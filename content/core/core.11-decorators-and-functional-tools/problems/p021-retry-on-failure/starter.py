import time
from functools import wraps


def retry(attempts, exceptions=(Exception,), delay=0.0, sleep=time.sleep):
    def decorator(func):
        return func
    return decorator
