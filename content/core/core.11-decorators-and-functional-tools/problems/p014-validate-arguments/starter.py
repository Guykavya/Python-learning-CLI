from functools import wraps


def typed(*types):
    def decorate(func):
        return func
    return decorate


def in_range(low, high):
    def decorate(func):
        return func
    return decorate
