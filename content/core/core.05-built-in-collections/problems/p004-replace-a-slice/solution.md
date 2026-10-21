## Approach

Slice assignment removes the stretch `i` to `j` (not including `j`) and puts in all the items
of the right-hand side. Lengths do not have to match.

## Code

```python
nums = [int(x) for x in input().split()]
i, j = [int(x) for x in input().split()]
new = [int(x) for x in input().split()]
nums[i:j] = new
print(" ".join(str(n) for n in nums) if nums else "(empty)")
```

## Complexity

O(n): the items after the slice may need to shift left or right.

## Another way

`nums = nums[:i] + new + nums[j:]` gives the same result but builds a new list instead of
changing the old one.
