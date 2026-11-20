## Approach

Chapter section 11. The prefix function of the pattern tells, after a mismatch, how much of the pattern is **still** matched. So the text is read once, left to right, never backwards.

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


def kmp_search(text, pattern):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))      # "" occurs at every position
    pi = prefix_function(pattern)
    found = []
    k = 0                                      # pattern letters matched right now
    for i, ch in enumerate(text):
        while k > 0 and ch != pattern[k]:
            k = pi[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:
            found.append(i - m + 1)
            k = pi[k - 1]                      # keep the border: overlaps are found too
    return found
```

After a full match, `k = pi[m - 1]` does two things: it keeps the longest border of the pattern as "already matched" (so `aa` in `aaaaa` is found at 0, 1, 2, 3), and it makes sure `pattern[k]` is a valid index on the next letter.

## Complexity

`O(m)` for `pi` and `O(n)` for the scan: `k` rises at most once per text letter, so fallbacks total at most `n`. Memory `O(m)`.

## Another way

`str.find` in a loop with `start = i + 1` (not `i + len(pattern)`) lists overlapping matches too, and CPython's search is linear in the worst case for long patterns since Python 3.10. For a plain search in Python, that is the practical tool (chapter section 16). KMP earns its place for streams (the state is one integer) and for the questions about borders and periods.
