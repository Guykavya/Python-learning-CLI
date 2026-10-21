## Approach

Build real tuples and print them. Python's own display handles the one-item comma and the
empty tuple.

## Code

```python
nums = [int(x) for x in input().split()]
print(tuple(nums))
print((min(nums), max(nums)))
print(tuple(n for n in nums if n % 2 == 0))
```

## Why the comma

`(5)` is just the number 5 in brackets. The comma makes a tuple, so Python shows a one-item
tuple as `(5,)` to make clear it is a tuple.
