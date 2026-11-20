def ordered_ways(nums, target):
    f = [0] * (target + 1)
    f[0] = 1                         # the empty sequence
    for a in range(1, target + 1):   # outer loop: amounts
        for x in nums:               # inner loop: the last number of the sequence
            if x <= a:
                f[a] += f[a - x]
    return f[target]
