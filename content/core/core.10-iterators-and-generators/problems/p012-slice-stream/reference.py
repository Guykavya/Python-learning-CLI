from itertools import islice


def slice_stream(iterable, start, stop):
    return list(islice(iterable, start, stop))
