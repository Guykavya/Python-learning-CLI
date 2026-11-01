# Null object: kill the None checks

In `starter.py` every use of the optional `logger` and `cache` is guarded:
`if logger is not None: logger.info(...)`, `if cache is not None: ...`. The checks are noise,
easy to forget (one forgotten check is an `AttributeError` in production), and they hide the
real logic.

The **null object pattern** replaces "no collaborator" (`None`) with a collaborator that
**does nothing**. The call sites then always just call it.

Copy `starter.py` to `solution.py`. Keep `DictCache`, `PRICES` and `_price` as they are, and:

- Add `NullLogger` with methods `info(message)` and `error(message)` that do nothing.
- Add `NullCache` with `get_or_compute(key, compute)` that just returns `compute()` (it
  remembers nothing).
- Change `price_order_lines(orders, logger=..., cache=...)` and `order_total(orders, logger=..., cache=...)`
  so that the **defaults are null objects** and the bodies contain **no `None` checks**: no
  `None`, no `if logger`, no `cache or ...`. Passing `None` explicitly is no longer supported.
- The behavior and the log messages with real collaborators stay exactly the same as the old code
  (same text, same order).

A default argument is created once. That is fine here because the null objects have no state;
a *stateful* default would be shared by every call.

**Example**

```python
order_total([("pen", 3), ("lamp", 1)])                 # 36, silently
order_total([("pen", 3)], logger=my_logger)            # my_logger gets "priced pen x3" and "total 6"
order_total([("pen", 3), ("pen", 1)], cache=DictCache())   # the second pen price comes from the cache
```
