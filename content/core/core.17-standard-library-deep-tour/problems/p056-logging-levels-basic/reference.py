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
