## Approach

Two steps: fill the interval table of chapter section 17, then walk it back (chapter section 9, "Method 2: re-derive the choice from the table").

**The table.** `f[i][j]` = the length of the longest palindromic subsequence of `s[i..j]`.

- If `s[i] == s[j]`: `f[i][j] = f[i + 1][j - 1] + 2`. Using both ends is always safe: take any best palindrome inside, and wrapping it in the two equal letters makes it 2 longer.
- Otherwise the two ends cannot both be in it: `f[i][j] = max(f[i + 1][j], f[i][j - 1])`.
- `f[i][i] = 1`; an empty inside counts 0. Fill by length.

**The walk.** From `(0, n - 1)`: when the ends match, both letters are part of the answer (one goes to the front, one to the back); when they differ, follow the larger neighbour, which is where the value came from; when `i == j`, one letter sits in the middle.

```python
def longest_pal_subseq(s):
    n = len(s)
    if n == 0:
        return ""
    f = [[0] * n for _ in range(n)]          # f[i][j] = LPS length inside s[i..j]
    for i in range(n):
        f[i][i] = 1
    for length in range(2, n + 1):           # short ranges first
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                f[i][j] = (f[i + 1][j - 1] if length > 2 else 0) + 2
            else:
                f[i][j] = max(f[i + 1][j], f[i][j - 1])

    left, right, middle = [], [], ""
    i, j = 0, n - 1
    while i <= j:
        if i == j:                           # one letter in the middle
            middle = s[i]
            break
        if s[i] == s[j]:                     # both ends belong to the palindrome
            left.append(s[i])
            right.append(s[j])
            i += 1
            j -= 1
        elif f[i + 1][j] >= f[i][j - 1]:     # drop the left end
            i += 1
        else:                                # drop the right end
            j -= 1
    return "".join(left) + middle + "".join(reversed(right))
```

For `"character"`: `c` and `r` differ, and the walk drops the `r` at the end. Then `c...e` differ, so the `e` is dropped, and `c...t` differ, so the `t` is dropped. Now `c` and `c` match, then `h` and `a` differ (drop `h`), and `a` and `a` match. That leaves `r` alone in the middle: `"car" + "ac"` = `"carac"`.

## Complexity

`O(n**2)` time and memory for the table; the walk is `O(n)`. With `n = 1000` the table has a million cells.

## Another way

The longest palindromic subsequence of `s` is the longest common subsequence of `s` and `s[::-1]` (chapter section 17). So the LCS string of p056, applied to `s` and its reverse, gives a palindrome of the right length. Careful: an arbitrary LCS of the two is not always a palindrome itself when there are several. The standard fix is to rebuild from the LCS table and mirror its first half, which is more fiddly than the walk above.
