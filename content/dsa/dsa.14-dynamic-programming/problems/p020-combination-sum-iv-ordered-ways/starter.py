def ordered_ways(nums, target):
    """Number of sequences (order matters) of numbers from nums that sum to exactly target."""
    f = [0] * (target + 1)
    f[0] = 1
    for x in nums:
        for a in range(x, target + 1):
            f[a] += f[a - x]
    return f[target]
