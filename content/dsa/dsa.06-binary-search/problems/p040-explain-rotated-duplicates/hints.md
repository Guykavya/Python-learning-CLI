## Hint 1

Try to decide where the minimum is for `[3, 3, 3, 1, 3]` and `[3, 1, 3, 3, 3]` using only `a[lo]`, `a[mid]`, `a[hi]`. Are the three numbers the same in both?

## Hint 2

If `a[hi]` equals `a[mid]` and `mid < hi`, a copy of the value `a[hi]` stays at `mid` after you drop `hi`. So if `a[hi]` was the minimum, the minimum value is still in the range.

## Hint 3

Consider `[1, 1, 1, 1, 0, 1, 1]`. Each step that sees `a[mid] == a[hi]` can only remove one element. A single different value can hide anywhere, so any algorithm must look at every position in the worst case.
