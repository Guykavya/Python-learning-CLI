## Hint 1

On `text = "a" * n` and `pattern = "a" * (m - 1) + "b"`, every start matches `m - 1` letters, then fails on the `b`. The next start re-reads `m - 2` of those same letters. That is `(n - m + 1) * m` comparisons: `10**10` for the test.

## Hint 2

After matching `m - 1` letters and failing, the last `m - 2` text letters are already known to be `a`s. KMP keeps that knowledge as the number `k` and falls back to the longest border (`pi[k - 1]`) instead of restarting. Build `pi` for the pattern (p014), then scan the text once.

## Hint 3

```
pi = prefix_function(pattern); k = 0; found = []
for i, ch in enumerate(text):
    while k > 0 and ch != pattern[k]: k = pi[k - 1]
    if ch == pattern[k]: k += 1
    if k == m: found.append(i - m + 1); k = pi[k - 1]
return found
```
