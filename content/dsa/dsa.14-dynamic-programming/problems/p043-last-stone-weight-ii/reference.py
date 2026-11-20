def last_stone_weight_ii(stones):
    total = sum(stones)
    half = total // 2
    f = [False] * (half + 1)
    f[0] = True
    for x in stones:
        for s in range(half, x - 1, -1):     # downwards: each stone once
            if f[s - x]:
                f[s] = True
    for s in range(half, -1, -1):            # largest reachable sum <= half
        if f[s]:
            return total - 2 * s
    return total                             # never reached: f[0] is True
