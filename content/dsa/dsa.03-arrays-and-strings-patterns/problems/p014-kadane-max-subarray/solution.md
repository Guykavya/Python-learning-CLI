## Approach

Every subarray ends somewhere. For each end position, the best subarray ending there is either the element alone or
the element added to the best subarray ending one step earlier. That gives `cur`. The answer is the largest `cur`
over all end positions.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

cur = best = a[0]
for x in a[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)

print(best)
```

## Complexity

O(n) time, O(1) extra memory. Checking all subarrays is O(n^2) even with a running sum, about 2 * 10^10 steps here.

## Another way

With prefix sums, the subarray `a[l..r]` sums to `p[r + 1] - p[l]`. For each `r`, subtract the **smallest** prefix
seen so far (`min(p[0..r])`). Keeping that running minimum is also O(n) and gives the same answer; Kadane's `cur` is
exactly `p[r + 1] - min(p[0..r])`.
