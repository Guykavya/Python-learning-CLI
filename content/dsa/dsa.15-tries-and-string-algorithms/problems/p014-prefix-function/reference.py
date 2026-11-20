def prefix_function(s):
    n = len(s)
    pi = [0] * n
    k = 0                                    # length of the current border
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = pi[k - 1]                    # fall back to a shorter border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi
