def make_counter(start=0, step=1):
    """Return a function that adds step to a private count and returns it."""
    count = start

    def counter():
        nonlocal count
        count += step
        return count

    return counter
