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


def repeat_info(s):
    n = len(s)
    p = n - prefix_function(s)[-1]           # the smallest period
    if p < n and n % p == 0:
        return s[:p], n // p
    return s, 1
