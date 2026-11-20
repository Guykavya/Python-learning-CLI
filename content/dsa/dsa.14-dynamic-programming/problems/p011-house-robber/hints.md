## Hint 1

`f(i)` = the most money from the first `i` houses. If you skip house `i` (that is `nums[i - 1]`), you get `f(i - 1)`. If you rob it, you could not rob house `i - 1`, so you get `f(i - 2) + nums[i - 1]`. What are `f(0)` and `f(1)`?

## Hint 2

```
f = [0] * (n + 1)
if n >= 1: f[1] = nums[0]
for i in 2..n:
    f[i] = max(f[i-1], f[i-2] + nums[i-1])
return f[n]
```

Then, if you like, roll it into two variables (chapter section 6).
