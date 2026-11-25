import math


def p_exactly_k_heads(n, k):
    if k < 0 or k > n:
        return 0.0
    return math.comb(n, k) / 2 ** n
