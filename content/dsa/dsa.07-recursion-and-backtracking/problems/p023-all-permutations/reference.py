def permute(nums):
    result, path = [], []
    used = [False] * len(nums)

    def go():
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            go()
            path.pop()
            used[i] = False

    go()
    return result
