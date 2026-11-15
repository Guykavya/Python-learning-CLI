## Hint 1

Which of the five commands need a position in the list? Can the same two searches (lower bound and upper bound) give that position for every command?

## Hint 2

`add x`: insert at `lower(x)` (or `upper(x)`; for equal numbers it does not matter). `remove x`: `i = lower(x)`; the value is present if `i < len(s)` and `s[i] == x`; then `del s[i]`. `count_le x` is `upper(x)`. `kth k` is `s[k - 1]` (check the range). `ceil x` is `s[lower(x)]` if it exists.

## Hint 3

```
def lower(x): first index with s[i] >= x
def upper(x): first index with s[i] > x
add:      s.insert(lower(x), x)
remove:   i = lower(x); if i < len(s) and s[i] == x: del s[i]; print 1 else print 0
count_le: print upper(x)
kth:      print s[k-1] if 1 <= k <= len(s) else "none"
ceil:     i = lower(x); print s[i] if i < len(s) else "none"
```
