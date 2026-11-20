def rod_cut(price, n):
    f = [0] * (n + 1)                    # f[m] = best money for a rod of length m
    for m in range(1, n + 1):
        for k in range(1, m + 1):        # length of the first piece
            f[m] = max(f[m], price[k - 1] + f[m - k])
    return f[n]
