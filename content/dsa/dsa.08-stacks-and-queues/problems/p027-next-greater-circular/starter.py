def next_greater_circular(nums):
    n = len(nums)
    ans = [-1] * n
    stack = []
    for i in range(n):          # TODO: one lap is not enough in a circle
        x = nums[i]
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x
        stack.append(i)
    return ans
