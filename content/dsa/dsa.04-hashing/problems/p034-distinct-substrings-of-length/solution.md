## Approach

Hash every window of length `L` with a rolling update and count how many **different hashes** occur. With `M = 2^61 - 1` and a
fixed base, the chance that two different windows collide is about `1 / 2.3 * 10^18` per pair, so for these inputs counting
hashes equals counting substrings.

## Code

```python
B = 911382323
M = (1 << 61) - 1

s = input().strip()
L = int(input())
n = len(s)

h = 0
for i in range(L):
    h = (h * B + ord(s[i]) - 96) % M
top = pow(B, L - 1, M)

hashes = {h}
for i in range(L, n):
    h = ((h - (ord(s[i - L]) - 96) * top) * B + ord(s[i]) - 96) % M
    hashes.add(h)

print(len(hashes))
```

## Complexity

O(n) time, O(n) memory (one integer per window). The slice-set version is O(n * L).

## Another way

For short `L` a set of slices is simpler and exact. For large `L` use the rolling hash, or a **suffix automaton** or suffix
array (later modules) which count distinct substrings exactly and without any collision risk.
