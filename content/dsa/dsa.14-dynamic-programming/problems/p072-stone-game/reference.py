def stone_game(piles):
    n = len(piles)
    if n == 0:
        return 0
    f = [[0] * n for _ in range(n)]
    for i in range(n):
        f[i][i] = piles[i]                      # one pile left: take it
    for length in range(2, n + 1):              # short rows of piles first
        for i in range(n - length + 1):
            j = i + length - 1
            f[i][j] = max(piles[i] - f[i + 1][j],    # take the left pile
                          piles[j] - f[i][j - 1])    # take the right pile
    return f[0][n - 1]
