## Hint 1

Keep two lists. `f[i]` = the LIS length ending at `i` (as in p051), and `c[i]` = **how many** increasing subsequences of that length end at `i`. Start with `f[i] = 1`, `c[i] = 1` (the item alone).

## Hint 2

For each `j < i` with `nums[j] < nums[i]`, the subsequences ending at `j` extended by `nums[i]` have length `f[j] + 1`.

- If `f[j] + 1 > f[i]`: a new best length. The old ones no longer count: `f[i] = f[j] + 1`, `c[i] = c[j]`.
- If `f[j] + 1 == f[i]`: more subsequences of the same best length: `c[i] += c[j]`.
- If smaller: ignore.

## Hint 3

The longest subsequences may end at several indices. Add up `c[i]` for every `i` whose `f[i]` equals the maximum.

```
L = max(f)
return sum(c[i] for i in range(n) if f[i] == L)      # 0 for an empty list
```
