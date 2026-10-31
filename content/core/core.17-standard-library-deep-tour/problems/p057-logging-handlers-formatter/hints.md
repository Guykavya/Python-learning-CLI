## Hint 1

There are three places that can drop a message: the logger's level, each handler's level, and
filters. Which one should stop DEBUG from reaching the console but not the file? And where must the
`RequestIdFilter` sit so that records from `shop.app.db` also get a `request_id`?

## Hint 2

Build each handler in four steps: create it, `setLevel`, `setFormatter(logging.Formatter(fmt,
datefmt=...))`, `addFilter` (file only). Then `logger.addHandler(...)`. For `close_logging`, loop over
a **copy** (`list(logger.handlers)`), because `removeHandler` changes the list.

## Hint 3

```
close_logging(logger):
    for h in list(logger.handlers): logger.removeHandler(h); h.close()

setup_logging(...):
    logger = getLogger(name); close_logging(logger)
    logger.setLevel(DEBUG); logger.propagate = False
    ch = StreamHandler(console); ch.setLevel(console_level); ch.setFormatter(Formatter(CONSOLE_FMT))
    fh = FileHandler(log_file, encoding="utf-8"); fh.setLevel(DEBUG)
    fh.setFormatter(Formatter(FILE_FMT, datefmt="%Y-%m-%d %H:%M:%S")); fh.addFilter(RequestIdFilter(request_id))
    add both; return logger
```
