## Approach

Chapter section 10. Use the previous answer to get the next one. With `k = pi[i - 1]`:

- if `s[i] == s[k]`, the border `s[:k]` extends by one letter: `pi[i] = k + 1`;
- otherwise fall back to the longest border of the border, `k = pi[k - 1]`, and test again, until a letter matches or `k = 0`.

```python
def prefix_function(s):
    n = len(s)
    pi = [0] * n
    k = 0                                    # length of the current border
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = pi[k - 1]                    # fall back to a shorter border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi
```

**Why `pi[k - 1]` and not `k - 1`.** The next candidate must still be a suffix of `s[:i]`. Every border of `s[:i]` that is shorter than `k` is a suffix of the border `s[:k]` and a prefix of it, so it is a border **of `s[:k]`**. The longest one is `pi[k - 1]`. Trying `k - 1` would test strings that may not end at position `i - 1` at all.

## Complexity

`O(n)` time, amortised: `k` grows by at most 1 per `i`, and every fallback makes it strictly smaller, so there are at most `n` fallbacks in total. `O(n)` memory for `pi`.

## Another way

From the Z-function (p021): every `i` with `z[i] > 0` gives a border of length `z[i]` ending at `i + z[i] - 1`, so `pi[i + z[i] - 1] = max(..., z[i])`, and then fill the gaps backwards with `pi[j] = max(pi[j], pi[j + 1] - 1)`. It is also `O(n)`, but harder to get right than the direct method.
