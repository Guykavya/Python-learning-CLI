## Approach

Three outcomes, three log calls, chosen by **how surprising** the outcome is:

- success: `DEBUG`, useful only when you are digging;
- a known data problem (zero): `WARNING`, a short line, no traceback;
- a bug-like surprise (wrong type): `logger.exception`, which is `ERROR` **plus the traceback**.

`try / except / else` keeps the success logging out of the `try`, so a bug in the logging line
cannot be mistaken for a division error.

## Code

```python
def safe_divide_all(pairs, logger) -> list:
    results = []
    for i, (a, b) in enumerate(pairs):
        try:
            q = a / b
        except ZeroDivisionError:
            logger.warning("pair %d: division by zero (%r / %r)", i, a, b)
            results.append(None)
        except TypeError:
            logger.exception("pair %d: cannot divide %r by %r", i, a, b)
            results.append(None)
        else:
            logger.debug("pair %d: %r / %r = %r", i, a, b, q)
            results.append(q)
    return results
```

Why lazy arguments? `logger.debug(f"... {q!r}")` builds the string **every time**, even when
DEBUG is switched off (the usual case in production), which is wasted work in a hot loop. With
`logger.debug("... %r", q)` the record keeps the template and the args, and formatting happens
only if a handler actually emits it. A side benefit: all records from this line share one
template, so a log viewer can count "how many division-by-zero warnings today".

## Complexity

O(n) for n pairs.

## Another way

`logger.error("...", i, a, b, exc_info=True)` is the same as `logger.exception(...)`. Use
`exc_info=True` when you want a traceback at a different level, for example
`logger.warning(..., exc_info=True)`.
