# Trace: which log messages appear?

When you call `some_logger.info("...")`, logging decides in this order:

1. **The logger's effective level.** The logger's own level, or if it has none (`NOTSET`), the
   level of the nearest ancestor that has one (`app.db` asks `app`, then the root). Below it,
   the message is dropped right here. A logger with `disabled = True` drops everything.
2. **Every handler on this logger** emits the record if the record's level is at least the
   **handler's** level.
3. If `propagate` is true (the default), the record is passed to the **parent's handlers**,
   then the grandparent's, up to the root. **Only the handlers' levels are checked on the
   way up. The parent loggers' own levels are not checked again.**

What does this program print? (Every handler writes to `sys.stdout`, so everything appears in
order.)

```python
import logging
import sys

fmt = logging.Formatter("%(name)s %(levelname)s %(message)s")


def handler(level):
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(level)
    h.setFormatter(fmt)
    return h


root = logging.getLogger()
root.setLevel(logging.ERROR)
root.addHandler(handler(logging.WARNING))

app = logging.getLogger("app")
app.setLevel(logging.INFO)
app.addHandler(handler(logging.DEBUG))

db = logging.getLogger("app.db")        # no level of its own

web = logging.getLogger("app.web")
web.setLevel(logging.DEBUG)
web.propagate = False
web.addHandler(handler(logging.ERROR))

other = logging.getLogger("other")      # no level, no handler

app.debug("1")
app.info("2")
app.warning("3")
db.info("4")
db.debug("5")
db.error("6")
web.debug("7")
web.error("8")
other.warning("9")
other.error("10")
db.disabled = True
db.critical("11")
print("done")
```

**Example**: `app.debug("1")` prints nothing: `app`'s level is `INFO`, so the record is dropped
in step 1 before any handler sees it.

Write in `answer.txt` the lines the program prints, in order.
