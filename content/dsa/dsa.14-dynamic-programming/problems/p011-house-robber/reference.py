def rob(nums):
    prev2, prev1 = 0, 0          # f(i-2), f(i-1)
    for money in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1
