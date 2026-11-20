## Approach

Chapter section 13. A window's fingerprint is its polynomial hash. Sliding the window one step removes the front letter's term (`ord(front) * B**(m-1)`), multiplies the rest by `B`, and adds the new letter: `O(1)` per step.

```python
def window_hashes(text, m, B, M):
    n = len(text)
    if m > n:
        return []
    top = pow(B, m - 1, M)                       # B**(m-1) mod M, computed once
    h = 0
    for ch in text[:m]:
        h = (h * B + ord(ch)) % M
    out = [h]
    for i in range(n - m):
        h = ((h - ord(text[i]) * top) * B + ord(text[i + m])) % M    # drop text[i], add text[i+m]
        out.append(h)
    return out


def string_hash(s, B, M):
    h = 0
    for ch in s:
        h = (h * B + ord(ch)) % M
    return h


def rabin_karp(text, pattern, params=((131, 1_000_000_007), (137, 998_244_353)), verify=True):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    if m > len(text):
        return []
    lists = [window_hashes(text, m, B, M) for B, M in params]
    wanted = [string_hash(pattern, B, M) for B, M in params]
    found = []
    for i in range(len(text) - m + 1):
        if all(hs[i] == w for hs, w in zip(lists, wanted)):
            if not verify or text[i:i + m] == pattern:
                found.append(i)
    return found
```

**The crafted pair.** For `(31, 101)`, `die` and `cab` both hash to 72, so a trusting search reports position 2. For `(37, 103)` they hash to 85 and 65: requiring both pairs to agree removes the false alarm. Equal strings have equal hashes for **every** pair, so extra pairs can never remove a real match; they only make false alarms rarer (about `1 / (M1 * M2)` per window).

## Complexity

`O(n + m)` per pair, plus `O(m)` per verified candidate. With verification, the worst case is `O(n * m)` when the pattern really occurs at almost every position (`aaaa...` / `aaa`), because each real match is compared; chapter section 13 discusses why that is the size of the answer, not a flaw of hashing.

## Another way

Prefix hashes (chapter section 14): `H[i]` = hash of `text[:i]`, then `hash(text[l:r]) = (H[r] - H[l] * P[r - l]) % M`. They give any substring's hash in `O(1)`, not only fixed-length windows. For a plain search in Python, `str.find` in a loop is simpler and faster; Rabin-Karp shines for **many patterns of the same length** (one pass, a set of pattern hashes).
