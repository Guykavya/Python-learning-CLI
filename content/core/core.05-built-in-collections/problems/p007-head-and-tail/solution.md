## Approach

Star unpacking does the splitting in one line. The starred name is always a list, so `sum`
and `join` work on it directly, even when it is empty.

## Code

```python
nums = [int(x) for x in input().split()]
first, *middle, last = nums
print("First:", first)
print("Last:", last)
print("Middle:", " ".join(str(n) for n in middle) if middle else "(none)")
print("Middle sum:", sum(middle))
```

## Complexity

O(n): the unpacking copies the middle items into a new list.

## Another way

`first, last, middle = nums[0], nums[-1], nums[1:-1]` does the same with slices.
