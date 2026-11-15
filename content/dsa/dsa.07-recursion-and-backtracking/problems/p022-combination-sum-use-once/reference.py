def combination_sum2(candidates, target):
    candidates = sorted(candidates)
    result, path = [], []

    def go(start, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break
            if i > start and c == candidates[i - 1]:
                continue
            path.append(c)
            go(i + 1, remaining - c)
            path.pop()

    go(0, target)
    return result
