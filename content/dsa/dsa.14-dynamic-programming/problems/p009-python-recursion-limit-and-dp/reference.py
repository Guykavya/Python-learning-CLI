def min_steps(n):
    f = [0] * (n + 1)                  # f[1] = 0: already at 1
    for i in range(2, n + 1):
        best = f[i - 1] + 1
        if i % 2 == 0 and f[i // 2] + 1 < best:
            best = f[i // 2] + 1
        if i % 3 == 0 and f[i // 3] + 1 < best:
            best = f[i // 3] + 1
        f[i] = best
    return f[n]
