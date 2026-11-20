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


def all_periods(s):
    n = len(s)
    pi = prefix_function(s)
    periods = []
    b = pi[-1]                       # the longest border
    while b > 0:
        periods.append(n - b)        # a border of length b gives the period n - b
        b = pi[b - 1]                # the next shorter border
    periods.append(n)                # the empty border: period n
    return periods


def smallest_period(s):
    return len(s) - prefix_function(s)[-1]
