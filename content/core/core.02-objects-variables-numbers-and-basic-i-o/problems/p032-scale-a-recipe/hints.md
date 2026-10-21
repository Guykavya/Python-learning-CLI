## Hint 1

If you store `1/3` as a float, can you ever print it as the fraction `1/3` again?

## Hint 2

`Fraction("3/4")` reads the text exactly. Multiplying or dividing a Fraction by an int keeps it a Fraction.

## Hint 3

```
scaled = Fraction(input()) * want / have
print(f"Cups: {scaled}")
print(f"About: {float(scaled):.3f}")
```
