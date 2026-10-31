# Build a logger

Every module in a real program asks for **its own** logger by name and attaches what it needs.
The most common logging bug is the **duplicated line**: a setup function that adds a new handler
each time it is called, so after three calls every message is printed three times.

Write `make_logger(name: str, level: int, stream) -> logging.Logger` in `solution.py`:

- Get the logger with `logging.getLogger(name)` (so the same name gives the same object) and
  set its level to `level`.
- Give it **exactly one** handler: a `logging.StreamHandler(stream)` with the formatter
  `"%(levelname)s %(name)s: %(message)s"`.
- Calling `make_logger` again with the same name must **not** add a second handler. Remove the
  old handlers first, so the logger ends up with one handler writing to the **new** stream and
  the **new** level.
- Set `propagate` to `False`, so messages are not also passed on to the root logger's handlers
  (that is the other source of duplicated lines).
- Return the logger.

**Example**

```python
import io, logging

buf = io.StringIO()
log = make_logger("shop.cart", logging.INFO, buf)
log.debug("hidden")
log.info("added %s x%d", "pen", 3)
log = make_logger("shop.cart", logging.INFO, buf)   # called again
log.warning("stock low")
print(buf.getvalue(), end="")
```

```text
INFO shop.cart: added pen x3
WARNING shop.cart: stock low
```

`stock low` appears **once**, although `make_logger` ran twice.
