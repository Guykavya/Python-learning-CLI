## Hint 1

Compare a middle element with its right neighbour. If `a[mid] < a[mid + 1]`, are you on the rising slope or the falling slope? Where is the peak then?

## Hint 2

Rising slope (`a[mid] < a[mid + 1]`): the peak is to the right, `lo = mid + 1`. Falling slope: `mid` could be the peak itself, so `hi = mid`. Use `while lo < hi`; at the end `lo` is the peak. The predicate "`a[i] > a[i + 1]`" is False...False True...True.

## Hint 3

```
lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if ask(mid) < ask(mid + 1): lo = mid + 1
    else: hi = mid
print("!", lo)
```
`mid + 1 <= hi` always holds because `mid < hi` inside the loop.
