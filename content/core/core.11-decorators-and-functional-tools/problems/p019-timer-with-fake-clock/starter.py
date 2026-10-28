import time
from functools import wraps


def timed(clock=time.perf_counter):
    def decorate(func):
        func.durations = []
        return func
    return decorate


def report(func):
    return ""
