## Hint 1

Draw `[1, 3, 4, 2, 2]` as arrows: `0 -> 1`, `1 -> 3`, `2 -> 4`, `3 -> 2`, `4 -> 2`. Follow them from 0. Which node has two arrows coming in, and what is its index?

## Hint 2

"Move one step" is `x = nums[x]`; "move two steps" is `x = nums[nums[x]]`. Run phase 1 of Floyd from index 0 until `slow == fast`, then phase 2: `p = 0`, move `p` and `slow` one step each until they are equal. Here you compare integers (indexes), so `==` is right.

## Hint 3

```
slow = fast = 0
repeat: slow = nums[slow]; fast = nums[nums[fast]]; stop when slow == fast
p = 0
while p != slow: p = nums[p]; slow = nums[slow]
return p
```
