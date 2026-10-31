## Approach

`sys.settrace` installs a **global** trace function that Python calls on every new frame. If it
returns a function, that **local** trace function receives the `"line"` events of that frame.

1. Remember `code = fn.__code__` and an empty `hits` dictionary.
2. Global tracer: return the local tracer only when `frame.f_code is code`, otherwise `None`
   (so other functions run untraced and fast).
3. Local tracer: on `"line"`, add 1 to `hits[f_lineno - co_firstlineno + 1]`; always return
   itself so it keeps receiving events.
4. Save the old tracer, install yours, call `fn` inside `try`, restore in `finally`.

## Code

```python
import sys


def line_hits(fn, *args, **kwargs):
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
```

## Complexity

One Python function call per executed line of `fn`, so `fn` runs many times slower (often 10x
to 50x) while traced. That is why line profilers are used on one function at a time, after
`cProfile` has shown which function deserves it.

## Another way

Python 3.12 added `sys.monitoring`, a faster event API designed for profilers and coverage.
You register a tool id and a callback for `sys.monitoring.events.LINE` and enable it only for
`fn.__code__` with `sys.monitoring.set_local_events`. It does not clash with `sys.settrace`
users, but it does not exist on 3.11.
