## Hint 1

Define the predicate "`a[i] >= x`". Along the list it looks like `False False ... True True`. What are you searching for in that pattern?

## Hint 2

You want the first `True`. If `a[mid] < x`, then `mid` is False, so the answer is at `mid + 1` or later: `lo = mid + 1`. Otherwise `mid` could be the answer, so keep it: `hi = mid`.

## Hint 3

```
lo, hi = 0, n
while lo < hi:
    mid = (lo + hi) // 2
    if a[mid] < x: lo = mid + 1
    else: hi = mid
print(lo)
```
Why can `hi` start at `n`? Because "index n" means "all elements are smaller", and the loop never reads `a[n]`.
