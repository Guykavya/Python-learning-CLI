# Jump game

`nums[i]` is the **maximum** jump length from index `i`: from `i` you may move to any index `i + 1 .. i + nums[i]`. You start at index 0. Write `can_jump(nums)` that returns `True` if you can reach the **last** index, `False` otherwise (chapter section 11).

## Example

```python
>>> can_jump([2, 3, 1, 1, 4])
True
>>> can_jump([3, 2, 1, 0, 4])        # every path lands on the 0 at index 3
False
>>> can_jump([0])                    # already at the last index
True
>>> can_jump([2, 0, 0])              # jump 2 straight over the first zero
True
```

## Constraints

- `1 <= len(nums) <= 10**5`, `0 <= nums[i] <= 10**5`.
- Your solution should be `O(n)`: one pass, no list of "reachable" flags filled jump by jump.

## Think about

The set of indices you can reach is always a block `0 .. farthest` with no holes. Why? And why does that mean one number is enough to remember?
