# Logging levels: say the right thing at the right level

`print` is for the program's **output**. `logging` is for messages **about** the program: what it is
doing, what looks odd, what failed. Each message has a **level**:

| Level | Number | Use it for |
|---|---|---|
| `DEBUG` | 10 | details only a developer hunting a bug wants |
| `INFO` | 20 | normal milestones ("processed 120 orders") |
| `WARNING` | 30 | something unusual, but the program carries on |
| `ERROR` | 40 | something failed (this item could not be handled) |
| `CRITICAL` | 50 | the program cannot continue |

A logger set to level `WARNING` drops `DEBUG` and `INFO` messages before any work is done.
That is how one program can be quiet by default and chatty with `-v` or `-vv`.

Pass values as **arguments**, not with an f-string:

```python
logger.debug("checking order %s", order_id)     # good: formatted only if DEBUG is enabled
logger.debug(f"checking order {order_id}")      # works, but always builds the string
```

The first form is "lazy": when the message is dropped, the string is never built. It also keeps the
template (`record.msg`) and the values (`record.args`) separate, so tools can group "the same message"
with different values.

Write three functions in `solution.py`:

1. `level_for(verbosity) -> int`: `0` gives `logging.WARNING`, `1` gives `INFO`, `2` or more gives
   `DEBUG`, a negative number (a `--quiet` flag) gives `ERROR`.
2. `make_logger(name, verbosity) -> logging.Logger`: `logging.getLogger(name)` with its level set from
   `level_for(verbosity)`. Do **not** add handlers (the application decides where logs go).
3. `process_orders(orders, logger) -> int`: `orders` is a list of `(order_id, quantity)`. For each order:
   - `DEBUG` `"checking order %s"` with the id;
   - if the quantity is 0 or less: `ERROR` `"invalid quantity %d in order %s"` (quantity, id), and the
     order is invalid;
   - else if the quantity is more than 100: `WARNING` `"large order %s: %d items"` (id, quantity); the
     order is still valid.

   At the end: `INFO` `"processed %d orders, %d invalid"` (number of orders, number invalid). Return
   the number of **valid** orders. Use the lazy `%` style with arguments for every message.

**Example**

```python
log = make_logger("shop.orders", 2)          # DEBUG
process_orders([("A1", 5), ("A2", 0), ("A3", 250)], log)     # returns 2
```

Logged records (level and message):

```text
DEBUG    checking order A1
DEBUG    checking order A2
ERROR    invalid quantity 0 in order A2
DEBUG    checking order A3
WARNING  large order A3: 250 items
INFO     processed 3 orders, 1 invalid
```

With `make_logger("shop.orders", 0)` only the `ERROR` and `WARNING` lines are kept.
