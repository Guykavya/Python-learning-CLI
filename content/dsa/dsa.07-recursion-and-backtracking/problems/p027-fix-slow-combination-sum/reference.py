def combination_sum(candidates, target, counter):
    candidates = sorted(candidates)
    result, path = [], []

    def go(start, remaining):
        counter.tick()                 # keep this line: the tests count the calls
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                  # sorted: every later candidate is too big as well
            path.append(c)
            go(i, remaining - c)
            path.pop()

    go(0, target)
    return result
