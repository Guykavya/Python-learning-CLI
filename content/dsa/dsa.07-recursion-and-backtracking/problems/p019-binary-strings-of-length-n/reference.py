def binary_strings(n):
    result = []
    path = []

    def go():
        if len(path) == n:
            result.append("".join(path))
            return
        for ch in "01":
            path.append(ch)
            go()
            path.pop()

    go()
    return result
