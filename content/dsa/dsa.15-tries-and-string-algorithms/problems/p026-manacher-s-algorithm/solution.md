## Approach

Chapter section 15. Insert separators so that every palindrome has a single centre in `t` and odd length there (the chapter writes `"#" + "#".join(s) + "#"`, which gives `"##"` for an empty `s`; building `t` as below gives the promised length `2n + 1` in every case); `p[i]` (the radius in `t`) equals the length of the palindrome in `s`.

Keep the rightmost palindrome `(c, r)`. A centre `i < r` lies inside it, so the area around `i` mirrors the area around `2c - i` **as far as `r`**: start at `min(r - i, p[2c - i])` and expand only beyond what is known.

```python
def manacher(s):
    t = "#" + "".join(ch + "#" for ch in s)       # length 2n + 1, also for s = ""
    n = len(t)
    p = [0] * n
    c = r = 0                                    # centre and right edge of the rightmost palindrome
    for i in range(n):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])      # copy from the mirror, capped at the edge
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1                            # expand beyond what is known
        if i + p[i] > r:
            c, r = i, i + p[i]
    return p


def count_palindromes(s):
    return sum((x + 1) // 2 for x in manacher(s))
```

**Why a `#` inside `s` does no harm.** In `t`, separators sit at even indices and characters of `s` at odd ones. The algorithm compares `t[i - k]` with `t[i + k]`, two indices of the **same parity**: separator with separator (always equal) or character with character (the real test). A `#` from `s` is never compared with a separator. This is different from p020, where the prefix function compares positions of any distance and a `#` from `s` could match the separator.

**Counting.** Centre `i` holds the palindromes of lengths `p[i]`, `p[i] - 2`, ... down to 1 or 2 (each is the previous one with its ends removed): `(p[i] + 1) // 2` of them. `aaa`: `p = [0, 1, 2, 3, 2, 1, 0]` gives `0 + 1 + 1 + 2 + 1 + 1 + 0 = 6`.

## Complexity

`r` only moves right; each successful comparison moves `i + p[i]` beyond the old `r`, so there are at most `2n + 1` of them, plus one failing comparison per `i`. `O(n)` time and memory.

## Another way

Two arrays without separators: `d1[i]` (odd palindromes centred at `s[i]`) and `d2[i]` (even ones centred between `s[i - 1]` and `s[i]`), each computed with its own mirror rule. It saves the transformed string but doubles the code; the separator version is the one to remember.
