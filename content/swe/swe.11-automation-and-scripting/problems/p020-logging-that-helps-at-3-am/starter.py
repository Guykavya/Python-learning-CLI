import logging
import logging.handlers
import sys


def setup_logging(verbose=0, logfile=None, stream=None):
    """Configure and return the 'auto' logger: console level by verbose, file always DEBUG, no duplicate handlers."""
    log = logging.getLogger("auto")
    # TODO
    return log
