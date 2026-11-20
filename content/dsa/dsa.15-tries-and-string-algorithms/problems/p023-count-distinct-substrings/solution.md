## Approach

Grow the string one character at a time and count only the substrings that appear for the first time.

When `c` is appended to `t`, giving `u` of length `L`, every new substring ends with that `c`, so it is a **suffix** of `u`. If a suffix of length `k` already occurred earlier in `u`, so did every shorter suffix (they are suffixes of that earlier occurrence). So the new substrings are exactly the suffixes longer than `k_max`, the longest suffix that occurred earlier: `L - k_max` of them.

To find `k_max`, reverse `u`: suffixes become prefixes, and "occurred earlier" becomes "occurs again at a later position". That is the Z-function: `k_max = max(z[1:])` of `reversed(u)`.

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def count_distinct(s):
    total = 0
    for length in range(1, len(s) + 1):
        v = s[:length][::-1]                     # the suffixes of s[:length] become prefixes of v
        z = z_function(v)
        seen = max(z[1:], default=0)             # the longest suffix that occurred earlier
        total += length - seen                   # the longer suffixes are new
    return total
```

`aba`: `a` adds 1 (`a`); `ab` adds 2 (`b`, `ab`); `aba` adds `3 - 1 = 2` (the suffix `a` occurred before; `ba` and `aba` are new). Total 5.

## Complexity

`n` Z-functions of length up to `n`: `O(n**2)` time, about 2 million steps for `n = 2000`. Memory `O(n)` at any moment.

## Another way

- **A trie of all suffixes:** insert `s[i:]` for every `i`; every trie node except the root is one distinct substring. Simple, but it makes up to `n(n + 1)/2` nodes: 2 million Python objects for `n = 2000`, hundreds of megabytes.
- **Hashing:** for each length, put the prefix hashes of all windows (p025's `StringHash`) into a set and count them. `O(n**2)` time with `O(n)` memory per length, but with a small collision risk unless you double-hash.
- **Suffix array or suffix automaton:** `O(n log n)` or `O(n)`, the tools for strings of millions of characters, beyond this module.
