## Hint 1

Keep a range `lo .. hi` of indexes where the first bad version can still be. What should the
range be at the start if "no bad version at all" is also a possible answer? (Try letting
`hi = n` mean "none of them".) If `versions[mid]` is bad, can the answer be after `mid`? If it
is good, can it be at `mid`?

## Hint 2

Loop while the range has more than one candidate, and never test the same version twice.

```
lo, hi = 0, len(versions)          # answer index is in [lo, hi]; hi == n means "none"
while lo < hi:
    mid = (lo + hi) // 2
    if is_bad(versions[mid]): hi = mid       # mid could be the first bad one
    else:                     lo = mid + 1   # first bad is after mid
return versions[lo] if lo < len(versions) else None
```

Count how many calls that makes for n = 1, 2, 3, 8.
