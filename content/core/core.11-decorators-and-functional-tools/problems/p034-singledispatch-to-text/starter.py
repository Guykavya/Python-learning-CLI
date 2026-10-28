from functools import singledispatch


@singledispatch
def to_text(value):
    return str(value)
