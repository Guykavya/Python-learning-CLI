## Approach

The circle adds one rule to the row of p011: the first and the last house may not both be robbed. So every valid choice leaves the first house alone **or** leaves the last house alone (or both). That splits the problem into two row problems:

- without the last house: the row `nums[:-1]`;
- without the first house: the row `nums[1:]`.

Every valid circle choice is a valid choice in at least one of the rows, and every row choice is valid on the circle (the first and last of the circle are never both in one row). So the answer is the max of the two row answers. With one house, both rows are empty, but a lone house has no neighbour: answer `nums[0]`.

```python
def rob_row(houses):
    prev2, prev1 = 0, 0
    for money in houses:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1


def rob_circle(nums):
    if len(nums) == 1:
        return nums[0]
    return max(rob_row(nums[:-1]), rob_row(nums[1:]))
```

## Complexity

`O(n)` time. The slices copy the list, `O(n)` extra space; pass start and end indices to `rob_row` instead if you want `O(1)`.

## Another way

Add the missing fact to the state: run the row DP twice, once where the first house is **forced out** and once where it is **allowed**, and in the second run forbid the last house. This is the same split, written as a state flag. The general lesson: when a circle breaks a DP, **fix a decision at the joint** (here, "is house 0 robbed?") and solve each case as a line.
