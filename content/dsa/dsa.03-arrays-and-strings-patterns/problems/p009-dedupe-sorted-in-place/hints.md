## Hint 1

When the fast pointer reads a value, how do you know whether it is new? In a **sorted** array, which single earlier
value do you need to compare it with?

## Hint 2

Compare `a[r]` with `a[w - 1]`, the last value you kept. If they differ, write it at `a[w]` and grow `w`. The first
element is always kept, so you can start with `w = 1` and `r = 1` (when `n > 0`).

## Hint 3

```
if n == 0: k = 0
else:
    w = 1
    for r in 1 .. n-1:
        if a[r] != a[w - 1]:
            a[w] = a[r]; w += 1
    k = w
print k, then a[:k]
```
