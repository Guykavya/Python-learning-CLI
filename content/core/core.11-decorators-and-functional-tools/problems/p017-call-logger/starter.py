from functools import wraps


def logged(log):
    def decorate(func):
        return func
    return decorate
