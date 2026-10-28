## Approach

Rules used (chapter section on context managers):

1. `with A as x, B as y:` enters A, then B; it exits B, then A.
2. If the body raises, `__exit__` of the innermost manager runs first and receives the exception. If it returns a true value the exception stops there; the next manager out gets `None, None, None`; execution continues after that `with` statement.
3. A generator manager receives the exception at `yield`. `except KeyError` handles it (and swallows it if the generator then ends normally); `finally` always runs.

Walk through:

- **one**: no exception. `enter a`, `body A`, `exit a None`, `finished normally`.
- **two**: `enter a`, `enter b`, body prints `body A B`, then `ValueError`. Exits from the inside: `exit b ValueError`, `exit a ValueError`. Both return `False`, so the error escapes: `escaped ValueError`.
- **three**: `enter a`, `enter b`; `ValueError`; `exit b ValueError` returns `True`: swallowed. `after b` is printed, then `exit a None` (a sees no exception). Finished normally.
- **four**: `enter a`, `enter b`, `body`, `KeyError`. `exit b KeyError` (not swallowed), `exit a KeyError` returns `True`: swallowed. `never` is skipped; `after a` is printed; finished normally.
- **five**: `setup p`, `body pp`, the `KeyError` arrives at `yield`: `gen caught KeyError p`, then `cleanup p`; the generator ends normally, so the exception is swallowed; `after p`; finished normally.
- **six**: `setup q`, `body qq`, `ValueError` at `yield`: not a `KeyError`, so `cleanup q` runs and the error leaves the generator: `escaped ValueError`.

## Another way

Run the code, then change `swallow` flags one at a time and predict again.
