## Hint 1

Walk from left to right and remember `farthest`: the largest index you know you can reach. When you arrive at index `i`, how can you tell whether `i` itself is reachable? If it is, how far can you get from it?

## Hint 2

If `i > farthest`, nothing before `i` can jump to `i` or beyond, so you are stuck. Otherwise update `farthest = max(farthest, i + nums[i])`. A zero is only a problem when `farthest` stops exactly on it.

## Hint 3

```
farthest = 0
for i, jump in enumerate(nums):
    if i > farthest: return False
    farthest = max(farthest, i + jump)
return True
```
