## Hint 1

Compute the prefix function of the **pattern** (p014). Then scan the text with one number `k`: how many pattern letters are matched right now. For each text letter, fall back with `k = pi[k - 1]` while `k > 0` and the letter differs from `pattern[k]`; then, if it equals `pattern[k]`, `k += 1`.

## Hint 2

When `k` reaches `m`, the match started at `i - m + 1`. Record it, then set `k = pi[m - 1]`: the longest border of the pattern is still matched, which is exactly what overlapping matches need.

## Hint 3

```
if pattern == "": return list(range(len(text) + 1))
pi = prefix_function(pattern); k = 0; found = []
for i, ch in enumerate(text):
    while k > 0 and ch != pattern[k]: k = pi[k - 1]
    if ch == pattern[k]: k += 1
    if k == m: found.append(i - m + 1); k = pi[k - 1]
return found
```
