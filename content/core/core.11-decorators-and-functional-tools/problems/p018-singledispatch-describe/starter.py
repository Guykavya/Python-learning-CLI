from functools import singledispatch


def describe(x):
    return f"unknown: {x!r}"
