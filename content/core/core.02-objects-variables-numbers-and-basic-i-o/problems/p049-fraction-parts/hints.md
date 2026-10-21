## Hint 1

On a number line, where is -22/7 (about -3.14)? Which whole number is directly **below** it?
Which is closer to zero?

## Hint 2

`//` and `%` work on Fractions just as on ints: `f // 1` is the floor (an int), and `f % 1` is
what is left, a Fraction from 0 up to (but not including) 1.

## Hint 3

```
whole = f // 1
rest = f % 1
print("floor:", whole)
print("remainder:", rest)
print("truncated:", int(f))
print("rounded:", round(f))
print("check:", whole + rest == f)
```
