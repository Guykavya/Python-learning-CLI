## Approach

Index `i` is a node, `nums[i]` is its `next`. Every value is between `1` and `n`, so every arrow lands on a valid index: the walk never leaves the array, so it must eventually repeat a node, which means the chain from `0` ends in a cycle. No arrow points to `0` (no value is 0), so `0` is in the tail, a fine head. A value `v` that appears twice means two different indexes point to node `v`: one arrow from the tail and one from inside the cycle. A node with two incoming arrows on the walk is exactly the **entrance of the cycle**. Floyd's two phases (problem 19) find that entrance in `O(1)` memory, and its index is the duplicate value.

## Code

```python
def find_duplicate(nums):
    slow = fast = 0
    while True:                          # phase 1: meet inside the cycle
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    p = 0
    while p != slow:                     # phase 2: the entrance of the cycle
        p = nums[p]
        slow = nums[slow]
    return p
```

## Complexity

`O(n)` time (the same bound as problem 19), `O(1)` extra memory, and `nums` is only read.

## Another way

Binary search on the **value**: for a guess `m`, count how many numbers are `<= m`. If the count is greater than `m`, the duplicate is `<= m` (pigeonhole), otherwise it is greater. That is `O(n log n)` time and `O(1)` memory, also without modifying the array. With extra memory allowed, a `set` finds it in one pass; with modification allowed, sorting finds two equal neighbours.
