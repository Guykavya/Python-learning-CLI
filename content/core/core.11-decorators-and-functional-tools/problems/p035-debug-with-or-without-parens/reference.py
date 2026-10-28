from functools import wraps


def debug(func=None, *, prefix="DEBUG", log=None):
    def record(line):
        if log is None:
            print(line)
        else:
            log.append(line)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            parts = [repr(a) for a in args]
            parts += [f"{k}={v!r}" for k, v in kwargs.items()]
            call = f"{prefix}: {f.__name__}({', '.join(parts)})"
            try:
                result = f(*args, **kwargs)
            except Exception as err:
                record(f"{call} raised {type(err).__name__}")
                raise
            record(f"{call} -> {result!r}")
            return result
        return wrapper

    if func is None:
        return decorator
    if not callable(func):
        raise TypeError(
            f"debug() got {func!r} instead of a function. "
            f'To set the prefix, write @debug(prefix="{func}").'
        )
    return decorator(func)
