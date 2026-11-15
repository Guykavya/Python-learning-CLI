## Approach

Every index waits in the stack until a strictly greater number arrives. The waiting values never increase from bottom to top (a larger value above a smaller one would already have answered it), so a new `x` answers a run of waiting indices **at the top**, and the first top that is not smaller stops the loop. Whatever is still waiting at the end has no greater element and keeps `-1`.

## Code

```python
def next_greater(nums):
    ans = [-1] * len(nums)
    waiting = []                               # indices whose answer is not known yet
    for i, x in enumerate(nums):
        while waiting and nums[waiting[-1]] < x:
            ans[waiting.pop()] = x
        waiting.append(i)
    return ans
```

## Complexity

`O(n)` time: each index is pushed once and popped at most once, so the `while` loop runs at most `n` times **in total**. `O(n)` memory.

## Another way

Scan from the **right** and keep a stack of candidates: pop every value `<= x` (they are hidden behind `x` for everything to the left), then the top, if any, is `x`'s answer; push `x`. Same cost, and the answer is found when the element is visited instead of when it is popped.

```python
def next_greater(nums):
    ans = [-1] * len(nums)
    stack = []
    for i in range(len(nums) - 1, -1, -1):
        while stack and stack[-1] <= nums[i]:
            stack.pop()
        if stack:
            ans[i] = stack[-1]
        stack.append(nums[i])
    return ans
```
