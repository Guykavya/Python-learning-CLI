- Printing `body a` instead of `body A`. `as d` binds what `__aenter__` **returns** (`"A"`), not
  the `Door` object or its name.
- Forgetting `exit b ValueError` because the body raised. `__aexit__` runs whether the block
  ends normally or with an exception; that is the whole point of a context manager.
- Expecting the `KeyError` to crash the program. `__aexit__` returned `True`, which swallows it,
  so `after c` prints.
- Printing `generator cleanup` right after the `break`. A `break` leaves the async generator
  paused; its `finally` runs only at `aclose()`.
- Printing `generator finished` for `numbers(5)`. That line is after the loop inside the
  generator, and the generator never got there.
- Printing `exit b None`. The exception type is passed to `__aexit__`; it is `None` only when
  there was no exception.
