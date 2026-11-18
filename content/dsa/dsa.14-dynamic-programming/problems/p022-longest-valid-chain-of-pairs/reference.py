def longest_chain(pairs):
    pairs = sorted(pairs)                 # by first value: a predecessor always comes earlier
    n = len(pairs)
    f = [1] * n                           # f[i] = longest chain that ENDS with pairs[i]
    for i in range(n):
        for j in range(i):
            if pairs[j][1] < pairs[i][0] and f[j] + 1 > f[i]:
                f[i] = f[j] + 1
    return max(f) if f else 0
