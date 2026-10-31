import functools


class Retry:
    def __init__(self, times=3, exceptions=(Exception,)):
        self.times = times
        self.exceptions = exceptions
        self.failures = 0

    # TODO: __call__(self, func) must return a wrapper function
