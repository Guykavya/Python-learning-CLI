from functools import partial


def power(base, exp):
    return base ** exp


square = partial(power, exp=2)
cube = partial(power, exp=3)
from_binary = partial(int, base=2)
from_hex = partial(int, base=16)
