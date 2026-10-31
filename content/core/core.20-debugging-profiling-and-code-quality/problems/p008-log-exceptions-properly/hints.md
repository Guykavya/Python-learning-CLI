## Hint 1

Put the division in a `try` with two `except` clauses, one per exception type. Where must
`logger.exception` be called for it to find the traceback? What is the difference between
`logger.error(...)` and `logger.exception(...)`?

## Hint 2

Compare `logger.warning(f"pair {i}: ...")` with `logger.warning("pair %d: ...", i)`. In the
second, the record stores the template in `record.msg` and the values in `record.args`. Tests
(and log tools) can see the difference.

```
results = []
for i, (a, b) in enumerate(pairs):
    try:
        q = a / b
    except ZeroDivisionError:
        logger.warning(TEMPLATE_ZERO, i, a, b); results.append(None)
    except TypeError:
        logger.exception(TEMPLATE_TYPE, i, a, b); results.append(None)
    else:
        logger.debug(TEMPLATE_OK, i, a, b, q); results.append(q)
return results
```
