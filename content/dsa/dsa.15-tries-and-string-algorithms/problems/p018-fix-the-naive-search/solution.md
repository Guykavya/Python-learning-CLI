## Approach

**Why it is slow.** On `text = "a" * n` and `pattern = "a" * (m - 1) + "b"`, every one of the `n - m + 1` starts matches `m - 1` letters, then fails on the `b`. The next start re-reads `m - 2` of the letters it just compared. That is about `n * m` comparisons: `10**6 * 10**4 = 10**10` for the test, hours in Python. On ordinary text the same code is fast, because most starts fail after one or two letters: that is why the bug went unnoticed.

**The fix.** KMP (chapter section 11) keeps the number `k` of pattern letters matched right now. On a mismatch it falls back to the longest border of the matched part, `pi[k - 1]`, which is exactly the amount of the pattern that is **still** matched. The text pointer never moves back.

```python
# Why the old version was slow: on text = "aaa...a" and pattern = "aa...ab", every start position
# matches m - 1 letters before failing on the 'b', and the next start re-reads almost the same letters.
# That is (n - m + 1) * m comparisons: O(n * m). KMP keeps what was matched (k) and never re-reads the text.


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


def find_all(text, pattern):
    m = len(pattern)
    pi = prefix_function(pattern)
    found = []
    k = 0
    for i, ch in enumerate(text):
        while k > 0 and ch != pattern[k]:
            k = pi[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:
            found.append(i - m + 1)
            k = pi[k - 1]
    return found
```

## Complexity

`O(n + m)` time, `O(m)` memory.

## Another way

`text.find(pattern, start)` in a loop with `start = i + 1`. CPython's `find` is written in C and, since Python 3.10, uses the "two-way" algorithm for long patterns, so it stays linear on this input too. In a real log tool that is the fix to use; KMP is the fix that does not depend on the library.
