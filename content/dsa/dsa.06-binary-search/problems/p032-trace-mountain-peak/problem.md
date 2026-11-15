# Trace the search for a mountain peak

Predict **exactly** what this program prints. Do not run it.

```python
a = [1, 3, 8, 12, 9, 5, 2]
lo, hi = 0, len(a) - 1
while lo < hi:
    mid = (lo + hi) // 2
    if a[mid] < a[mid + 1]:
        print("lo", lo, "mid", mid, "hi", hi, a[mid], "<", a[mid + 1], "go right")
        lo = mid + 1
    else:
        print("lo", lo, "mid", mid, "hi", hi, a[mid], ">", a[mid + 1], "go left")
        hi = mid
print("peak index", lo, "value", a[lo])
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

The mountain is `[1, 3, 8, 12, 9, 5, 2]`. Every step compares `a[mid]` with its right neighbour `a[mid + 1]` and prints both values around a `<` or `>` sign, then the direction.
Notice the shape: `lo < hi` with `hi = mid` in one branch and `lo = mid + 1` in the other.

## After you answer

1. Why can `hi = mid` (not `mid - 1`) be written in the falling branch?
2. Why is it always safe to read `a[mid + 1]`?
3. The loop ends with `lo == hi`. Why is that index the peak?
