import sys


def line_hits(fn, *args, **kwargs):
    """Call fn(*args, **kwargs); return {relative line number: times it ran} for fn's own lines."""
    code = fn.__code__
    hits = {}

    def local_tracer(frame, event, arg):
        if event == "line":
            rel = frame.f_lineno - code.co_firstlineno + 1
            hits[rel] = hits.get(rel, 0) + 1
        return local_tracer

    def global_tracer(frame, event, arg):
        if frame.f_code is code:
            return local_tracer
        return None

    old = sys.gettrace()
    sys.settrace(global_tracer)
    try:
        fn(*args, **kwargs)
    finally:
        sys.settrace(old)
    return hits
