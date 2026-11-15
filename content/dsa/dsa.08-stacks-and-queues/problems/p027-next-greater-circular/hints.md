## Hint 1

Write `x = nums[i % n]` for `i` in `range(2 * n)`. The popping loop is exactly the one of problem 26. What changes for the push?

## Hint 2

```
for i in range(2 * n):
    x = nums[i % n]
    while stack and nums[stack[-1]] < x:
        ans[stack.pop()] = x
    if i < n: stack.append(i)
```
