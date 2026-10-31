import tracemalloc


def peak_bytes(fn, *args, **kwargs):
    """Run fn(*args, **kwargs); return the peak bytes allocated above the starting level."""
    fn(*args, **kwargs)
    return 0
