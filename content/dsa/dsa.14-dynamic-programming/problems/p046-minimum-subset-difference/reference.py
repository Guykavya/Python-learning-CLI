def split_evenly(nums):
    n = len(nums)
    total = sum(nums)
    half = total // 2
    f = [[False] * (half + 1) for _ in range(n + 1)]   # f[i][s]: first i parcels can make s
    f[0][0] = True
    for i in range(1, n + 1):
        w = nums[i - 1]
        prev, row = f[i - 1], f[i]
        for s in range(half + 1):
            row[s] = prev[s] or (s >= w and prev[s - w])
    best = half
    while not f[n][best]:
        best -= 1
    group = []
    s = best
    for i in range(n, 0, -1):          # walk back: was parcel i-1 needed?
        if not f[i - 1][s]:
            group.append(i - 1)
            s -= nums[i - 1]
    group.reverse()
    return total - 2 * best, group
