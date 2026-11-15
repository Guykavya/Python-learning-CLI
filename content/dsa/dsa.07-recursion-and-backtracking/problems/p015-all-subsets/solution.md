## Approach

Every node of the "choose the next item" tree is a subset. Record a **copy** of the path at every call, then extend it with each later item in turn. The `start` index stops us from going back, so each subset is built exactly once, in increasing position order.

## Code

```python
def subsets(nums):
    result = []
    path = []

    def go(start):
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])     # choose
            go(i + 1)                # explore
            path.pop()               # un-choose

    go(0)
    return result
```

## Complexity

`2^n` subsets, each copied in up to `O(n)` time: `O(n * 2^n)` time and memory for the output. The stack depth is `n`.

## Another way

Include/exclude recursion (view 1) or bit masks (view 3): for `mask` in `range(2 ** n)`, take `nums[i]` when bit `i` of `mask` is set.
