# Money that refuses to mix currencies

Adding `5 USD` and `5 EUR` is a bug, not a number. Make the operators say so with a clear error.

`Money(cents, currency)` and `CurrencyMismatchError` (a `ValueError`) are started for you. Add:

- `a + b` and `a - b` for two `Money` with the same currency: a new `Money`.
- If the currencies differ, raise `CurrencyMismatchError` with a message that contains both currency codes.
- `m * n` and `n * m` for a whole number `n` (`int`): a new `Money` with `cents * n`.
  Floats are **not** allowed (cents must stay whole): `TypeError`.
- `-m`: a new `Money` with negated cents.
- Adding a `Money` to something that is not a `Money` (`m + 5`) is a `TypeError`, **not** a mismatch error.
- `==` between different currencies is simply `False` (already written; do not raise there).

**Example**

```python
a = Money(500, "USD")
print(a + Money(250, "USD"))     # Money(750, 'USD')
print(3 * a)                      # Money(1500, 'USD')
print(-a)                         # Money(-500, 'USD')
a + Money(100, "EUR")             # CurrencyMismatchError: cannot mix USD and EUR
```
