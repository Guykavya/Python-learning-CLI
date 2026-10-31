## Hint 1

Who owns the **root** logger: the library or the application? What happens to *other* libraries'
debug messages when the root's level becomes DEBUG? And what does `basicConfig` do when it is called a
second time?

## Hint 2

Look up three things: what `logging.getLogger(__name__)` returns inside `pricing/core.py`; the
difference between `log.error(...)` and `log.exception(...)` inside an `except` block; and what
`logging.NullHandler` does (nothing!) and why that is useful when nobody configured logging.

## Hint 3

A plan for your answer:

```
1. five bullets: basicConfig, name, f-string, error vs exception, print
2. library: getLogger(__name__), emit only, NullHandler, never configure
3. app: configure once in main(); basicConfig(level=WARNING); getLogger("pricing").setLevel(DEBUG)
4. dotted names -> tree -> effective level + propagation to the root handler
then ~10 lines of corrected code
```
