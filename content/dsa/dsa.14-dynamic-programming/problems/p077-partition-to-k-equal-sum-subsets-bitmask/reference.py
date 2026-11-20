def can_split(nums, k):
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    if max(nums) > target:
        return False
    n = len(nums)
    fill = [-1] * (1 << n)          # fill[mask]: how full the current group is; -1 = unreachable
    fill[0] = 0
    for mask in range(1 << n):
        here = fill[mask]
        if here == -1:
            continue
        for i in range(n):
            if not mask >> i & 1 and here + nums[i] <= target:
                fill[mask | (1 << i)] = (here + nums[i]) % target
    return fill[(1 << n) - 1] == 0
