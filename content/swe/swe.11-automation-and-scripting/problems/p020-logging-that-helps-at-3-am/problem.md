# Logging that helps at 3 a.m.

Chapter section 8.2 (logging that helps at 3 a.m.). A scheduled script must leave a trail. The screen (stderr) should be quiet by default and chattier with `-v` and `-vv`; the log **file** should always keep everything, with timestamps, because when something failed overnight you cannot re-run it with `-vv`.

The chapter's version sets one level for both handlers. Here the two handlers get **different** levels.

## What to write

```python
def setup_logging(verbose=0, logfile=None, stream=None) -> logging.Logger: ...
```

Configure and return the logger named **`"auto"`** (the tool's logger; `logging.getLogger("auto.tidy")` and other children send their records to it):

- the logger's own level is `DEBUG`, and `propagate = False` (it does not also send records to the root logger);
- a **console** handler, `logging.StreamHandler(stream or sys.stderr)`, whose level depends on `verbose`: `0` is `WARNING`, `1` is `INFO`, `2` or more is `DEBUG`. Format: `"%(levelname)s %(name)s: %(message)s"`;
- if `logfile` is given, a **file** handler, `logging.handlers.RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=3, encoding="utf-8")`, always at level `DEBUG`. Format: `"%(asctime)s %(levelname)s %(name)s: %(message)s"` (the time is what makes a 3 a.m. log useful);
- calling it **again** (a test, or a long-running process that reloads its settings) must not add handlers on top of the old ones: first remove the logger's existing handlers and `close()` them, so every message is written once.

## Example

```python
log = setup_logging(verbose=1, logfile="auto.log", stream=sys.stderr)
log.info("starting backup of %d folders", 3)      # screen: INFO auto: starting backup of 3 folders
log.debug("details")                              # screen: nothing (needs -vv); file: yes
logging.getLogger("auto.tidy").warning("empty")   # screen: WARNING auto.tidy: empty
# auto.log:
# 2026-11-21 03:00:01,123 INFO auto: starting backup of 3 folders
# 2026-11-21 03:00:01,124 DEBUG auto: details
# 2026-11-21 03:00:01,124 WARNING auto.tidy: empty
```
