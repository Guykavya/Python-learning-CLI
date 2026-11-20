## Hint 1

Sort the pairs by their first value. If `(a, b)` can come right before `(c, d)` then `a < b < c`, so it is earlier in the sorted list. Now every chain is a **subsequence** of the sorted list, as in LIS (you will meet it in section 13).

## Hint 2

State: `f[i]` = the length of the longest chain that **ends with** pair `i`. Base: `f[i] = 1` (the pair alone). Transition: look at every `j < i` whose second value is `< pairs[i][0]`. The answer is `max(f)`: the best chain may end with any pair.

## Hint 3

```
pairs = sorted(pairs)
f = [1] * n
for i in 0 .. n-1:
    for j in 0 .. i-1:
        if pairs[j][1] < pairs[i][0]:
            f[i] = max(f[i], f[j] + 1)
return max(f) or 0 for an empty list
```
