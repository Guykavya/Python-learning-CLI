## Hint 1

Keep `k`, the length of the border of `s[:i]`. The border `s[:k]` can be extended by the letter `s[i]` exactly when `s[i] == s[k]`; then the new border has length `k + 1`.

## Hint 2

If `s[i] != s[k]`, every shorter candidate is a border of `s[:k]` as well (it ends where the old border ends). The longest of those is `pi[k - 1]`. Try `k = pi[k - 1]`, and repeat while `k > 0` and the letters differ.

## Hint 3

```
pi = [0] * n; k = 0
for i in 1..n-1:
    while k > 0 and s[i] != s[k]: k = pi[k - 1]
    if s[i] == s[k]: k += 1
    pi[i] = k
```
