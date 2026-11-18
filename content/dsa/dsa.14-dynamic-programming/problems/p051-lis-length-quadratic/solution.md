## Approach

The "ends at `i`" state of chapter section 13:

- State: `f[i]` = length of the longest strictly increasing subsequence that ends with `nums[i]`.
- Transition: `f[i] = 1 + max(f[j])` over `j < i` with `nums[j] < nums[i]`; 1 if there is no such `j`.
- Base: every `f[i]` starts at 1 (the item alone).
- Answer: `max(f)`, because the best subsequence may end at any index. An empty list has answer 0.

```python
def lis_length(nums):
    n = len(nums)
    if n == 0:
        return 0
    f = [1] * n                          # f[i]: longest increasing subsequence ending at i
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and f[j] + 1 > f[i]:
                f[i] = f[j] + 1
    return max(f)
```

For `[10, 9, 2, 5, 3, 7, 101, 18]`, `f = [1, 1, 1, 2, 2, 3, 4, 4]` and the answer is 4 (chapter section 13 traces every cell).

## Complexity

`O(n^2)` time (about 320,000 comparisons for 800 items), `O(n)` space.

## Another way

The `tails` list with `bisect_left` (chapter section 13, and problem p052) gives the length in `O(n log n)`. Another view: the LIS of `nums` is the LCS of `nums` and `sorted(set(nums))` (a strictly increasing subsequence is a common subsequence with the sorted distinct values), which is `O(n^2)` as well but uses more memory.
