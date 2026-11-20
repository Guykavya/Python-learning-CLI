## Hint 1

Write the recipe first. State: `f[i]` = the fewest jumps to arrive at index `i`. Base: `f[0] = 0`. Every other cell starts as `INF` ("not reached yet"). Answer: `f[n - 1]`, or `-1` if it is still `INF`. What is the transition: from which cells can you arrive at `j`?

## Hint 2

It is easier to **push** forward than to pull back. When `f[i]` is final, index `i` can send `f[i] + 1` to every `j` in `i + 1 .. i + nums[i]`. Keep the smaller value at `j`. Why is `f[i]` final when the left-to-right loop reaches `i`?

## Hint 3

```
f = [INF] * n;  f[0] = 0
for i in 0 .. n-1:
    if f[i] is INF: skip          # nobody reaches i
    for j in i+1 .. min(n-1, i+nums[i]):
        f[j] = min(f[j], f[i] + 1)
return -1 if f[n-1] is INF else f[n-1]
```
