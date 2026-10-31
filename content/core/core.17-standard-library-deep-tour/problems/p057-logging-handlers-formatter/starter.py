import logging


class RequestIdFilter(logging.Filter):
    def __init__(self, request_id="-"):
        super().__init__()
        self.request_id = request_id


def setup_logging(name, log_file, console, request_id="-", console_level=logging.WARNING):
    return logging.getLogger(name)


def close_logging(logger):
    pass
