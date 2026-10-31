## Approach

The function that does the work (`process_orders`) only **emits** messages at honest levels; it does
not decide what is shown. The caller decides, by setting the logger's level (`make_logger`). This
split is the heart of logging: the same code can be silent in production and detailed while
debugging, without editing it.

Each message uses a template plus arguments. The logger first checks the level; only if the record
survives is `msg % args` computed (when a handler formats it).

## Code

```python
import logging


def level_for(verbosity):
    if verbosity < 0:
        return logging.ERROR
    if verbosity == 0:
        return logging.WARNING
    if verbosity == 1:
        return logging.INFO
    return logging.DEBUG


def make_logger(name, verbosity):
    logger = logging.getLogger(name)
    logger.setLevel(level_for(verbosity))
    return logger


def process_orders(orders, logger):
    invalid = 0
    for order_id, quantity in orders:
        logger.debug("checking order %s", order_id)
        if quantity <= 0:
            logger.error("invalid quantity %d in order %s", quantity, order_id)
            invalid += 1
        elif quantity > 100:
            logger.warning("large order %s: %d items", order_id, quantity)
    logger.info("processed %d orders, %d invalid", len(orders), invalid)
    return len(orders) - invalid
```

## Complexity

O(n) for n orders. A dropped message costs only a level comparison.

## Another way

`level_for` can be a table lookup: `levels = [logging.WARNING, logging.INFO, logging.DEBUG]`, then
`logging.ERROR if v < 0 else levels[min(v, 2)]`. In a real program verbosity usually comes from
`argparse` with `parser.add_argument("-v", action="count", default=0)`.
