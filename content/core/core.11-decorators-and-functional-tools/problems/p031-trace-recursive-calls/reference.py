from functools import wraps


def trace_calls(log):
    def decorator(func):
        depth = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal depth
            indent = "  " * depth
            parts = [repr(a) for a in args]
            parts += [f"{k}={v!r}" for k, v in kwargs.items()]
            log.append(f"{indent}{func.__name__}({', '.join(parts)})")
            depth += 1
            try:
                result = func(*args, **kwargs)
            except Exception as err:
                log.append(f"{indent}!! {type(err).__name__}")
                raise
            finally:
                depth -= 1
            log.append(f"{indent}-> {result!r}")
            return result
        return wrapper
    return decorator
