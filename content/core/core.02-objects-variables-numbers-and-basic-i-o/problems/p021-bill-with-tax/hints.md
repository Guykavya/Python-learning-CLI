## Hint 1

Can a `float` store `0.575` exactly? What does `f"{0.575:.2f}"` print?

## Hint 2

Create Decimals from the input **text**: `Decimal(input())`. Then use
`value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` to round to cents.

## Hint 3

```
subtotal = (price * qty).quantize(CENT, rounding=ROUND_HALF_UP)
tax = (subtotal * rate / 100).quantize(CENT, rounding=ROUND_HALF_UP)
total = subtotal + tax
```
Printing a Decimal shows exactly the digits it has, so a quantized value prints with 2 decimals.
