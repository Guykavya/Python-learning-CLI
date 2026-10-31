## Approach

A record travels: **logger level** (DEBUG here, so everything passes), then for each handler on this
logger and its ancestors (until `propagate` is `False`), **handler level**, **handler filters**,
**formatter**, output. Putting the WARNING limit on the console *handler* keeps the file complete.
Putting the `RequestIdFilter` on the file *handler* means every record that reaches the file, including
ones propagated from child loggers, gets its `request_id` before the formatter needs it.

`setup_logging` starts by removing old handlers, because `getLogger(name)` always returns the same
object: without the clean-up, every call adds two more handlers and messages repeat.
`propagate = False` stops records here; otherwise the root logger's handlers (for example one added by
`basicConfig`, or pytest's) would print them a second time.

## Code

```python
import logging

CONSOLE_FORMAT = "%(levelname)s: %(message)s"
FILE_FORMAT = "%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class RequestIdFilter(logging.Filter):
    def __init__(self, request_id="-"):
        super().__init__()
        self.request_id = request_id

    def filter(self, record):
        record.request_id = self.request_id
        return True


def close_logging(logger):
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def setup_logging(name, log_file, console, request_id="-", console_level=logging.WARNING):
    logger = logging.getLogger(name)
    close_logging(logger)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    console_handler = logging.StreamHandler(console)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(FILE_FORMAT, datefmt=DATE_FORMAT))
    file_handler.addFilter(RequestIdFilter(request_id))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
```

## Complexity

O(1) per message per handler (plus the cost of writing it).

## Another way

`logging.config.dictConfig({...})` describes the same set-up as data (a dict, often loaded from a
JSON or TOML file): formatters, filters, handlers and loggers by name. Applications with several
loggers usually prefer it. Instead of a filter, `logging.LoggerAdapter(logger, {"request_id": "req-42"})`
adds the extra field to every message logged through the adapter; and a call can pass
`extra={"request_id": ...}` for a single message.
