import logging

CONSOLE_FORMAT = "%(levelname)s: %(message)s"
FILE_FORMAT = "%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class RequestIdFilter(logging.Filter):
    def __init__(self, request_id="-"):
        super().__init__()
        self.request_id = request_id

    def filter(self, record):
        record.request_id = self.request_id
        return True


def close_logging(logger):
    for handler in list(logger.handlers):      # copy: we change the list while looping
        logger.removeHandler(handler)
        handler.close()


def setup_logging(name, log_file, console, request_id="-", console_level=logging.WARNING):
    logger = logging.getLogger(name)
    close_logging(logger)                      # calling setup twice must not double the output
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    console_handler = logging.StreamHandler(console)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(FILE_FORMAT, datefmt=DATE_FORMAT))
    file_handler.addFilter(RequestIdFilter(request_id))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
