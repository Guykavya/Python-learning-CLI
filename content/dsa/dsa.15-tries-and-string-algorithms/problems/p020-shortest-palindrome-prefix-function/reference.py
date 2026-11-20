def prefix_function(seq):
    pi = [0] * len(seq)
    k = 0
    for i in range(1, len(seq)):
        while k > 0 and seq[i] != seq[k]:
            k = pi[k - 1]
        if seq[i] == seq[k]:
            k += 1
        pi[i] = k
    return pi


def shortest_palindrome(s):
    if not s:
        return s
    seq = list(s) + [None] + list(reversed(s))   # None equals no character: a safe separator
    k = prefix_function(seq)[-1]                 # length of the longest palindromic prefix
    return s[k:][::-1] + s
