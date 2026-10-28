# Two handlers, two formats, one filter

A logger decides **whether** a message is worth recording. **Handlers** decide **where** it goes,
and each handler has its own level and its own **formatter** (how the line looks). A typical
program shows short warnings on the console but writes every detail, with times, to a file:

```text
console:   WARNING: disk almost full
file:      2025-03-01 10:15:02 WARNING  [req-42] shop.app: disk almost full
```

A **filter** can drop records, or add information to them. A filter that sets
`record.request_id` lets the format string use `%(request_id)s`.

One subtle rule: filters attached to a **logger** only see records logged on that exact logger.
Records from child loggers (`shop.app.db`) that propagate up skip the parent's logger filters but do
go through the parent's **handler** filters. So a filter that adds fields belongs on the handler.

## Your task

In `solution.py` write:

1. `class RequestIdFilter(logging.Filter)`: `RequestIdFilter(request_id="-")`; its `filter(record)` sets
   `record.request_id` and returns `True` (keep every record).
2. `setup_logging(name, log_file, console, request_id="-", console_level=logging.WARNING) -> logging.Logger`:
   - get the logger `name`, set its level to `DEBUG`, and set `propagate = False` (these messages are
     handled here and must not also reach the root logger's handlers);
   - **first remove and close any handlers it already has**, so calling `setup_logging` twice does not
     print every message twice;
   - console handler: `logging.StreamHandler(console)` (`console` is a stream such as `sys.stderr`),
     level `console_level`, format `"%(levelname)s: %(message)s"`;
   - file handler: `logging.FileHandler(log_file, encoding="utf-8")`, level `DEBUG`, format
     `"%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s"` with
     `datefmt="%Y-%m-%d %H:%M:%S"`, and a `RequestIdFilter(request_id)` added **to this handler**.
3. `close_logging(logger)`: remove every handler from the logger and close it (on Windows an open log
   file cannot be deleted or moved).

**Example**

```python
import io
console = io.StringIO()
log = setup_logging("shop.app", "app.log", console, request_id="req-42")
log.debug("cart has %d items", 3)
log.warning("disk almost full")
logging.getLogger("shop.app.db").error("connection lost")
close_logging(log)

console.getvalue()
# 'WARNING: disk almost full\nERROR: connection lost\n'
```

`app.log` (the times are those of your run):

```text
2025-03-01 10:15:02 DEBUG    [req-42] shop.app: cart has 3 items
2025-03-01 10:15:02 WARNING  [req-42] shop.app: disk almost full
2025-03-01 10:15:02 ERROR    [req-42] shop.app.db: connection lost
```

`%(levelname)-8s` pads the level name to 8 characters, so the columns line up.
