def combination_sum(candidates, target, counter):
    result, path = [], []

    def go(start, remaining):
        counter.tick()                 # keep this line: the tests count the calls
        if remaining < 0:
            return
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            path.append(candidates[i])
            go(i, remaining - candidates[i])
            path.pop()

    go(0, target)
    return result
