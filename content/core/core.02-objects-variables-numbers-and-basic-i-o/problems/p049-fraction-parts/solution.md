## Approach

Apply the same rules you know for ints to an exact Fraction. Nothing is approximated, so the
identity `(f // 1) + (f % 1) == f` holds exactly.

## Code

```python
from fractions import Fraction

f = Fraction(input())
whole = f // 1
rest = f % 1
print("floor:", whole)
print("remainder:", rest)
print("truncated:", int(f))
print("rounded:", round(f))
print("check:", whole + rest == f)
```

## What the outputs teach

- `-22/7 // 1` is `-4` and `-22/7 % 1` is `6/7`: `-4 + 6/7 = -22/7`. The remainder takes the sign of the divisor (1).
- `int(-22/7)` is `-3`, cutting toward zero.
- `round(Fraction(5, 2))` is `2` and `round(Fraction(7, 2))` is `4`: exact ties go to the even integer,
  and with a Fraction there is no binary error to blur the tie.

## Another way

`math.floor(f)` gives the same as `f // 1`, and `math.trunc(f)` the same as `int(f)`.
