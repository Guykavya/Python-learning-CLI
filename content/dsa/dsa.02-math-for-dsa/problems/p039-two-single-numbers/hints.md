## Hint 1

XOR all numbers. What do you get? Is it zero? Why not?

## Hint 2

If `x = a ^ b` and `x` has a 1 at some bit, what do `a` and `b` look like at that bit? Now think of the lowest 1 bit of `x`:
`x & -x`. If you separate the numbers by whether they have that bit, where do the two copies of a repeated number go?

## Hint 3

```
x = XOR of all
low = x & -x
a = 0; b = 0
for v in values:
    if v & low: a ^= v
    else:       b ^= v
print(min(a, b), max(a, b))
```
