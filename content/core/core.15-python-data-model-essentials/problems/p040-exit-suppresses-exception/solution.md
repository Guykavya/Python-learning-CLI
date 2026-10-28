## Approach

`__exit__` is the only place where a context manager can stop an exception: returning a true value tells Python "I handled it, continue after the `with`". The standard library's `contextlib.suppress` is exactly `Ignore` without the bookkeeping.

`Expect` shows a second use of `__exit__`: it can raise a *new* exception (the `AssertionError`) when the block behaved wrongly. `pytest.raises` works in the same way.

## Code

```python
class Ignore:
    def __init__(self, *exc_types):
        self.exc_types = exc_types
        self.exception = None

    def __enter__(self):
        self.exception = None
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None and issubclass(exc_type, self.exc_types):
            self.exception = exc
            return True
        return False

    @property
    def caught(self):
        return self.exception is not None


class Expect:
    def __init__(self, exc_type):
        self.exc_type = exc_type
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            raise AssertionError(f"expected {self.exc_type.__name__}, but nothing was raised")
        if issubclass(exc_type, self.exc_type):
            self.exception = exc
            return True
        return False
```

## Complexity

O(1) for both.

## Another way

`contextlib.suppress(KeyError, ValueError)` for the simple case; a `@contextmanager` generator with `try: yield ... except types as err: ...` (note that a generator-based manager swallows by simply not re-raising).
