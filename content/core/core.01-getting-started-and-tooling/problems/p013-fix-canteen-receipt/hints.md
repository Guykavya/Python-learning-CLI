## Hint 1

Why does nothing at all print the first time you run it, not even
"Canteen receipt"? What kind of error is found before any line runs?

## Hint 2

The three errors are a `SyntaxError` (a bracket never closed), a `TypeError`
(joining text and a number with `+`) and a `NameError` (a typo). Python shows
them one at a time, in that order.

## Hint 3

- Last line: add the missing `)`.
- Quantity line: `"Quantity: " + str(quantity)`, or `print("Quantity:", quantity)`.
- Total line: use the name that was actually defined.
