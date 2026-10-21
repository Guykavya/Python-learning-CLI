## Hint 1

In `x ** n * t`, which operator is applied first?

## Hint 2

Write the formula with brackets exactly where the maths has them: the rate per period is
`r / (100 * n)`, and the number of periods is `(n * t)`.

## Hint 3

```
a = p * (1 + r / (100 * n)) ** (n * t)
print(f"Amount: {a:,.2f}")
```
