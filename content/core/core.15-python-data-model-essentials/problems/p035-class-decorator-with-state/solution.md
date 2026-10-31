## Approach

A class-based decorator has two phases: `__init__(func)` runs once at decoration time, `__call__` runs at every call. All the memory sits on `self`. `functools.update_wrapper(self, func)` does what `@functools.wraps` does for function wrappers: it copies `__name__`, `__doc__`, `__module__` and sets `__wrapped__`.

The `try`/`except`/`raise` records failures without hiding them. `last_result` is a `@property`: computed on access, read without parentheses.

## Code

```python
import functools


class Recorder:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = []

    def __call__(self, *args, **kwargs):
        try:
            result = self.func(*args, **kwargs)
        except Exception as err:
            self.calls.append((args, kwargs, "error", err))
            raise
        self.calls.append((args, kwargs, "ok", result))
        return result

    @property
    def last_result(self):
        for _, _, status, value in reversed(self.calls):
            if status == "ok":
                return value
        raise LookupError("no successful call yet")

    def clear(self):
        self.calls.clear()

    def __repr__(self):
        return f"<Recorder {self.func.__name__}: {len(self.calls)} call(s)>"
```

## Complexity

O(1) per call (appending); memory grows with the number of calls. `last_result` is O(k) in the worst case.

## Another way

A function decorator with a closure: `calls = []` outside the `wrapper`, then `wrapper.calls = calls`. It is shorter, but properties and methods like `clear()` and `__repr__` are awkward to add, which is why the class wins once the decorator has behaviour of its own.
