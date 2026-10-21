## Hint 1

`show(parse, "12")` raises nothing. For `parse("x")`: which exception is being handled when the
new `ValueError` is raised, and what does `from e` add on top of that?

## Hint 2

`from None` sets `__cause__` to `None` and `__suppress_context__` to `True`, but Python still
records `__context__` automatically. It is only hidden when a traceback is printed.

## Hint 3

`careless([5])`: `values[3]` fails, and the handler's `values[0] / 0` raises a new exception while
the `IndexError` is being handled. `careless([])`: the handler's `values[0]` fails too, so the new
exception is **another** `IndexError`. A bare `raise` re-raises the original object, which was not
raised during the handling of anything else.
