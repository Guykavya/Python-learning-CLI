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
