## Walkthrough

**`first`.** In every case `finally` prints **before** the caller prints the returned value,
because the function has not returned yet when `finally` runs.

- `n = 5`: no exception, no early return, so the `try` block reaches its end and `else` runs,
  returning `"from else"`.
- `n = 0`: `return "zero from try"` leaves the `try` block early, so `else` is **skipped**.
- `n = -5`: the `ValueError` is handled and the handler returns `"from except"`.

**`build`.** `return items, count` builds the tuple `(items, 1)` first. Then `finally` appends to
the **same** list object, which the tuple also refers to, and rebinds the local name `count` to
`2`, which does not affect the tuple. Result: `(['a', 'b'], 1)`.

**`override`.** The `return` in `finally` wins both times. For `"5"` it replaces the value `5`.
For `"five"` the `ValueError` is pending, and the `return` in `finally` throws it away: no
traceback, just `finally wins`. (This is why Python 3.14 warns about it.)

**The loop.** `finally` runs on every exit from the `try` block: normal (`i` 0 and 2), `continue`
(`i` 1, so no `body 1`), and `break` (`i` 3, which also ends the loop).

## The exact output

```text
  finally sees 5
from else
  finally sees 0
zero from try
  finally sees -5
from except
(['a', 'b'], 1)
finally wins
finally wins
body 0
finally 0
finally 1
body 2
finally 2
finally 3
loop done
```
