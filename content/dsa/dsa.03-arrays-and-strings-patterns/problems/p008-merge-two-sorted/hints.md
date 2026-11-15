## Hint 1

The smallest element of the result is either `a[0]` or `b[0]`. Once you have taken it, what is the next candidate
from that array?

## Hint 2

Loop while both pointers are inside their arrays: compare `a[i]` and `b[j]`, append the smaller, advance its pointer.
After the loop at most one array has elements left, and they are all at least as big as everything taken.

## Hint 3

```
i = j = 0; out = []
while i < n and j < m:
    if a[i] <= b[j]: out.append(a[i]); i += 1
    else:            out.append(b[j]); j += 1
out += a[i:] + b[j:]
print out
```
