def round_robin(*iterables):
    alive = [iter(x) for x in iterables]
    while alive:
        still_alive = []
        for it in alive:
            try:
                value = next(it)
            except StopIteration:
                continue
            still_alive.append(it)
            yield value
        alive = still_alive
