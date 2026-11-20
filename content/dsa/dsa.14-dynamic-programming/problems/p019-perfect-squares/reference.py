INF = float("inf")


def num_squares(n):
    squares = []
    k = 1
    while k * k <= n:
        squares.append(k * k)
        k += 1
    f = [INF] * (n + 1)
    f[0] = 0                                   # zero squares make 0
    for a in range(1, n + 1):
        for s in squares:
            if s > a:
                break                          # squares are increasing
            if f[a - s] + 1 < f[a]:
                f[a] = f[a - s] + 1
    return f[n]
