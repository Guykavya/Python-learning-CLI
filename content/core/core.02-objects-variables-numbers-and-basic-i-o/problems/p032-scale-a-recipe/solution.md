## Approach

Keep the value exact with `Fraction` for as long as possible. Convert to `float` only at the last
moment, for display.

## Code

```python
from fractions import Fraction

amount = Fraction(input())
have = int(input())
want = int(input())
scaled = amount * want / have
print(f"Cups: {scaled}")
print(f"About: {float(scaled):.3f}")
```

## Why the type stays Fraction

When a Fraction meets an int in `*` or `/`, Python converts the int to a Fraction and the result
is a Fraction. When a Fraction meets a float, the result is a float, and exactness is lost.
That is the numeric widening rule: int, then Fraction, then float.

## Another way

`Fraction(amount) * Fraction(want, have)` builds the scale factor as one fraction first.
