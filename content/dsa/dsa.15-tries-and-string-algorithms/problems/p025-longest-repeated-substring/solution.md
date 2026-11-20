## Approach

Chapter section 14. Two facts:

1. **Monotone:** a repeat of length `L` contains a repeat of length `L - 1`, so binary search on `L` works.
2. **One length in `O(n)`:** with prefix hashes, every window's hash costs `O(1)`; a dict finds two equal hashes. A hash match is verified by comparing the two windows, so the answer is always a real repeat.

```python
class StringHash:
    def __init__(self, s, B=131, M=(1 << 61) - 1):
        self.M = M
        self.H = [0] * (len(s) + 1)
        self.P = [1] * (len(s) + 1)
        for i, ch in enumerate(s):
            self.H[i + 1] = (self.H[i] * B + ord(ch)) % M
            self.P[i + 1] = (self.P[i] * B) % M

    def get(self, l, r):
        """Hash of s[l:r]."""
        return (self.H[r] - self.H[l] * self.P[r - l]) % self.M


def has_repeat(s, length, sh):
    """Start of a window of this length that occurred earlier, or -1."""
    seen = {}
    for i in range(len(s) - length + 1):
        h = sh.get(i, i + length)
        if h in seen:
            j = seen[h]
            if s[j:j + length] == s[i:i + length]:     # verify: never trust a hash alone
                return i
        else:
            seen[h] = i
    return -1


def longest_repeat(s):
    sh = StringHash(s)
    lo, hi, best = 1, len(s) - 1, ""
    while lo <= hi:
        mid = (lo + hi) // 2
        i = has_repeat(s, mid, sh)
        if i != -1:
            best = s[i:i + mid]
            lo = mid + 1                               # try longer
        else:
            hi = mid - 1                               # too long
    return best
```

A collision that is not verified only makes `has_repeat` say "no" for that pair (the first window stays in `seen`); with `M = 2**61 - 1` that is practically impossible, and it can never produce a wrong answer string.

## Complexity

`O(n)` to build the hashes; each test is `O(n)` hashes plus a verification on a real match (`O(L)`); `O(log n)` tests. Total `O(n log n)` expected time, `O(n)` memory.

## Another way

A **suffix array** with the LCP array: the answer is the maximum LCP of two neighbouring suffixes in sorted order. `O(n log n)` and deterministic, but much more code. For short strings, sort all suffixes with `sorted(range(n), key=lambda i: s[i:])` and compare neighbours with `os.path.commonprefix`: very short, but `O(n**2)` memory and time in the worst case (`aaaa...`).
