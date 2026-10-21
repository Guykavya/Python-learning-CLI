## Hint 1

Euclid's rule says: replace the pair `(a, b)` with `(b, a % b)`. When does that stop, and which number is the answer at that moment?

## Hint 2

Make both numbers non-negative with `abs()` first. Then loop `while b != 0`, and update both at the same time with `a, b = b, a % b`. If you update `a` first, you lose the old `a` before computing `a % b`.

## Hint 3

```
a = abs(a)
b = abs(b)
while b != 0:
    a, b = b, a % b
print(a)
```

Check the case `a = 0`, `b = 5`: one step gives `(5, 0)`, and the answer is 5.
