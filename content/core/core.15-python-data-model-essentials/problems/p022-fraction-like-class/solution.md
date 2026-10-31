## Approach

Normalise once in `__init__` (lowest terms, positive denominator) and every other method can assume that. A `_coerce` helper keeps the int-handling in one place. Subtraction and division are not commutative, so their reflected versions must swap the operands.

## Code

```python
import math
from functools import total_ordering


def _coerce(x):
    if isinstance(x, Frac):
        return x
    if isinstance(x, int) and not isinstance(x, bool):
        return Frac(x, 1)
    return None


@total_ordering
class Frac:
    def __init__(self, num, den=1):
        if den == 0:
            raise ZeroDivisionError("denominator is zero")
        if den < 0:
            num, den = -num, -den
        g = math.gcd(num, den)
        self.num = num // g
        self.den = den // g

    def __add__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        return Frac(self.num * o.den + o.num * self.den, self.den * o.den)

    __radd__ = __add__

    def __sub__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        return Frac(self.num * o.den - o.num * self.den, self.den * o.den)

    def __rsub__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        return o - self

    def __mul__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        return Frac(self.num * o.num, self.den * o.den)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        if o.num == 0:
            raise ZeroDivisionError("division by zero fraction")
        return Frac(self.num * o.den, self.den * o.num)

    def __rtruediv__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        return o / self

    def __eq__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        return (self.num, self.den) == (o.num, o.den)

    def __lt__(self, other):
        o = _coerce(other)
        if o is None:
            return NotImplemented
        return self.num * o.den < o.num * self.den

    def __hash__(self):
        if self.den == 1:
            return hash(self.num)
        return hash((self.num, self.den))

    def __float__(self):
        return self.num / self.den

    def __repr__(self):
        return f"Frac({self.num}, {self.den})"

    def __str__(self):
        if self.den == 1:
            return str(self.num)
        return f"{self.num}/{self.den}"
```

## Complexity

O(log n) per operation because of `gcd`.

## Another way

The standard library has `fractions.Fraction`, which does all of this (and more). Writing your own once shows what the operator methods are for.
