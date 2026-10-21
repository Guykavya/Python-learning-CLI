## Approach

Separate the three concerns. The digits come from `format(abs(amount), spec)`, where the spec is
built from the options: `",.2f"` or `".2f"` and so on. The sign is decided from the original
amount. Then join sign, currency, a space and the digits.

## Code

```python
def format_price(amount, currency="Rs", decimals=2, thousands=True):
    """Return amount as text such as 'Rs 1,234.50' or '-Rs 12.00'."""
    spec = ",." if thousands else "."
    digits = format(abs(amount), spec + str(decimals) + "f")
    sign = "-" if amount < 0 else ""
    return sign + currency + " " + digits
```

## Complexity

O(number of digits).

## Another way

A nested f-string: `f"{abs(amount):,.{decimals}f}"` when `thousands` is true, and
`f"{abs(amount):.{decimals}f}"` otherwise. Same result; building the spec string once avoids
writing the format twice.
