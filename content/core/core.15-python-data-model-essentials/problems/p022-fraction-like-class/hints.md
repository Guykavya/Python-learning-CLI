## Hint 1

Start with `__init__`: reduce with `math.gcd` and fix the sign so the denominator is positive. Then write a small helper that turns the other operand into a `Frac` (int becomes `Frac(n, 1)`, anything else gives `NotImplemented`).

## Hint 2

Use the helper in every operator, then write the reflected versions by hand for `-` and `/` (order matters!), and reuse the plain ones for `+` and `*`. For comparison, cross-multiply: `a.num * b.den < b.num * a.den` (denominators are positive).

## Hint 3

```
_coerce(other): Frac -> itself; int (not bool) -> Frac(other, 1); else None
__add__ : o = coerce ; None -> NotImplemented ; Frac(a.n*b.d + b.n*a.d, a.d*b.d)
__radd__ = __add__ ; __rmul__ = __mul__
__sub__ , __rsub__ (o - self) ; __truediv__ , __rtruediv__ (o / self)
__eq__ via (num, den) ; __hash__: hash(num) if den == 1 else hash((num, den))
__lt__ by cross multiplication (total_ordering)
```
