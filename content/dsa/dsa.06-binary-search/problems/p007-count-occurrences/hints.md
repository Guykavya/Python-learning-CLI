## Hint 1

Where does the block of equal values `x` start, and where does it end (one past the last)? The count is the length of that block.

## Hint 2

The block starts at the first index with `a[i] >= x` and ends before the first index with `a[i] > x`. Two binary searches that differ in one comparison.

## Hint 3

```
def first_not_less(x, strict):    # strict False: first a[i] >= x ; strict True: first a[i] > x
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x or (strict and a[mid] == x): lo = mid + 1
        else: hi = mid
    return lo
answer = first_not_less(x, True) - first_not_less(x, False)
```
