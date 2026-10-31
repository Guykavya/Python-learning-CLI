import tracemalloc


def peak_bytes(fn, *args, **kwargs):
    """Run fn(*args, **kwargs); return the peak bytes allocated above the starting level."""
    was_tracing = tracemalloc.is_tracing()
    if not was_tracing:
        tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        start_current, _ = tracemalloc.get_traced_memory()
        fn(*args, **kwargs)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        if not was_tracing:
            tracemalloc.stop()
    return max(0, peak - start_current)
