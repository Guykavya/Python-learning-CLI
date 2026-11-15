## Hint 1

What is `gcd(g, x)` when you add one more number `x` to a group whose gcd is `g`? What should `g` start as, so
that the first number is handled like all the others?

## Hint 2

Start with `g = 0`: `gcd(0, x) = x`. Or start with `g = a[0]` and fold the rest. Do **not** start with 1: that
would make the answer always 1.

## Hint 3

```
g = 0
for x in a: g = gcd(g, x)      # Euclid inside
count = number of x with x == g
total = sum of x // g
print g, count, total
```
