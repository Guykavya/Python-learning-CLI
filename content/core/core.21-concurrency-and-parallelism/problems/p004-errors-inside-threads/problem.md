# Catch errors that happen inside threads

If a function raises inside a thread, the exception does **not** travel back to the code that
called `start()` or `join()`. Python prints a traceback (through `threading.excepthook`), the
thread dies, and `join()` returns normally as if nothing happened. The caller never learns
that the work failed.

Write `run_and_collect(funcs)`:

- `funcs` is a list of functions that take **no arguments**.
- Run each one in its **own thread**, all at the same time (start all, then join all).
- Return a list with one entry per function, **in input order**:
  - `("ok", value)` if the function returned `value`;
  - `("error", exc)` if it raised, where `exc` is the **exception object itself** (not its
    message, not its type).
- One failing function must not stop the others.

Catch `Exception` (not `BaseException`): things like `KeyboardInterrupt` should still behave
normally.

**Example**

```python
def ok():
    return 42

def bad():
    raise ValueError("no data")

result = run_and_collect([ok, bad, lambda: "hi"])
print(result)
print(type(result[1][1]).__name__, result[1][1])
```

```text
[('ok', 42), ('error', ValueError('no data')), ('ok', 'hi')]
ValueError no data
```

`starter.py` is a first attempt that stores only successes. Run it on the example: you will
see a traceback printed by the thread, yet `run_and_collect` returns `None` for `bad` and
gives no sign that anything went wrong.
