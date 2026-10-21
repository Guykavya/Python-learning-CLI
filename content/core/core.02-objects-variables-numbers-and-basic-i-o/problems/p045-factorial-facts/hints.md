## Hint 1

How many digits does 999 have? 1000? What are `log10(999)` and `log10(1000)`?

## Hint 2

`25 = 5 x 5`, so the number 25 in the product contributes **two** factors of 5. `n // 5` counts it only once.

## Hint 3

```
print("Digits:", int(math.log10(f)) + 1)
print("Trailing zeros:", n // 5 + n // 25 + n // 125 + n // 625)
```
