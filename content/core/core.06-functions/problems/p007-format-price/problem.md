# Format a price

Write `format_price(amount, currency="Rs", decimals=2, thousands=True)` that returns a price
as text:

- the currency, a space, then the amount rounded to `decimals` places;
- if `thousands` is true, digits are grouped in threes with commas (`1,234,567.50`);
- a negative amount puts the minus sign **before** the currency: `-Rs 12.00`.

**Examples**

```python
format_price(1234.5)                          # "Rs 1,234.50"
format_price(1234.5, "USD")                   # "USD 1,234.50"
format_price(1234.5, decimals=0)              # "Rs 1,234"
format_price(1234567.891, thousands=False)    # "Rs 1234567.89"
format_price(-12)                             # "-Rs 12.00"
format_price(0.5, currency="EUR", decimals=1) # "EUR 0.5"
```

Hint from core.03: the format spec `,.2f` groups thousands and shows 2 decimals, and the
precision can itself come from a variable: `f"{x:,.{decimals}f}"`.
