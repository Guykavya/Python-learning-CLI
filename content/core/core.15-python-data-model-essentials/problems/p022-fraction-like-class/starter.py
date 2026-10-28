import math
from functools import total_ordering


@total_ordering
class Frac:
    def __init__(self, num, den=1):
        # TODO: reduce with math.gcd, make den positive, ZeroDivisionError if den == 0
        self.num = num
        self.den = den

    # TODO: + - * / (and reflected versions), ==, hash, <, repr, str, float
