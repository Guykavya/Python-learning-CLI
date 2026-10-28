import logging


def level_for(verbosity):
    return logging.NOTSET


def make_logger(name, verbosity):
    return logging.getLogger(name)


def process_orders(orders, logger):
    return 0
