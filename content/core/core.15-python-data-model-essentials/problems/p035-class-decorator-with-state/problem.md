# A class-based decorator that records calls

When a decorator needs to **remember things** (a history, a counter, a cache), a class is often
clearer than a closure: the memory is in attributes you can inspect. Write `Recorder` in
`solution.py`, used as `@Recorder` above a function.

- Every call to the decorated function is recorded in the list `calls` as a 4-tuple:
  `(args, kwargs, status, value)`. `status` is `"ok"` and `value` is the result, or `status` is
  `"error"` and `value` is the exception object. The result is returned, or the exception is
  **raised again** unchanged.
- `last_result` (a property): the result of the most recent **successful** call. If there has been
  none, raise `LookupError`.
- `clear()` empties `calls`.
- The decorated object keeps the function's `__name__`, `__doc__` and `__wrapped__` (use
  `functools.update_wrapper(self, func)` in `__init__`).
- `repr`: `<Recorder add: 2 call(s)>` (the function's name and how many calls were recorded).
- Every decorated function has its own `calls`.

**Example**

```python
@Recorder
def add(a, b=0):
    return a + b

add(1, 2)
add(5, b=1)
add.calls        # [((1, 2), {}, 'ok', 3), ((5,), {'b': 1}, 'ok', 6)]
add.last_result  # 6
add              # <Recorder add: 2 call(s)>
add.__name__     # 'add'
```
