import logging

FORMAT = "%(levelname)s %(name)s: %(message)s"


def make_logger(name: str, level: int, stream) -> logging.Logger:
    """A logger with exactly one stream handler, safe to call many times."""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    return logger
