## Approach

Take Kadane's "ends here" state from p013 and add the fact that a sign change swaps the roles of big and small:

- **State:** `hi(i)` and `lo(i)` = the largest and the smallest product of a block ending exactly at `i`.
- **Transition:** a block ending at `i` is `nums[i]` alone or extends a block ending at `i - 1`. Multiplying by `x = nums[i]` keeps or reverses the order, so the extreme values come from the extremes: `hi(i) = max(x, hi(i-1) * x, lo(i-1) * x)` and `lo(i) = min(...)` of the same three.
- **Base:** `hi(0) = lo(0) = nums[0]`.
- **Answer:** the max of `hi(i)` over all `i`.

```python
def max_product(nums):
    hi = lo = best = nums[0]          # largest and smallest product ending here
    for x in nums[1:]:
        candidates = (x, hi * x, lo * x)
        hi, lo = max(candidates), min(candidates)
        if hi > best:
            best = hi
    return best
```

Zeros need no special case: after `x = 0`, all three candidates are 0, and at the next index the candidate `x` alone restarts the block.

## Complexity

`O(n)` time, `O(1)` space.

## Another way

Without zeros, the best block is a **prefix** or a **suffix** of the list: if the number of negatives is even, the whole list is best; if it is odd, you drop everything up to the first negative or from the last negative on. Zeros cut the list into pieces. So scan from the left and from the right with a running product that restarts after a zero, and keep the max:

```python
def max_product(nums):
    best = max(nums)
    for seq in (nums, nums[::-1]):
        product = 1
        for x in seq:
            product = x if product == 0 else product * x
            best = max(best, product)
    return best
```
