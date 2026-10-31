## Hint 1

Levels are just numbers (`logging.DEBUG` is 10, `logging.WARNING` is 30). Which logger method sends a
message at each level? And how does a logger decide to drop a message?

## Hint 2

`level_for` is an `if`/`elif` chain on `verbosity`. `make_logger` is two lines: `getLogger`, then
`setLevel`. In `process_orders`, count invalid orders while looping, and call
`logger.debug(...)`, `logger.error(...)`, `logger.warning(...)`, `logger.info(...)` with a template
and its values as separate arguments.

## Hint 3

```
process_orders(orders, logger):
    invalid = 0
    for order_id, qty in orders:
        logger.debug("checking order %s", order_id)
        if qty <= 0:   logger.error("invalid quantity %d in order %s", qty, order_id); invalid += 1
        elif qty > 100: logger.warning("large order %s: %d items", order_id, qty)
    logger.info("processed %d orders, %d invalid", len(orders), invalid)
    return len(orders) - invalid
```
