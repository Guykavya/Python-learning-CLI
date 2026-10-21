## Hint 1

What happens if you call `float("1/3")`? What other type can read text like `"1/3"`?

## Hint 2

`Fraction("1/3")` builds the exact value one third. Arithmetic between Fractions stays exact.

## Hint 3

```
x = Fraction(input())
y = Fraction(input())
print(x + y)
print(x * y)
print(float(x + y))
```
