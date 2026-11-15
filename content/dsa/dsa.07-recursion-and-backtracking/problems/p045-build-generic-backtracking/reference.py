def backtrack(choices, is_valid, is_done):
    result, path = [], []

    def go():
        if is_done(path):
            result.append(path[:])
        for option in choices(path):
            if not is_valid(path, option):
                continue
            path.append(option)
            go()
            path.pop()

    go()
    return result


def subsets(nums):
    n = len(nums)

    def choices(path):
        last = path[-1] if path else -1
        return range(last + 1, n)

    found = backtrack(choices, lambda path, i: True, lambda path: True)
    return [[nums[i] for i in idx] for idx in found]


def permutations(nums):
    n = len(nums)
    found = backtrack(lambda path: range(n) if len(path) < n else [],
                      lambda path, i: i not in path,
                      lambda path: len(path) == n)
    return [[nums[i] for i in idx] for idx in found]
