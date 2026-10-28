# deprecated: warn once per function

When a library wants people to stop using an old function, it marks it as **deprecated**: the
function still works, but it tells the caller to switch. Printing the warning on every call is
noisy, so we warn **only on the first call**.

Write `deprecated(message, log=None)` in `solution.py`. It is a decorator factory:

- On the **first** call of the decorated function, record the text
  `"<name> is deprecated: <message>"`, where `<name>` is the function's `__name__`.
  - If `log` is a list, append the text to it.
  - If `log` is `None`, `print` the text instead.
- Later calls record nothing.
- Every call still runs the original function with all its arguments and returns its result.
- The warning is recorded **before** the function runs, so it appears even if the first call raises.
- Each decorated function warns **once on its own**. If the same `deprecated(...)` result is used
  on two functions, each of them warns on its own first call.
- Keep the metadata with `functools.wraps`.

**Example**

```python
log = []

@deprecated("use area_v2", log)
def area(w, h):
    return w * h

area(2, 3)     # 6
area(4, 5)     # 20
log            # ["area is deprecated: use area_v2"]   only one line
```
