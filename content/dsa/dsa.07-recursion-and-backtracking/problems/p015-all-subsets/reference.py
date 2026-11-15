def subsets(nums):
    result = []
    path = []

    def go(start):
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return result
