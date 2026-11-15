## Approach

Backtracking over "which bucket gets the next number". No bucket may exceed `side`; since the total is exactly `k * side`, when every number is placed all buckets are full. Prunings: impossible inputs are rejected before searching; numbers are placed largest first; and buckets with equal current sums are interchangeable, so only the first of them is tried (this also covers the many empty buckets at the start).

## Code

```python
def can_partition_k(nums, k):
    total = sum(nums)
    if total % k != 0:
        return False
    side = total // k
    nums = sorted(nums, reverse=True)
    if nums[0] > side:
        return False
    buckets = [0] * k

    def go(i):
        if i == len(nums):
            return True
        tried = set()
        for b in range(k):
            if buckets[b] + nums[i] > side or buckets[b] in tried:
                continue
            tried.add(buckets[b])
            buckets[b] += nums[i]          # choose
            if go(i + 1):                  # explore
                return True
            buckets[b] -= nums[i]          # un-choose
        return False

    return go(0)
```

## Complexity

The worst case is still about `k^n`, but the "equal buckets" rule removes the `k!` ways of naming the same grouping, and largest-first fails early. On the 16-number test it makes about 9,000 calls instead of millions.

## Another way

Fill **one bucket at a time** with a bit mask of used numbers, and memoise on the mask: `O(n * 2^n)` time. That is the dynamic-programming version of the same search.
