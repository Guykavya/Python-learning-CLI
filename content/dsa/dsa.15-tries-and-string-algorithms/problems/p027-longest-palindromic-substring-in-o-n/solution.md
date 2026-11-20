## Approach

One Manacher array answers both questions (chapter section 15, "Reading the answers from p" and "Is this substring a palindrome?").

- **Longest:** the largest `p[i]` is the length; the palindrome starts at `(i - p[i]) // 2` in `s`. Scanning left to right and updating only on a strictly larger value keeps the leftmost.
- **Queries:** `s[l:r]` spans `t[2l + 1 .. 2r - 1]`, whose middle is `l + r`. A palindrome centred there of length `p[l + r]` contains every shorter one with the same centre, so `s[l:r]` is a palindrome exactly when `p[l + r] >= r - l`.

```python
def manacher(s):
    t = "#" + "".join(ch + "#" for ch in s)       # length 2n + 1, also for s = ""
    n = len(t)
    p = [0] * n
    c = r = 0
    for i in range(n):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
        if i + p[i] > r:
            c, r = i, i + p[i]
    return p


def longest_palindrome(s):
    p = manacher(s)
    best = 0
    for i in range(len(p)):
        if p[i] > p[best]:                       # strictly larger: keeps the leftmost
            best = i
    start = (best - p[best]) // 2
    return s[start:start + p[best]]


def palindrome_queries(s, queries):
    p = manacher(s)
    return [p[l + r] >= r - l for l, r in queries]   # the centre of s[l:r] is l + r in t
```

Example: `s = "abacdcaba"`, query `(1, 4)` is `bac`. Its centre is index `1 + 4 = 5` of `t`, which is the letter `s[2] = a`. Around that `a` the neighbours are `b` and `c`, so `p[5] = 1`, and `1 < 4 - 1 = 3`: not a palindrome. Query `(3, 6)` is `cdc`: centre 9 (the `d`), where the longest palindrome is the whole string `abacdcaba`, so `p[9] = 9`, and `9 >= 3`: a palindrome.

## Complexity

`O(n)` preparation, `O(1)` per query: `O(n + q)` in total, `O(n)` memory.

## Another way

Hashes of `s` and of `reversed(s)` (chapter section 14): `s[l:r]` is a palindrome when its hash equals the hash of the matching window of the reversed string. Also `O(1)` per query, but with a collision risk, and finding the longest palindrome needs a binary search per centre.
