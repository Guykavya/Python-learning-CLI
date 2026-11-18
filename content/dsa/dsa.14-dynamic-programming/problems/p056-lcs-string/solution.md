## Approach

Fill the LCS table (p055), then **re-derive the choices** from it (chapter section 9, method 2), walking back from the corner:

- equal last characters: they are matched, so the character belongs to the answer; go diagonally;
- different: `f[i][j]` came from the larger of `f[i-1][j]` and `f[i][j-1]`; move to a neighbour with that same value, so the remaining walk still collects `f[i][j]` characters.

```python
def lcs_string(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    i, j = n, m
    out = []
    while i > 0 and j > 0:                 # walk back from the corner
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])           # a matched character
            i -= 1
            j -= 1
        elif f[i - 1][j] >= f[i][j - 1]:
            i -= 1                         # moving up loses nothing
        else:
            j -= 1                         # moving left loses nothing
    return "".join(reversed(out))
```

Every step either collects a character that sits at index `i-1` of `a` and `j-1` of `b`, with both indices going down, or moves without collecting. So the collected characters (reversed) appear in order in both strings: a common subsequence. And the walk keeps the invariant "characters still to collect = `f[i][j]`", so the total is `f[n][m]`: a longest one.

Tie-breaking (`>=` prefers up) decides **which** LCS you get: for `"ABCBDAB"` and `"BDCABA"` this code returns `BCBA`; preferring left would give another one, equally right.

## Complexity

`O(n * m)` time and space for the table; the walk is `O(n + m)`.

## Another way

Store the strings themselves in the table: `s[i][j]` = one LCS of the prefixes (`s[i-1][j-1] + a[i-1]` or the longer of the two neighbours). It needs no walk back, but copies strings in every cell: `O(n * m * L)` time and memory. For length 400 that is noticeably slower; the walk back is the standard method. With only two rows of the table you cannot walk back (Hirschberg's divide-and-conquer algorithm recovers the string in linear memory, beyond this course).
