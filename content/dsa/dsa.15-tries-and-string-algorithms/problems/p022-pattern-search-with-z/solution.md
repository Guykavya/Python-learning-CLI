## Approach

Chapter section 12 uses `pattern + "#" + text`. The separator only makes sure that no value is larger than `m`; capping with `min(z, m)` does the same job and works for any characters.

Let `u = pattern + text`. For a text position `i`, `z[m + i]` is the common prefix of `u` and `text[i:]`.

- Its first `min(z[m + i], m)` characters compare `text[i:]` with `u[:m]`, which is the pattern: that is exactly the answer.
- Anything beyond `m` compares the text with the **text** (the part of `u` after the pattern). It is a real equality, just not one we need, so we cut it off.
- A match never runs past the end of `u`, and `u[m + i:]` is entirely text, so it can never "borrow" pattern characters.

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


def match_lengths(text, pattern):
    m = len(pattern)
    z = z_function(pattern + text)               # no separator: the cap below is enough
    return [min(z[m + i], m) for i in range(len(text))]


def z_search(text, pattern):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    return [i for i, length in enumerate(match_lengths(text, pattern)) if length == m]
```

`match_lengths("abaab", "aba")`: `u = "abaabaab"`, `z = [8, 0, 1, 5, 0, 1, 2, 0]`; the text part `[5, 0, 1, 2, 0]` capped at 3 gives `[3, 0, 1, 2, 0]`. The 5 at text position 0 says "`abaab` matches `abaab...`": true, but only 3 of it is pattern.

## Complexity

`O(n + m)` time and memory.

## Another way

Compute `z` of the pattern only, then run a Z-box over the text that compares against the pattern (the "Z-algorithm with an external text"): it never builds `pattern + text`, so it uses only `O(m)` extra memory besides the output. Or use KMP (p015) for the positions: the prefix function's state `k` after reading `text[i]` is the longest prefix of the pattern that **ends** at `i`, not one that **starts** there, so `match_lengths` is the Z-function's own question.
