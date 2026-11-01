# A line tracer with `sys.settrace`

Debuggers (`pdb`) and coverage tools are written in Python on top of one hook:
`sys.settrace(tracer)`. The evaluation loop then calls your function at interesting moments,
handing it the current **frame**:

- For every **new frame** (a function call, and also every time a generator is resumed), the
  **global** trace function is called as `tracer(frame, "call", None)`. Whatever it returns
  becomes the **local** trace function for that frame; returning `None` means "do not trace this
  frame".
- The local trace function is called as `local(frame, event, arg)` with `"line"` before each new
  source line runs, and with `"return"` and `"exception"`. It must **return itself** (or another
  function) to keep receiving events for that frame.
- `sys.settrace(None)` switches tracing off; `sys.gettrace()` returns the current trace function.

Copy `starter.py` to `solution.py` and write:

**`trace_lines(func, *args, **kwargs)`** calls `func(*args, **kwargs)` with tracing on and
returns `(result, events)`. `events` is a list with one tuple per `"line"` event:
`(function name, line number relative to the def line)`, that is
`(frame.f_code.co_name, frame.f_lineno - frame.f_code.co_firstlineno)`. Rules:

- Trace every function called along the way (helpers, recursion, generators), but **only code
  from the same file as `func`** (compare `frame.f_code.co_filename` with
  `func.__code__.co_filename`), so the standard library is skipped.
- Save the trace function that was active before (a debugger or a coverage tool may have
  installed one) and put it back afterwards, **even if `func` raises**. The exception must still
  reach the caller.

**`line_counts(events, name)`** returns a `collections.Counter` `{relative line: times}` for
the events of the function called `name`.

**Example**

```python
def loop(n):
    total = 0
    for i in range(n):
        total += i
    return total

>>> result, events = trace_lines(loop, 3)
>>> result
3
>>> events          # Python 3.14; see the note below
[('loop', 1), ('loop', 2), ('loop', 3), ('loop', 2), ('loop', 3), ('loop', 2), ('loop', 3), ('loop', 2), ('loop', 4)]
>>> line_counts(events, "loop")[3]
3
```

**Version note.** Which lines produce an event is decided by the evaluation loop, and some
details differ between Python versions: whether the `for` line is reported once more when the
loop ends, or whether a generator's `yield` line is reported again when it resumes. The tests
only check what is the same on 3.11 to 3.14 (body lines, how often a plain loop body runs, the
order of calls), so do not filter or "fix" any events yourself; just record them all.
