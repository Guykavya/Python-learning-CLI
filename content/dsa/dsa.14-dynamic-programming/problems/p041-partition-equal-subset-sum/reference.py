def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    half = total // 2
    f = [False] * (half + 1)
    f[0] = True                          # the empty subset
    for x in nums:
        for s in range(half, x - 1, -1):     # downwards: each number once
            if f[s - x]:
                f[s] = True
    return f[half]
