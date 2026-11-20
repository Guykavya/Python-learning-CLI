## Approach

Chapter section 16 shows both methods. They answer the same question from two sides.

**DP.** `is_pal[i][j]` = `s[i..j]` is a palindrome. It is True when the ends match and the inside is a palindrome. The inside is shorter, so the table is filled by **length**, not by row.

```python
def longest_pal_dp(s):
    n = len(s)
    if n == 0:
        return ""
    is_pal = [[False] * n for _ in range(n)]
    start, best = 0, 1
    for i in range(n):
        is_pal[i][i] = True                       # length 1
    for length in range(2, n + 1):                # shorter substrings first
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
                if length > best:                 # strictly longer: keeps the leftmost
                    start, best = i, length
    return s[start:start + best]
```

**Expand around the centre.** Every palindrome is symmetric around a centre: a letter (odd length) or the gap between two letters (even length). There are `2n - 1` centres. Grow each one outward while the ends match.

```python
def longest_pal_expand(s):
    best = ""
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):    # odd, even length
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1
                hi += 1
            if hi - lo - 1 > len(best):
                best = s[lo + 1:hi]
    return best
```

**The tie rule.** In the DP, one length is scanned with `i` going left to right, and `best` changes only on a strictly longer length, so the leftmost of the longest is kept. In the expansion, centres go left to right; two palindromes of the same length with different starts have different centres, and the one starting first has the earlier centre. So `>` (not `>=`) keeps the leftmost in both.

| | DP table | Expand around centre |
|---|---|---|
| time, worst case | `O(n**2)` always | `O(n**2)` (string of one repeated letter) |
| time, random text | `O(n**2)` always | about `O(n)`: most centres stop after a step or two |
| memory | `O(n**2)` | `O(1)` |

## Complexity

Both are `O(n**2)` in the worst case. The table always does `n**2 / 2` steps and holds `n**2` booleans (9 million for `n = 3000`). Expansion does work only where palindromes are, so on ordinary text it is far faster.

## Another way

Manacher's algorithm finds the longest palindromic substring in `O(n)` by reusing the expansion of a mirrored centre. It is a classic string algorithm (dsa.15 territory) and rarely needed: expansion is fast enough for `n` in the thousands.
