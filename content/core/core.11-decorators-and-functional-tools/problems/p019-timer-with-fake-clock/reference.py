import time
from functools import wraps


def timed(clock=time.perf_counter):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                wrapper.durations.append(clock() - start)
        wrapper.durations = []
        return wrapper
    return decorate


def report(func):
    name = func.__name__
    times = func.durations
    if not times:
        return f"{name}: no calls"
    return f"{name}: {len(times)} calls, total {sum(times):.3f}s, slowest {max(times):.3f}s"
