def take(iterable, n):
    it = iter(iterable)
    result = []
    for _ in range(n):
        try:
            result.append(next(it))
        except StopIteration:
            break
    return result
