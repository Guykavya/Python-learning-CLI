**1. What is wrong**

- **`basicConfig` in a library.** It configures the **root** logger, which belongs to the application.
  Run at import time, it sets the root level to DEBUG (so *every* library's debug messages appear) and
  installs its own handler and format. If the application configures logging later, `basicConfig`
  in the app does nothing because the root already has a handler, so the user's format "changes".
- **`"my_logger"`.** A made-up name is not part of the package tree, may clash with another library's
  logger, and tells the reader nothing. `getLogger(__name__)` gives `pricing.core`.
- **f-string.** The text is built even when DEBUG is off, and the record loses its template/arguments.
  Write `log.debug("computing total of %d items", len(items))`.
- **`log.error("bad item")` in `except`.** No details and no traceback. `log.exception("bad item in
  %r", items)` logs at ERROR level **with** the traceback (which key, which line). Even better, a
  library that re-raises often should not log at all: the caller decides whether this is an error.
- **`print`.** It cannot be filtered, redirected or turned off, and it pollutes the program's real output.

**2. Library rule.** Only *create* loggers and *emit* messages: `log = logging.getLogger(__name__)`
in each module, honest levels, lazy `%` arguments. Never call `basicConfig`, never set levels on the
root, never add real handlers. Optionally add `logging.getLogger("pricing").addHandler(logging.NullHandler())`
in `pricing/__init__.py`: a handler that does nothing, so that if the application configured nothing,
`lastResort` does not print the library's warnings to stderr.

**3. Application rule.** Configure logging **once**, at the entry point (`main()` or
`if __name__ == "__main__":`), before real work starts, with `basicConfig` or `dictConfig`:

```python
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("pricing").setLevel(logging.DEBUG)
```

The root handler has no level of its own, so it prints whatever reaches it; the root's level WARNING
gates every logger without its own level, while `pricing.*` loggers now have DEBUG as effective level.

**4. Why `__name__` makes this work.** Module names are dotted (`pricing.core`, `pricing.db`), so
loggers named after them form a tree under `pricing`. A level set on `pricing` becomes the effective
level of every child that has none, and their records **propagate** up to the root's handler. One line
controls a whole package without the library knowing anything about the application.

**Corrected library code**

```python
# pricing/core.py
import logging

log = logging.getLogger(__name__)


def total(items):
    log.debug("computing total of %d items", len(items))
    try:
        return sum(i["price"] * i["qty"] for i in items)
    except KeyError:
        log.exception("item without price or qty in %r", items)
        raise
```
