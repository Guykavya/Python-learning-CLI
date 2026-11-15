def iter_subsets(items):
    path = []

    def go(start):
        yield path[:]
        for i in range(start, len(items)):
            path.append(items[i])
            yield from go(i + 1)
            path.pop()

    yield from go(0)
