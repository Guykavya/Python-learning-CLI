import cProfile
import pstats


def call_counts(fn, *args, **kwargs):
    """Run fn(*args, **kwargs) under cProfile; return {function name: total calls}."""
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        fn(*args, **kwargs)
    finally:
        profiler.disable()
    counts = {}
    for (filename, _line, name), (_primitive, total, *_rest) in pstats.Stats(profiler).stats.items():
        if filename == "~":  # built-in functions and methods
            continue
        counts[name] = counts.get(name, 0) + total
    return counts
