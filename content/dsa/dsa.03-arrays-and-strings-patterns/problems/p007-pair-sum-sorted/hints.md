## Hint 1

The smallest element plus the largest element is too big. Can the largest element be part of **any** pair? Every
other partner for it is at least as big as the smallest one.

## Hint 2

If `a[i] + a[j]` is too big, `a[j]` is useless (pairing it with anything at or after `i` is just as big or bigger):
drop it with `j -= 1`. If it is too small, `a[i]` is useless: `i += 1`. Each step throws away one element for good.

## Hint 3

```
i, j = 0, n - 1
while i < j:
    s = a[i] + a[j]
    if s == target: print(i + 1, j + 1); stop
    elif s < target: i += 1
    else: j -= 1
if nothing was printed: print(-1)
```
