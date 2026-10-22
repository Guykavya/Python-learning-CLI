def for_each(iterable, action):
    it = iter(iterable)
    count = 0
    while True:
        try:
            item = next(it)
        except StopIteration:
            return count
        action(item)
        count += 1
