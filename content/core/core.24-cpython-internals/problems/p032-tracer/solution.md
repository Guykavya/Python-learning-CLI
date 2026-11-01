## Approach

`sys.settrace` has a two-level protocol. The **global** function is asked once per new frame
(`"call"`), and its return value decides whether and how that frame is traced. The **local**
function then receives the frame's `"line"`, `"return"` and `"exception"` events. So the filter
(same file?) goes into the global function, and the recording into the local one. Everything is
wrapped in `try`/`finally` so the previous trace function always comes back.

Generators work without extra code: every resume creates a new `"call"` event for the
generator's frame, the global function returns the local tracer again, and the body's line
events are recorded under the generator's name.

## Code

```python
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
```

## Complexity

Every executed line in the traced file costs one Python function call, so a traced program runs
many times slower (often 10x or more). Frames from other files cost one call of the global
function each. Memory: one tuple per line event.

## Another way

One callable object can serve as both the global and the local trace function, because it can
look at `event` and the frame itself:

```python
class Recorder:
    def __init__(self, filename):
        self.filename = filename
        self.events = []

    def __call__(self, frame, event, arg):
        code = frame.f_code
        if code.co_filename != self.filename:
            return None
        if event == "line":
            self.events.append((code.co_name, frame.f_lineno - code.co_firstlineno))
        return self
```

Since Python 3.12 there is also `sys.monitoring` (PEP 669), a lower-overhead API made for
debuggers and profilers: you register callbacks for specific events (such as `LINE`) for a tool
id, and CPython only pays for the events you asked for. `sys.settrace` itself is implemented on
top of it in 3.12+.
