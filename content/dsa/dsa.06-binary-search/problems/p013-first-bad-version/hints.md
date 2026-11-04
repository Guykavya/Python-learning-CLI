## Hint 1

The predicate "version `v` is bad" is `False ... False True ... True`. What are you looking for in that pattern, the first True or the last False?

## Hint 2

Use the half-open template on `[1, n]`: `lo = 1`, `hi = n`, `while lo < hi`. If `mid` is bad, `B <= mid`, so `hi = mid`. If it is good, `B > mid`, so `lo = mid + 1`. When `lo == hi` you have `B` without asking again.

## Hint 3

```
n = int(input())
lo, hi = 1, n
while lo < hi:
    mid = (lo + hi) // 2
    print("?", mid, flush=True)
    if int(input()) == 1: hi = mid
    else: lo = mid + 1
print("!", lo, flush=True)
```
