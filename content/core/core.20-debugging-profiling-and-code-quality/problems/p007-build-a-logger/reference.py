import logging

FORMAT = "%(levelname)s %(name)s: %(message)s"


def make_logger(name: str, level: int, stream) -> logging.Logger:
    """A logger with exactly one stream handler, safe to call many times."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    for old in list(logger.handlers):
        logger.removeHandler(old)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
