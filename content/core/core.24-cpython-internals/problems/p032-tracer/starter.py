"""A line tracer built on sys.settrace."""

import sys
from collections import Counter


def trace_lines(func, *args, **kwargs):
    """Call func(*args, **kwargs) while recording every executed line.

    Returns (result, events). Each event is (function name, line number relative to the
    function's `def` line). Only code from the same file as func is recorded.
    """
    events = []
    # TODO: a global tracer (for "call" events) and a local tracer (for "line" events),
    #       installed with sys.settrace and removed again afterwards
    result = func(*args, **kwargs)
    return result, events


def line_counts(events, name):
    """Counter {relative line: times executed} for the function called `name`."""
    return Counter()
