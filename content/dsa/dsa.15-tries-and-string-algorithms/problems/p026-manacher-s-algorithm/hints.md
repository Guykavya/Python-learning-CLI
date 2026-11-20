## Hint 1

Keep the palindrome that reaches furthest right: centre `c`, right edge `r` (it covers `t[2c - r .. r]`). For `i < r`, everything around `i` up to `r` mirrors the area around `2c - i`, so `p[i]` starts at `min(r - i, p[2c - i])`. Then expand with new comparisons; if `i + p[i] > r`, move `(c, r)` to `(i, i + p[i])`.

## Hint 2

`r` only moves right. Every successful comparison moves `i + p[i]` past the old `r`, so there are at most `len(t)` of them in total, plus one failing comparison per `i`.

## Hint 3

A centre `i` with radius `p[i]` has the palindromes of lengths `p[i], p[i] - 2, ...` down to 1 or 2: that is `(p[i] + 1) // 2` palindromes. `count_palindromes(s) = sum((x + 1) // 2 for x in manacher(s))`.

```
t = "#" + "".join(ch + "#" for ch in s)       # length 2n + 1, also for s = ""; p = [0] * len(t); c = r = 0
for i in range(len(t)):
    if i < r: p[i] = min(r - i, p[2 * c - i])
    while 0 <= i - p[i] - 1 and i + p[i] + 1 < len(t) and t[i - p[i] - 1] == t[i + p[i] + 1]: p[i] += 1
    if i + p[i] > r: c, r = i, i + p[i]
```
