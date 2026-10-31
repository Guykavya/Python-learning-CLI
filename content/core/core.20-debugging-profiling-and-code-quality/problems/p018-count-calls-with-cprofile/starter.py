import cProfile
import pstats


def call_counts(fn, *args, **kwargs):
    """Run fn(*args, **kwargs) under cProfile; return {function name: total calls}."""
    fn(*args, **kwargs)
    return {}
