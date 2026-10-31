- `int(float(number) * 100)` in `from_string`. `0.29` becomes 28 paise; `1.15` becomes 114.
- `round(float(number) * 100)`. It hides the problem for small numbers but still goes through an
  inexact float; work with the digits.
- `add` that changes `self._minor` and returns `self`. Then `a.add(b)` silently changes `a`
  everywhere it is used.
- `class CurrencyMismatchError(Exception)`. It works, but old code with `except ValueError` no
  longer catches it.
- `split` with `self.minor // n` for every part. The leftover paise disappear: 1000 / 3 gives
  333 + 333 + 333 = 999.
- `format` with `divmod(self.minor, 100)` for negative amounts: `-305` becomes `-4.95`.
- Accepting `"12.505 INR"` by cutting the third digit. Rejecting it is safer than silently losing money.
