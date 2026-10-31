- `except Exception` in the loop. A `PermanentError` (or a bug like `KeyError`) is then retried
  again and again and finally hidden inside `RetryExhausted`.
- Calling the function `attempts + 1` times ("one try plus N retries"). Here `attempts` is the total
  number of calls.
- `raise RetryExhausted(...)` without `from err`. Python still records the error as `__context__`
  (because you are inside `except`), but `__cause__` stays `None`, and the traceback says "During
  handling of the above exception, another exception occurred", which sounds like a bug in `retry`.
- Saving the error in a variable and raising `RetryExhausted` after the loop, forgetting that the
  loop also ends on success. Return inside the `try` and raise inside the `except`.
- Calling `on_retry` after the last attempt too. Nothing is retried then.
- In the decorator, calling `retry(func, attempts)` and losing the arguments. `func` needs its
  `*args` and `**kwargs`; wrap the call in a `lambda`.
- Forgetting `functools.wraps`: every decorated function is then called `wrapper`.
