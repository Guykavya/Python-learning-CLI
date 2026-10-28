from itertools import chain, islice


def first_valid(sources, n):
    readings = chain(*sources)
    valid = (r for r in readings if r is not None and 0 <= r <= 50)
    return list(islice(valid, n))
