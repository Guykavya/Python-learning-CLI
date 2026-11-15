## Approach

A circle is a line that is read twice. On the first lap every index is pushed and waits as usual. On the second lap no new index is pushed; the numbers only act as possible answers for indices still waiting from the first lap. After two laps, anyone still waiting is a maximum of the circle: nothing is greater.

## Code

```python
def next_greater_circular(nums):
    n = len(nums)
    ans = [-1] * n
    stack = []
    for i in range(2 * n):
        x = nums[i % n]
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x
        if i < n:
            stack.append(i)
    return ans
```

## Complexity

`O(n)` time: `2n` steps of the outer loop, and each index is pushed once and popped at most once. `O(n)` memory.

## Another way

Build the doubled list `nums + nums`, run the plain `next_greater` of problem 26 on it, and keep the first `n` answers. It is the same idea with `O(n)` extra memory for the copy; the `i % n` version avoids the copy.
