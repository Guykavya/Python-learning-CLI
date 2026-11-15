## Hint 1

Let `side = sum(nums) // k`. The state is the list `buckets` of current sums. A call `go(i)` decides where `nums[i]` goes. When every number is placed, all buckets must be exactly `side` (why is that automatic if no bucket ever exceeds `side`?).

## Hint 2

In `go(i)`, try every bucket `b` with `buckets[b] + nums[i] <= side`: add, recurse, and if that fails, subtract again (un-choose). Return `True` as soon as one branch works.

## Hint 3

```
sort nums descending; buckets = [0] * k
def go(i):
    if i == len(nums): return True
    tried = set()
    for b in range(k):
        if buckets[b] + nums[i] > side or buckets[b] in tried: continue
        tried.add(buckets[b])
        buckets[b] += nums[i]
        if go(i + 1): return True
        buckets[b] -= nums[i]
    return False
```
