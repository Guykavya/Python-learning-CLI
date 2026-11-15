## Hint 1

How many windows of length `L` does a string of length `n` have? How would a set tell you that you saw a window before?

## Hint 2

Slide `i` from 0 to `n - L`. `seg = s[i:i+L]`. If `seg` is already in `seen`, put it in `repeated`; else add it to `seen`.

## Hint 3

```
seen = set(); repeated = set()
for i in range(len(s) - L + 1):
    seg = s[i:i+L]
    if seg in seen: repeated.add(seg)
    else: seen.add(seg)
```
