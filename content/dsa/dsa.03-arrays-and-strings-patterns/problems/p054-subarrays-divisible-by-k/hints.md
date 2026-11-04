## Hint 1

`P[i] - P[j]` is divisible by `k` when `P[i]` and `P[j]` leave the same remainder. So instead of looking at subarrays,
look at the list of prefix remainders. How many good subarrays end at position `i`, if you know how many earlier
prefixes had the same remainder?

## Hint 2

Keep a dictionary `seen` from remainder to count. Start with `seen = {0: 1}` for the empty prefix. For each element:
update `rem = (rem + x) % k`, add `seen[rem]` (0 if missing) to the total, then increase `seen[rem]`.

## Hint 3

```
seen = {0: 1}; rem = 0; total = 0
for x in a:
    rem = (rem + x) % k
    total += seen.get(rem, 0)
    seen[rem] += 1
print total
```

You can keep only the remainder, never the full prefix sum: `(rem + x) % k` has the same remainder as `P + x`.
