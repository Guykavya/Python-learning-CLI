## Hint 1

`logging.getLogger("shop.cart")` returns the **same** object every time, with all the handlers
it already has. So what does `logger.addHandler(...)` do on the second call if you do nothing
else first? Where can you see the current handlers? (`logger.handlers` is a list.)

## Hint 2

Loop over a **copy** of the list while removing: `for h in list(logger.handlers):
logger.removeHandler(h)`. Removing from a list while looping over it skips items.

```
logger = getLogger(name)
logger.setLevel(level)
for h in copy of logger.handlers: logger.removeHandler(h)
handler = StreamHandler(stream); handler.setFormatter(Formatter(FORMAT))
logger.addHandler(handler)
logger.propagate = False
return logger
```
