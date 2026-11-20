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
