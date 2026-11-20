## Approach

Keep the farthest reachable index. Reachable indices always form a prefix `0 .. farthest`: if index `k` can jump to an index `j`, it can also land on every index between `k` and `j`. So the moment an index lies beyond `farthest`, it and everything after it is out of reach.

```python
def can_jump(nums):
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest:
            return False                       # a gap: nothing reaches i
        farthest = max(farthest, i + jump)
    return True
```

The `max` matters: a short jump from a later index must not shrink what an earlier index already reached.

## Complexity

One pass: `O(n)` time, `O(1)` extra space.

## Another way

Work backwards with a **goal**. The last index is the goal. Going from right to left, if index `i` can jump to the goal (`i + nums[i] >= goal`), then `i` becomes the new goal, because reaching `i` is now enough. At the end, the answer is `goal == 0`.

```python
def can_jump(nums):
    goal = len(nums) - 1
    for i in range(len(nums) - 2, -1, -1):
        if i + nums[i] >= goal:
            goal = i
    return goal == 0
```
