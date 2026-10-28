from functools import wraps


def deprecated(message, log=None):
    def decorator(func):
        warned = False

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal warned
            if not warned:
                warned = True
                text = f"{func.__name__} is deprecated: {message}"
                if log is None:
                    print(text)
                else:
                    log.append(text)
            return func(*args, **kwargs)
        return wrapper
    return decorator
