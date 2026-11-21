import contextvars
import json
import logging
import sys
import time

request_id_var = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # TODO: ts, level, logger, msg, request_id, the extra fields, the exception
        return record.getMessage()


def configure_logging(level="INFO", stream=None):
    # TODO: root logger gets ONE StreamHandler with JsonFormatter
    pass
