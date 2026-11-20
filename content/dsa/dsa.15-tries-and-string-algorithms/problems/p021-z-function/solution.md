## Approach

Chapter section 12. The Z-box `[l, r)` is the rightmost segment known to equal a prefix of `s`. Inside it, position `i` mirrors position `i - l` of the prefix, so `z[i]` starts at `min(r - i, z[i - l])` for free; only the part beyond `r` needs new comparisons.

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l, r = 0, 0                              # the Z-box is s[l:r]
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])      # reuse the copy inside the box
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1                        # extend with new comparisons
        if i + z[i] > r:
            l, r = i, i + z[i]               # a new rightmost box
    return z
```

Why `min(r - i, ...)`: `z[i - l]` describes the prefix, and the copy of the prefix is only guaranteed up to `r`. Beyond `r` nothing is known yet, so the value is capped there and the `while` loop checks the rest.

## Complexity

Every successful comparison moves `i + z[i]` past the old `r`, so `r` grows by one; `r <= n`, so there are at most `n` successes in total. Each `i` has at most one failing comparison. Total `O(n)` time, `O(n)` memory.

## Another way

From the prefix function: `z` and `pi` carry the same information and each can be converted into the other in `O(n)`. For checking, `os.path.commonprefix([s, s[i:]])` gives `z[i]` directly, in `O(n)` per position: a good slow reference for tests.
