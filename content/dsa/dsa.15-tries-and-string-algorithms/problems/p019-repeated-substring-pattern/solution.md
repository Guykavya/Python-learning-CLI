## Approach

Chapter section 11. A string is a block repeated exactly when its smallest period `p = n - pi[n - 1]` is smaller than `n` **and divides** `n`. Then the block is `s[:p]` and it repeats `n // p` times.

```python
def prefix_function(s):
    pi = [0] * len(s)
    k = 0
    for i in range(1, len(s)):
        while k > 0 and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi


def repeat_info(s):
    n = len(s)
    p = n - prefix_function(s)[-1]           # the smallest period
    if p < n and n % p == 0:
        return s[:p], n // p
    return s, 1
```

**Why only the smallest period needs checking.** If `s` were a block of length `q` repeated (`q` divides `n`, `q < n`), then `q` is a period. The smallest period `p` and `q` are both periods with `p + q <= n` (since `q <= n / 2`), so by the Fine and Wilf lemma `gcd(p, q)` is a period too; it is at most `p`, so it equals `p`, and `p` divides `q`, which divides `n`. So if the smallest period does not divide `n`, no repetition exists.

`abcab`: `pi[-1] = 2`, `p = 3`, and 3 does not divide 5: `('abcab', 1)`.

## Complexity

`O(n)` time and memory.

## Another way

The one-liner from the chapter: `s` is a repeated block exactly when `s in (s + s)[1:-1]`; then `(s + s).find(s, 1)` is the block length. `str.find` is linear in practice, so this is also a good Python answer:

```python
def repeat_info(s):
    p = (s + s).find(s, 1)
    return (s[:p], len(s) // p) if p < len(s) else (s, 1)
```
