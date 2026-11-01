"""A line tracer built on sys.settrace."""

import sys
from collections import Counter


def trace_lines(func, *args, **kwargs):
    """Call func(*args, **kwargs) while recording every executed line.

    Returns (result, events). Each event is (function name, line number relative to the
    function's `def` line). Only code from the same file as func is recorded.
    """
    filename = func.__code__.co_filename
    events = []

    def local_tracer(frame, event, arg):
        if event == "line":
            code = frame.f_code
            events.append((code.co_name, frame.f_lineno - code.co_firstlineno))
        return local_tracer

    def global_tracer(frame, event, arg):
        # called with event "call" for every new frame (and every generator resume)
        if frame.f_code.co_filename == filename:
            return local_tracer
        return None  # do not trace library code

    previous = sys.gettrace()
    sys.settrace(global_tracer)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(previous)
    return result, events


def line_counts(events, name):
    """Counter {relative line: times executed} for the function called `name`."""
    return Counter(line for func_name, line in events if func_name == name)
