## Approach

The recipe from chapter section 5:

- **State:** `f(i)` = the best total using only the first `i` houses.
- **Transition:** skip house `i` and get `f(i - 1)`, or rob it and get `f(i - 2) + nums[i - 1]`. Take the max.
- **Base:** `f(0) = 0`, `f(1) = nums[0]`.
- **Answer:** `f(n)`.

`f(i)` reads only the two cells before it, so two rolling variables are enough (chapter section 6):

```python
def rob(nums):
    prev2, prev1 = 0, 0          # f(i-2), f(i-1)
    for money in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1
```

Starting both at 0 makes `f(1) = max(0, 0 + nums[0]) = nums[0]` automatically, and an empty list returns 0.

## Complexity

`O(n)` time, `O(1)` space.

## Another way

The full table, as in the chapter, which you can print while debugging:

```python
def rob(nums):
    n = len(nums)
    f = [0] * (n + 1)
    if n >= 1:
        f[1] = nums[0]
    for i in range(2, n + 1):
        f[i] = max(f[i - 1], f[i - 2] + nums[i - 1])
    return f[n]
```

A memoised `go(i) = max(go(i + 1), nums[i] + go(i + 2))` is also right, but 100,000 levels deep it raises `RecursionError`.
