## Hint 1

"A repeat of length `L` exists" is true for small `L` and false for large `L` (drop the last character of both copies of a repeat to get a shorter one). So binary search the largest `L` for which it is true (dsa.06).

## Hint 2

Test one length with prefix hashes: `H[i]` = hash of `s[:i]`, `P[i] = B**i`, and `hash(s[l:r]) = (H[r] - H[l] * P[r - l]) % M`. Put the hash of every window of length `L` in a dict from hash to its first start; when a hash is seen again, **compare the two windows** before saying yes.

## Hint 3

```
lo, hi, best = 1, n - 1, ""
while lo <= hi:
    mid = (lo + hi) // 2
    i = start of a verified repeat of length mid, or -1
    if i != -1: best = s[i:i + mid]; lo = mid + 1
    else: hi = mid - 1
return best
```

Use a big prime modulus such as `2**61 - 1`, so collisions are almost impossible, and verify anyway.
