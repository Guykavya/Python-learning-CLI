## Approach

Treat `async with` and `async for` exactly like their sync twins, and follow the program one
step at a time.

| Step | What happens | Printed |
|---|---|---|
| `async with Door("a") as d` | `__aenter__` prints, returns `"A"` | `enter a` |
| body | `d` is `"A"` | `body A` |
| block ends normally | `__aexit__(None, None, None)` | `exit a None` |
| `async with Door("b")` | | `enter b` |
| body | prints, then raises `ValueError` | `body b` |
| `__aexit__(ValueError, ...)` | returns `False` (not `KeyError`), so the error goes on | `exit b ValueError` |
| `except ValueError` | | `caught bad` |
| `async with Door("c")` | | `enter c` |
| body raises `KeyError` | `__aexit__` returns `True`: swallowed | `exit c KeyError` |
| next line runs | | `after c` |
| `numbers(2)`, first round | | `yield 0`, `got 0` |
| second round | | `yield 1`, `got 1` |
| third round | `range` ends, body finishes, `finally` runs, loop stops | `generator finished`, `generator cleanup` |
| `gen = numbers(5)`, two rounds | | `yield 0`, `got 0`, `yield 1`, `got 1` |
| `break` | generator stays **paused** at `yield 1`; no cleanup yet | |
| | | `after break` |
| `await gen.aclose()` | `GeneratorExit` at the paused `yield`, `finally` runs | `generator cleanup` |
| | | `closed` |

Two points worth remembering:

- `__aexit__` decides whether an exception survives. Returning `True` hides it, which is right
  only when you really handled it. `Door` hides every `KeyError`, which is why `after c` prints.
- `break` does **not** finish an async generator. Notice that `generator finished` is **not**
  printed for `numbers(5)`: the loop body never ran past `yield 1`. Only `aclose()` (or the
  event loop, much later, when it shuts down) runs the `finally`. If that `finally` closes a
  network connection, "much later" can mean a leak, so close generators you stop early, or use
  `contextlib.aclosing(gen)`.

## Output

```text
enter a
body A
exit a None
enter b
body b
exit b ValueError
caught bad
enter c
exit c KeyError
after c
yield 0
got 0
yield 1
got 1
generator finished
generator cleanup
yield 0
got 0
yield 1
got 1
after break
generator cleanup
closed
```

## Complexity

Not relevant: the program is a fixed sequence of steps.

## Another way

Write the same program with the sync versions (`__enter__`/`__exit__`, a plain generator and
`gen.close()`), remove the `await`s and run it. The output is identical, which shows that the
async forms change *how* each step waits, not the order of the steps.

`contextlib.aclosing(numbers(5))` used as `async with aclosing(numbers(5)) as gen:` calls
`aclose()` for you when the block ends, even after a `break`.
