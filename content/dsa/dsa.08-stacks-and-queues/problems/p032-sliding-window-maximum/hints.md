## Hint 1

When index `i` with value `x` arrives, any index at the back with a value `<= x` is older **and** not larger, so it can never be the maximum of a window that contains `i`. Remove it. After appending `i`, when is the front index outside the window?

## Hint 2

```
for i, x in enumerate(nums):
    while dq and nums[dq[-1]] <= x: dq.pop()
    dq.append(i)
    if dq[0] <= i - k: dq.popleft()
    if i >= k - 1: out.append(nums[dq[0]])
```
