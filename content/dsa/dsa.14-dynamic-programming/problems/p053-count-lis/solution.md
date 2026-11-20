## Approach

Extend the `O(n^2)` LIS table of chapter section 13 with a **count** per index:

- `f[i]` = the longest increasing subsequence that ends at `i`;
- `c[i]` = the number of increasing subsequences of length `f[i]` that end at `i`.

Every subsequence ending at `i` (longer than 1) is a subsequence ending at some `j < i` with `nums[j] < nums[i]`, plus `nums[i]`. Different `j` give different subsequences, so the counts add up, but only for the `j` that reach the best length.

```python
def count_lis(nums):
    n = len(nums)
    if n == 0:
        return 0
    f = [1] * n                          # f[i]: LIS length ending at i
    c = [1] * n                          # c[i]: how many of that length end at i
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if f[j] + 1 > f[i]:
                    f[i] = f[j] + 1
                    c[i] = c[j]          # a longer length: forget the old count
                elif f[j] + 1 == f[i]:
                    c[i] += c[j]         # same length: more ways
    best = max(f)
    total = 0
    for i in range(n):
        if f[i] == best:
            total += c[i]
    return total
```

`[1, 3, 5, 4, 7]`: `f = [1, 2, 3, 3, 4]`, `c = [1, 1, 1, 1, 2]` (index 4 is reached at length 4 from both 5 and 4). The best length 4 ends only at index 4: answer 2.

`[2, 2, 2, 2, 2]`: no `j` qualifies (not strictly smaller), every `f[i] = 1`, `c[i] = 1`, and all five end a longest subsequence: answer 5.

## Complexity

`O(n^2)` time, `O(n)` space.

## Another way

Top-down with a memo: `ends(i)` returns the pair `(length, count)` for index `i`, combining the pairs of all `j < i` with `nums[j] < nums[i]` with the same rule. There is also an `O(n log n)` method that keeps, for each length, a sorted list of endings with prefix sums of counts; it is much harder to get right, and the pair rule above is the core of it.
