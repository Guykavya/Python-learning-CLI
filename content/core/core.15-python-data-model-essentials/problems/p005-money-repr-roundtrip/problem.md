# A repr you can eval back

A good `repr` follows a rule: `eval(repr(x))` should build an equal object (when that is practical).
It makes logs and test failures easy to copy and re-run.

The class `Money(cents, currency)` is started for you (it also has `__eq__`). Add:

- `__repr__`: `Money(1250, 'USD')`. It must be valid Python that rebuilds an equal object.
- `__str__`: friendly text with two decimals and the currency: `12.50 USD`.
  Negative amounts put the minus first: `Money(-5, 'EUR')` gives `-0.05 EUR`.

Amounts are whole cents, so no float rounding happens.

**Example**

```python
m = Money(1250, "USD")
print(repr(m))            # Money(1250, 'USD')
print(m)                  # 12.50 USD
print(eval(repr(m)) == m) # True
print(Money(-5, "EUR"))   # -0.05 EUR
```
