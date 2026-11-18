## Hint 1

Fix the end. `f[i]` = the length of the longest increasing subsequence that **ends at index `i`** (with `nums[i]` as its last item). Every item alone is such a subsequence, so `f[i] >= 1`.

## Hint 2

A subsequence ending at `i` is some subsequence ending at an earlier `j`, followed by `nums[i]`. That is allowed only if `nums[j] < nums[i]` (strictly). So `f[i] = 1 + max(f[j])` over those `j`, or 1 if there is none. The longest subsequence can end anywhere, so the answer is the **maximum** of all `f[i]` (0 for an empty list).

## Hint 3

```
if nums is empty: return 0
f = [1] * n
for i in range(n):
    for j in range(i):
        if nums[j] < nums[i]:
            f[i] = max(f[i], f[j] + 1)
return max(f)
```
