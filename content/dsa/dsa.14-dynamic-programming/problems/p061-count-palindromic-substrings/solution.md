## Approach

Expand around every centre. There are `n` letter centres (odd lengths) and `n - 1` gap centres (even lengths). From a centre, the palindromes with that centre are nested: if `s[lo..hi]` is a palindrome, so is `s[lo+1..hi-1]`. So expanding stops at the first mismatch, and every successful step before it is exactly one palindrome.

```python
def count_palindromes(s):
    total = 0
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):     # odd, even
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                total += 1
                lo -= 1
                hi += 1
    return total
```

For `"abba"`: the four letter centres give 1 each; the gap between the two `b`s gives `"bb"` and then `"abba"`; the other two gaps fail at once. Total `4 + 2 = 6`.

## Complexity

`O(n^2)` time in the worst case (`"aaaa..."`, where every expansion runs to an end), `O(1)` extra memory.

## Another way

The DP table of section 16. `is_pal[i][j]` depends on `is_pal[i + 1][j - 1]`, so fill `i` downwards and `j` upwards, and count:

```python
def count_palindromes(s):
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]
    total = 0
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
                total += 1
    return total
```

Same `O(n^2)` time, but `O(n^2)` memory. The table is worth it when you need the answers again, for example for the minimum palindrome cuts of section 16.
