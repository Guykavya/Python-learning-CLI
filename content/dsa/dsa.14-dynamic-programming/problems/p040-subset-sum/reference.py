def subset_sum(nums, target):
    f = [False] * (target + 1)
    f[0] = True                              # the empty subset
    for x in nums:
        for s in range(target, x - 1, -1):   # downwards: each number once
            if f[s - x]:
                f[s] = True
    return f[target]


def subset_sum_bits(nums, target):
    bits = 1                                 # bit s set = sum s reachable; only 0 at first
    mask = (1 << (target + 1)) - 1           # sums above target are never needed
    for x in nums:
        bits = (bits | (bits << x)) & mask
    return (bits >> target) & 1 == 1
