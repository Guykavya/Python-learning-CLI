from functools import wraps


def strip_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).strip()
    return wrapper
