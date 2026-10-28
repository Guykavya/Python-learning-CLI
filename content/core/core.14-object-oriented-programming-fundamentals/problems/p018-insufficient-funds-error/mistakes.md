- Forgetting `super().__init__(message)`. Then `str(e)` is `"(200, 500)"` or empty, and tracebacks
  show no useful message.
- Passing the numbers to `super().__init__(balance, amount)`. `str(e)` becomes `"(200, 500)"`.
- Inheriting from `BaseException`. Then `except Exception:` does not catch it; that class is meant
  for things like `KeyboardInterrupt`.
- Returning an error object or a string instead of raising it. The caller's code keeps running as if
  all was fine.
- Subtracting before the check, so a failed withdraw still changes the balance.
