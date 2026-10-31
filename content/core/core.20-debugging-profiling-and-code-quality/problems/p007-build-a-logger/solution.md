## Approach

A logger is a long-lived, **global** object: `getLogger(name)` creates it once and then keeps
handing back the same one. Setup code must therefore be written so that running it twice gives
the same result as running it once (it must be *idempotent*). The simplest way is "clear, then
add": remove whatever handlers are there, then add the one we want.

`propagate = False` stops the record from also travelling up to the parent loggers (`shop`,
then the root). If someone called `logging.basicConfig()` (which puts a handler on the root),
a propagating logger would print each line twice: once from its own handler and once from the
root's.

## Code

```python
import logging

FORMAT = "%(levelname)s %(name)s: %(message)s"


def make_logger(name: str, level: int, stream) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    for old in list(logger.handlers):
        logger.removeHandler(old)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
```

`list(logger.handlers)` makes a copy, because `removeHandler` changes the list we would
otherwise be looping over.

## Complexity

O(h) for h old handlers; in practice constant.

## Another way

Only add a handler if there is none yet:

```python
if not logger.handlers:
    logger.addHandler(handler)
```

That avoids duplicates but keeps the **first** stream forever, so a second call cannot switch
the output (this problem's last-but-one test). For a whole application, configure everything
once at start-up with `logging.config.dictConfig({...})`, which replaces handlers for you, and
let modules only call `logging.getLogger(__name__)`.
