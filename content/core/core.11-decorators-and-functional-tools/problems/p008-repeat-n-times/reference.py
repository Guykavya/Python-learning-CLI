from functools import wraps


def repeat(n):
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(n):
                results.append(func(*args, **kwargs))
            return results
        return wrapper

    return decorate
