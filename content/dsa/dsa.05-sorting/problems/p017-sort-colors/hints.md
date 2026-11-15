## Hint 1

There are only three different values. Do you need to compare elements at all, or is it enough to know how many of each there are?

## Hint 2

Counting: `c = [0, 0, 0]`, increase `c[x]` for each value, then print `c[0]` zeros, `c[1]` ones and `c[2]` twos. One pass to count, one pass to write.

## Hint 3

Dutch flag in one pass: `lo = 0, i = 0, hi = n - 1`. If `a[i] == 0` swap with `a[lo]`, `lo++`, `i++`; if `a[i] == 2` swap with `a[hi]`, `hi--` (do NOT advance `i`); else `i++`. Stop when `i > hi`.
