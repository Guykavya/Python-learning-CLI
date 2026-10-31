# A line counter with settrace

`cProfile` tells you **which function** is slow. Sometimes you need to know **which line**:
`line_profiler` does that, and at its heart is the same idea you can build with the standard
library. `sys.settrace(tracer)` makes Python call `tracer(frame, event, arg)` whenever a new
function frame starts (`event == "call"`). If the tracer returns a **local trace function**, that
function is then called for every `"line"` event in that frame (and for `"return"` and
`"exception"`). `frame.f_code` is the code object being run and `frame.f_lineno` the current
line number.

Write `line_hits(fn, *args, **kwargs) -> dict[int, int]` in `solution.py`. It calls
`fn(*args, **kwargs)` and returns how many times each line **of `fn` itself** ran:

- Keys are **relative** line numbers: the `def` line is 1, the next line is 2, and so on.
  `fn.__code__.co_firstlineno` is the absolute line number of the `def`.
- Count only frames running `fn`'s own code (`frame.f_code is fn.__code__`). Lines of other
  functions that `fn` calls are **not** counted. If `fn` is recursive, the lines of all its frames
  are added together.
- Lines that never ran are simply missing from the dictionary.
- **Always restore the trace function that was installed before** (`sys.gettrace()`), even when
  `fn` raises; let the exception reach the caller. Debuggers and coverage tools use
  `sys.settrace` too, and setting it to `None` would silently switch them off.

**Example**

```python
def count_evens(numbers):      # 1
    evens = 0                  # 2
    for n in numbers:          # 3
        if n % 2 == 0:         # 4
            evens += 1         # 5
    return evens               # 6

line_hits(count_evens, [1, 2, 3, 4, 6])
# {2: 1, 3: 6, 4: 5, 5: 3, 6: 1}
```

Line 3 runs 6 times for 5 numbers: once per item plus one last time to find out the loop is
finished. (That final check is how Python 3.10+ reports `for` and `while` lines.)
