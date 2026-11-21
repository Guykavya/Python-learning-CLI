import logging
import logging.handlers
import sys


def setup_logging(verbose=0, logfile=None, stream=None):
    """Configure and return the 'auto' logger: console level by verbose, file always DEBUG, no duplicate handlers."""
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
