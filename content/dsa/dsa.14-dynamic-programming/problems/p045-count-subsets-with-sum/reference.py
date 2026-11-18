def count_subsets(nums, target):
    f = [0] * (target + 1)
    f[0] = 1                             # the empty subset
    for x in nums:
        for s in range(target, x - 1, -1):   # downwards: each number once
            f[s] += f[s - x]
    return f[target]
