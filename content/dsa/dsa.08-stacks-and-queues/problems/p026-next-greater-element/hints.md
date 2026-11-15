## Hint 1

Keep `waiting`, a list of indices whose answer is not known yet. When `x = nums[i]` arrives, who can it answer: the bottom of the stack or the top? When can you stop popping?

## Hint 2

```
ans = [-1] * len(nums)
for i, x in enumerate(nums):
    while waiting and nums[waiting[-1]] < x:
        ans[waiting.pop()] = x
    waiting.append(i)
return ans
```
