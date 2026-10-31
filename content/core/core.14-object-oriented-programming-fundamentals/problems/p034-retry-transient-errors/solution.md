## Approach

**The hierarchy decides the behaviour.** The helper never looks at error messages. It catches one
class, `TransientError`. Every subclass (`Timeout`, `ConnectionReset`, ...) is caught too, because
`except` matches subclasses (chapter section 17). Everything else is not caught, so it leaves
`retry` exactly as it was raised.

**Giving up with the cause attached.** After the last attempt we raise our own `RetryExhausted`.
Its message tells the caller *what* happened (we gave up), and `from err` keeps *why*: the last real
error becomes `__cause__`, and the traceback prints both, joined by "The above exception was the
direct cause of the following exception" (section 18). We also store it as `last_error`, so code
can read it without knowing about `__cause__`.

**The custom exception with extra data** stores `attempts` and `last_error` and passes the message
up with `super().__init__(...)`, so `str(err)` works.

**The decorator** reuses `retry`. `lambda: func(*args, **kwargs)` packs one call with its arguments
into a function with no arguments, which is what `retry` expects. Each call of `wrapper` makes a new
lambda and starts a new loop, so each call gets its own attempts.

## Code

```python
import functools


class TransientError(Exception):
    """A failure that may go away if you try again."""


class PermanentError(Exception):
    """A failure that will not go away by trying again."""


class RetryExhausted(Exception):
    def __init__(self, attempts, last_error):
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"gave up after {attempts} attempts")


def retry(func, attempts=3, on_retry=None):
    if not isinstance(attempts, int) or attempts < 1:
        raise ValueError(f"attempts must be a whole number of at least 1, got {attempts!r}")
    for number in range(1, attempts + 1):
        try:
            return func()
        except TransientError as err:
            if number == attempts:
                raise RetryExhausted(attempts, err) from err
            if on_retry is not None:
                on_retry(number, err)


def retrying(attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry(lambda: func(*args, **kwargs), attempts)
        return wrapper
    return decorator
```

Note that `err` exists only inside the `except` block (Python deletes it when the block ends), which
is one more reason to raise `RetryExhausted` right there.

## Complexity

At most `attempts` calls of `func`, plus O(1) work per attempt.

## Another way

Real retry code waits between attempts, often longer each time ("exponential backoff":
`time.sleep(base * 2 ** (number - 1))`). The `on_retry` hook is the natural place for that, and
for logging. Instead of separate Transient/Permanent classes, some libraries put a flag on one
error class (`err.retryable = True`); the class-based version lets `except` do the sorting.
