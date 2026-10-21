## Walkthrough

- `parse("12")` returns 12: `ok 12`.
- `parse("x")`: `int` raises `ValueError` (call it A). The handler raises a new `ValueError` (B)
  `from e`. B's `__cause__` is A; its `__context__` is **also** A (Python sets it automatically,
  because A was being handled); `from` sets `__suppress_context__` to `True`.
- `lookup`: the `KeyError` is being handled when the `LookupError` is raised `from None`. So
  `__cause__` is `None`, `__context__` is still the `KeyError`, and suppress is `True`. `from None`
  hides the context in printed tracebacks; it does not erase it.
- `careless([5])`: `values[3]` raises `IndexError`; the handler computes `5 / 0`, raising
  `ZeroDivisionError` while handling it. Implicit chaining: no cause, context `IndexError`,
  suppress `False`. A traceback would say "During handling of the above exception...".
- `careless([])`: `values[3]` raises `IndexError`; in the handler, `values[0]` raises a **second**
  `IndexError` whose context is the first.
- `relay(0)`: the handler prints and re-raises the **same** `ZeroDivisionError` with a bare
  `raise`. That exception was raised by `10 / x` when nothing else was being handled, so all
  three attributes are empty.

## The exact output

```text
ok 12
ValueError | not a number: x
  cause: ValueError
  context: ValueError
  suppress: True
LookupError | no entry for b
  cause: NoneType
  context: KeyError
  suppress: True
ZeroDivisionError | division by zero
  cause: NoneType
  context: IndexError
  suppress: False
IndexError | list index out of range
  cause: NoneType
  context: IndexError
  suppress: False
  relay saw it
ZeroDivisionError | division by zero
  cause: NoneType
  context: NoneType
  suppress: False
```
