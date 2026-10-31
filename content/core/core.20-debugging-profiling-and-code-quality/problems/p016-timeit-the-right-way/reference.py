import time


def best_time(fn, number, repeat, timer=time.perf_counter):
    """Return the fastest per-call time (seconds) over `repeat` batches of `number` calls."""
    if number < 1 or repeat < 1:
        raise ValueError("number and repeat must be at least 1")
    per_call = []
    for _ in range(repeat):
        start = timer()
        for _ in range(number):
            fn()
        end = timer()
        per_call.append((end - start) / number)
    return min(per_call)
