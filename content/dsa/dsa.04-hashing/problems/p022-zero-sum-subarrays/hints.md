## Hint 1

When does the sum of `a[l..r]` equal 0 in terms of prefix sums `p[l]` and `p[r+1]`?

## Hint 2

As you compute each new prefix sum `s`, the number of earlier equal prefix sums is the number of subarrays ending here with sum 0. Start with `seen = {0: 1}` for the empty prefix.

## Hint 3

```
seen = {0: 1}; s = 0; ans = 0
for x in a:
    s += x
    ans += seen.get(s, 0)
    seen[s] = seen.get(s, 0) + 1
```
