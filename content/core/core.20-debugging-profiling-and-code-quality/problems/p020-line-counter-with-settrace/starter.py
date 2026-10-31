import sys


def line_hits(fn, *args, **kwargs):
    """Call fn(*args, **kwargs); return {relative line number: times it ran} for fn's own lines."""
    fn(*args, **kwargs)
    return {}
