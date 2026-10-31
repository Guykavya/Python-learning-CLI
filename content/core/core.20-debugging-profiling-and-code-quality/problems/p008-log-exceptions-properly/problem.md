# Log exceptions properly

A batch job divides many pairs of numbers. Some pairs are bad. The job must **not** stop, but
the log must say exactly what went wrong, at the right level, so that whoever reads it later
can debug without re-running anything.

Write `safe_divide_all(pairs, logger) -> list` in `solution.py`. For each `(a, b)` at index `i`
(counting from 0), in order:

| Case | Result item | Log call (exactly this template and these args) |
|---|---|---|
| `a / b` works | the quotient | `logger.debug("pair %d: %r / %r = %r", i, a, b, q)` |
| `ZeroDivisionError` | `None` | `logger.warning("pair %d: division by zero (%r / %r)", i, a, b)` |
| `TypeError` (not numbers) | `None` | `logger.exception("pair %d: cannot divide %r by %r", i, a, b)` |

Rules that matter for debugging:

- **Lazy formatting.** Pass the values as **arguments** to the logging call; never build the
  text yourself with an f-string or `%`. The logger then formats only if the record is really
  emitted, and log tools can group records by their template.
- A division by zero is an **expected** data problem: a warning, no traceback.
- A `TypeError` is a **surprise**: `logger.exception(...)` logs at `ERROR` level **and attaches
  the traceback** (`exc_info`). Call it inside the `except` block.
- Any other exception is not handled here: let it propagate.

**Example**

```python
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
log = logging.getLogger("batch")

safe_divide_all([(6, 3), (1, 0), ("7", 2)], log)   # [2.0, None, None]
```

```text
DEBUG pair 0: 6 / 3 = 2.0
WARNING pair 1: division by zero (1 / 0)
ERROR pair 2: cannot divide '7' by 2
Traceback (most recent call last):
  File "/home/you/batch.py", line 9, in safe_divide_all
    q = a / b
        ~~^~~
TypeError: unsupported operand type(s) for /: 'str' and 'int'
```

(The traceback lines depend on your file and Python version.)
