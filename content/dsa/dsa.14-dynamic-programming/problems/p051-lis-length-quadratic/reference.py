def lis_length(nums):
    n = len(nums)
    if n == 0:
        return 0
    f = [1] * n                          # f[i]: longest increasing subsequence ending at i
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and f[j] + 1 > f[i]:
                f[i] = f[j] + 1
    return max(f)
