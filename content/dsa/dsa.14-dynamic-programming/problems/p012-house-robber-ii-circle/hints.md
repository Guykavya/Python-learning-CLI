## Hint 1

In any valid choice, the first house and the last house are not **both** robbed. So at least one of them is untouched. Case A: the last house is not robbed. Then the circle is just the row `nums[0 .. n-2]`. Case B: the first house is not robbed. Then it is the row `nums[1 .. n-1]`. Is every valid choice in case A or case B?

## Hint 2

The answer is the better of the two row answers. Watch the case `n = 1`: both rows are empty, but the single house has no neighbour (it is not its own neighbour), so the answer is `nums[0]`.

## Hint 3

```
def row(houses):              # p011
    prev2, prev1 = 0, 0
    for money in houses:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1

if len(nums) == 1: return nums[0]
return max(row(nums[:-1]), row(nums[1:]))
```
