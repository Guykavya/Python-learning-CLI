## Approach

```python
def setup_logging(verbose=0, logfile=None, stream=None):
    log = logging.getLogger("auto")
    log.setLevel(logging.DEBUG)                 # the logger lets everything through...
    log.propagate = False
    for handler in list(log.handlers):          # ...called twice: replace, do not stack
        log.removeHandler(handler)
        handler.close()
    console = logging.StreamHandler(stream or sys.stderr)
    console.setLevel([logging.WARNING, logging.INFO, logging.DEBUG][min(verbose, 2)])
    console.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    log.addHandler(console)
    if logfile:
        fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(logging.DEBUG)              # ...and each handler decides what it keeps
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        log.addHandler(fh)
    return log
```

The design rule: **the logger filters nothing, the handlers filter everything**. The screen is for the person watching now (quiet unless asked); the file is for the person investigating later (complete, with times). `RotatingFileHandler` keeps the file from filling the disk. Removing and closing the old handlers makes the function safe to call twice, and closing matters on Windows, where an open log file cannot be deleted or rotated.

## Complexity

O(1) per call; each log record costs one write per handler that accepts it.

## Another way

`logging.config.dictConfig` describes the same setup as a dictionary (handlers, formatters, levels), which can live in the TOML config of p018. For a small tool the function above is easier to read; for a suite with many loggers, `dictConfig` keeps it in one place.
