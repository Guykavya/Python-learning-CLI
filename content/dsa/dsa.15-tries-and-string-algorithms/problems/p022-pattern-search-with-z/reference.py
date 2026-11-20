def z_function(s):
    n = len(s)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def match_lengths(text, pattern):
    m = len(pattern)
    z = z_function(pattern + text)               # no separator: the cap below is enough
    return [min(z[m + i], m) for i in range(len(text))]


def z_search(text, pattern):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    return [i for i, length in enumerate(match_lengths(text, pattern)) if length == m]
