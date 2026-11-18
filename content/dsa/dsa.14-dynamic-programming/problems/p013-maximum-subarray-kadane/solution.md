## Approach

Chapter section 5 strengthens the state so that it has a transition:

- **State:** `f(i)` = the best sum of a block that **ends exactly at `i`**.
- **Transition:** the block is `nums[i]` alone or extends the best block ending at `i - 1`: `f(i) = max(nums[i], f(i - 1) + nums[i])`.
- **Base:** `f(0) = nums[0]`.
- **Answer:** `max(f(i))` over all `i`.

Each `f(i)` reads only `f(i - 1)`, so one variable `cur` holds it, and `best` keeps the running maximum.

```python
def max_subarray(nums):
    cur = best = nums[0]             # f(0), and the best so far
    for x in nums[1:]:
        cur = max(x, cur + x)        # f(i) = max(nums[i], f(i-1) + nums[i])
        if cur > best:
            best = cur
    return best
```

`max(x, cur + x)` restarts the block exactly when `cur < 0`: a negative prefix only makes things worse.

## Complexity

`O(n)` time, `O(1)` space.

## Another way

**Prefix sums.** The sum of block `i..j` is `P[j+1] - P[i]`. For each end, subtract the smallest prefix seen so far:

```python
def max_subarray(nums):
    best = nums[0]
    prefix = 0
    smallest = 0            # smallest prefix before the current end (the empty prefix is 0)
    for x in nums:
        prefix += x
        best = max(best, prefix - smallest)
        smallest = min(smallest, prefix)
    return best
```

Same `O(n)`. Updating `best` **before** `smallest` keeps the block non-empty.
