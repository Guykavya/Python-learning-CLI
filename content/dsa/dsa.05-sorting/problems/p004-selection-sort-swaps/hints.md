## Hint 1

For each `i`, what are you searching for in the part `a[i:]`? How do you remember the best position while scanning?

## Hint 2

Keep `m = i`, then for `j` from `i + 1` to the end do `if a[j] < a[m]: m = j`. Use `<` (not `<=`) so ties keep the leftmost minimum.

## Hint 3

```
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        if a[j] < a[m]: m = j
    if m != i: swap, swaps += 1
```
