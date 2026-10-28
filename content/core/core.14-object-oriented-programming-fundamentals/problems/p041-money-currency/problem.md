# Money that never mixes currencies

Money is a classic place for bugs: `0.1 + 0.2` is not `0.3` in floating point, and adding rupees
to dollars gives nonsense. Write a small `Money` class in `solution.py` that stores whole **minor
units** (paise, cents) as an `int`, never changes after it is created, and refuses to mix
currencies.

**`CurrencyMismatchError(ValueError)`**: `CurrencyMismatchError(left, right)` stores `left` and
`right` (the two currency codes); message `f"cannot combine {left} and {right}"`. It inherits from
`ValueError`, so old code that catches `ValueError` still catches it.

**`Money(minor, currency)`**

- `minor` must be an `int` (it may be negative), otherwise `TypeError`.
- `currency` must be a `str` of exactly 3 capital letters A–Z, like `"INR"`, otherwise `ValueError`.
- `minor` and `currency` are **read-only properties**. Setting them raises `AttributeError`.
- `Money.from_string(text)` (classmethod) reads `"12.50 INR"`: a number, one space, a currency
  code. The number may start with `-` and may have **at most 2** digits after the point:
  `"12 INR"` → 1200, `"12.5 INR"` → 1250, `"-3.05 USD"` → -305. **Do not use `float`**
  (`float("0.29") * 100` is `28.999999999999996`). Anything else raises `ValueError`.
  Build the object with `cls(...)`.
- `add(other)` and `subtract(other)` return a **new** `Money`. `other` must be a `Money`, otherwise
  `TypeError`; a different currency raises `CurrencyMismatchError(self.currency, other.currency)`.
- `times(factor)` returns a new `Money`; `factor` must be an `int`, otherwise `TypeError`.
- `split(n)` divides the money into `n` parts (an `int` of at least 1, otherwise `ValueError`)
  that add up **exactly** to the original. The parts differ by at most 1 minor unit, and the larger
  parts come first: 10.00 split 3 ways is `[3.34, 3.33, 3.33]`.
- `format()` returns `"12.50 INR"` (always 2 digits after the point, `-` for negative amounts).
- `__repr__` returns `Money(1250, 'INR')`.

**Example**

```python
a = Money.from_string("12.50 INR")
a.minor, a.currency          # (1250, 'INR')
b = a.add(Money(75, "INR"))
b.format()                   # '13.25 INR'
a.format()                   # '12.50 INR'   (a did not change)
Money.from_string("0.29 INR").minor    # 29
[m.format() for m in Money(1000, "INR").split(3)]   # ['3.34 INR', '3.33 INR', '3.33 INR']
Money(-305, "USD").format()  # '-3.05 USD'
a.add(Money(100, "USD"))     # CurrencyMismatchError: cannot combine INR and USD
a.minor = 5                  # AttributeError
```
