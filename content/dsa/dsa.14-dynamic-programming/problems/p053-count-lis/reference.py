def count_lis(nums):
    n = len(nums)
    if n == 0:
        return 0
    f = [1] * n                          # f[i]: LIS length ending at i
    c = [1] * n                          # c[i]: how many of that length end at i
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if f[j] + 1 > f[i]:
                    f[i] = f[j] + 1
                    c[i] = c[j]          # a longer length: forget the old count
                elif f[j] + 1 == f[i]:
                    c[i] += c[j]         # same length: more ways
    best = max(f)
    total = 0
    for i in range(n):
        if f[i] == best:
            total += c[i]
    return total
