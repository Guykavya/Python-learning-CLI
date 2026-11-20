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


def count_distinct(s):
    total = 0
    for length in range(1, len(s) + 1):
        v = s[:length][::-1]                     # the suffixes of s[:length] become prefixes of v
        z = z_function(v)
        seen = max(z[1:], default=0)             # the longest suffix that occurred earlier
        total += length - seen                   # the longer suffixes are new
    return total
