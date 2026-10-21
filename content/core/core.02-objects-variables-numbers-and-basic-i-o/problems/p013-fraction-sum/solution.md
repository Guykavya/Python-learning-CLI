## Approach

A `Fraction` stores a numerator and a denominator as Python ints, so nothing is ever rounded.
It reduces itself to lowest terms after every operation.

## Code

```python
from fractions import Fraction

x = Fraction(input())
y = Fraction(input())
total = x + y
print(total)
print(x * y)
print(float(total))
```

## Why it is exact

`1/3 + 1/6` is computed as `2/6 + 1/6 = 3/6`, then reduced by the greatest common divisor to `1/2`.
Only the last line, the `float`, may be an approximation.

## Another way

You can build a Fraction from two ints: `Fraction(1, 3)`. Building from a float, as in
`Fraction(0.1)`, copies the float's binary error: `3602879701896397/36028797018963968`.
