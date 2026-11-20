def target_sum(nums, target):
    total = sum(nums)
    if abs(target) > total or (total + target) % 2:
        return 0
    plus = (total + target) // 2         # sum of the numbers marked '+'
    f = [0] * (plus + 1)
    f[0] = 1
    for x in nums:
        for s in range(plus, x - 1, -1):     # downwards: each number once
            f[s] += f[s - x]
    return f[plus]
