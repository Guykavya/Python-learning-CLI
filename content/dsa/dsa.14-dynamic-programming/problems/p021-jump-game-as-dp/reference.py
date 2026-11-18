INF = float("inf")


def min_jumps(nums):
    n = len(nums)
    f = [INF] * n            # f[i] = fewest jumps to arrive at index i
    f[0] = 0
    for i in range(n):
        if f[i] == INF:      # nobody reaches i, so i sends nothing forward
            continue
        for j in range(i + 1, min(n - 1, i + nums[i]) + 1):
            if f[i] + 1 < f[j]:
                f[j] = f[i] + 1
    return f[n - 1] if f[n - 1] != INF else -1
