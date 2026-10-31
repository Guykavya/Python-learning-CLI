# A Fraction class

Build your own small fraction type, `Frac(num, den)`, using nearly everything about operators.

Write `Frac` in `solution.py`:

- `Frac(num, den=1)` stores the fraction in lowest terms with a **positive** denominator:
  `Frac(2, 4)` gives `1/2`; `Frac(1, -2)` gives `-1/2`. `den == 0` raises `ZeroDivisionError`.
  Attributes: `num`, `den`.
- `+`, `-`, `*`, `/` between two `Frac`s, **and** between a `Frac` and an `int` on either side:
  `Frac(1, 2) + 1`, `1 + Frac(1, 2)`, `2 * Frac(1, 3)`, `1 - Frac(1, 4)`, `1 / Frac(2, 3)`.
  Dividing by a zero fraction raises `ZeroDivisionError`.
- `==` (also equal to an `int` when it has the same value: `Frac(4, 2) == 2`), `hash` consistent with it
  (`hash(Frac(4, 2)) == hash(2)`).
- Ordering `<`, `<=`, `>`, `>=` against `Frac` and `int` (for instance with `total_ordering`).
- `repr(f)` is `Frac(1, 2)`; `str(f)` is `1/2`, or just `3` when the denominator is 1.
- `float(f)` gives the decimal value.
- Anything else (like strings or floats) as the other operand: `TypeError`.

Use `math.gcd` to reduce.

**Example**

```python
a, b = Frac(1, 2), Frac(1, 3)
print(a + b)        # 5/6
print(a * 4)        # 2
print(1 - a)        # 1/2
print(Frac(2, 4) == Frac(1, 2))   # True
print(sorted([a, b, Frac(1, 4)])) # [Frac(1, 4), Frac(1, 3), Frac(1, 2)]
```
