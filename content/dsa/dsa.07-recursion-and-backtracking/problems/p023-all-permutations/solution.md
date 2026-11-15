## Approach

Fill the positions one by one. At each level any item that is not already in the path may go next, which the `used` list tells in `O(1)`. Un-choose both the path and the flag after the recursive call.

## Code

```python
def permute(nums):
    result, path = [], []
    used = [False] * len(nums)

    def go():
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True            # choose
            path.append(nums[i])
            go()                      # explore
            path.pop()                # un-choose
            used[i] = False

    go()
    return result
```

## Complexity

`n!` permutations, each copied in `O(n)`: `O(n * n!)` time. Depth `n`.

## Another way

The swap method (chapter section 8): put each item at position `i` by swapping, recurse on `i + 1`, swap back. No `used` list, but the output order is not sorted.
