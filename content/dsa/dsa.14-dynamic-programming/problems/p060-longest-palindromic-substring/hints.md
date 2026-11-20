## Hint 1

DP: `is_pal[i][j]` is True when `s[i] == s[j]` and the inside `s[i + 1..j - 1]` is a palindrome (an inside of length 0 or 1 always is). It reads a shorter range, so loop over the **length** first, then the start `i`. Keep `start, best` and update them only when a **strictly** longer palindrome appears: for one length, `i` goes left to right, so the first one found is the leftmost.

## Hint 2

Expand: there are `2n - 1` centres: each letter (odd lengths) and each gap between two letters (even lengths). From a centre `(lo, hi)`, move outwards while `lo >= 0`, `hi < len(s)` and `s[lo] == s[hi]`. When the loop stops, the palindrome is `s[lo + 1:hi]`, of length `hi - lo - 1`.

## Hint 3

```
best = ""
for c in 0..n-1:
    for (lo, hi) in ((c, c), (c, c + 1)):
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            lo -= 1; hi += 1
        if hi - lo - 1 > len(best):
            best = s[lo + 1:hi]
return best
```

Centres are visited from left to right, and two palindromes of the same length with different starts never share a centre, so `>` keeps the leftmost.
